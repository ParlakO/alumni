import os
from typing import Optional
from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user_optional
from app.database import get_db
from app.models import (
    JobPostingCreate,
    UserCreate,
    UserUpdate,
    application_model,
    job_model,
    user_model,
)

VIEWS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "views")
templates = Jinja2Templates(directory=VIEWS_DIR)

router = APIRouter(tags=["Web Views - Auth, User Pages & Admin Panel"])


def _render(request: Request, template: str, context: dict, status_code: int = 200) -> HTMLResponse:
    base = {
        "error": None,
        "success": None,
        "form": {},
        "current_user": get_current_user_optional(request),
    }
    base.update(context)
    return templates.TemplateResponse(request, template, base, status_code=status_code)


def _redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


# ===================================================================
# 1. REGISTER & LOGIN & LOGOUT (Items #2 & #3)
# ===================================================================

@router.get("/register", response_class=HTMLResponse, include_in_schema=False)
async def register_page(request: Request):
    user = get_current_user_optional(request)
    if user and user.get("role") != "admin":
        return _redirect("/me")
    return _render(request, "auth/register.html", {"title": "Kayıt Ol (Register)"})


@router.post("/register", response_class=HTMLResponse, include_in_schema=False)
async def register_submit(
    request: Request,
    name: str = Form(""),
    email: str = Form(""),
    department: str = Form(""),
    password: str = Form(""),
    password_confirm: str = Form(""),
    db: Session = Depends(get_db),
):
    current = get_current_user_optional(request)
    if current and current.get("role") != "admin":
        return _redirect("/me")

    form = {"name": name, "email": email, "department": department}
    if len(password) < 6:
        return _render(
            request,
            "auth/register.html",
            {"title": "Kayıt Ol (Register)", "error": "Parola en az 6 karakter olmalıdır.", "form": form},
            status.HTTP_400_BAD_REQUEST,
        )
    if password != password_confirm:
        return _render(
            request,
            "auth/register.html",
            {"title": "Kayıt Ol (Register)", "error": "Parolalar birbiriyle eşleşmiyor.", "form": form},
            status.HTTP_400_BAD_REQUEST,
        )

    try:
        new_user = user_model.create(
            UserCreate(
                name=name,
                email=email,
                department=department,
                password=password,
                role="graduate",
            ),
            db=db,
        )
    except (ValidationError, ValueError) as e:
        return _render(
            request,
            "auth/register.html",
            {"title": "Kayıt Ol (Register)", "error": str(e), "form": form},
            status.HTTP_400_BAD_REQUEST,
        )

    token = create_access_token(new_user)
    resp = _redirect("/me?welcome=1")
    resp.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24,
    )
    return resp


@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_page(request: Request, next: Optional[str] = None, logged_out: Optional[int] = None):
    user = get_current_user_optional(request)
    if user:
        return _redirect("/admin" if user.get("role") == "admin" else "/me")
    success = "Oturumunuz güvenli bir şekilde kapatıldı." if logged_out else None
    return _render(
        request,
        "auth/login.html",
        {"title": "Giriş Yap (Login)", "next_url": next or "", "success": success},
    )


@router.post("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_submit(
    request: Request,
    email: str = Form(""),
    password: str = Form(""),
    next_url: str = Form(""),
    db: Session = Depends(get_db),
):
    user = user_model.authenticate(email, password, db=db)
    if not user:
        return _render(
            request,
            "auth/login.html",
            {
                "title": "Giriş Yap (Login)",
                "error": "invalid email or password",
                "form": {"email": email},
                "next_url": next_url,
            },
            status.HTTP_401_UNAUTHORIZED,
        )

    token = create_access_token(user)
    target = next_url if (next_url and next_url.startswith("/")) else ("/admin" if user["role"] == "admin" else "/me")
    resp = _redirect(target)
    resp.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24,
    )
    return resp


@router.get("/logout", include_in_schema=False)
@router.post("/logout", include_in_schema=False)
async def logout_view():
    resp = _redirect("/login?logged_out=1")
    resp.delete_cookie("access_token")
    return resp


# ===================================================================
# 2. USER-SPECIFIC PAGES: /me, /my-jobs, /my-applications (Item #7)
# ===================================================================

@router.get("/me", response_class=HTMLResponse, include_in_schema=False)
async def my_profile_page(
    request: Request,
    welcome: Optional[int] = None,
    updated: Optional[int] = None,
    db: Session = Depends(get_db),
):
    user = get_current_user_optional(request)
    if not user:
        return _redirect("/login?next=/me")

    my_jobs = job_model.get_by_user_id(user["id"], db=db)
    my_apps = application_model.get_by_user_id(user["id"], db=db)
    success = None
    if welcome:
        success = f"Hoş geldiniz, {user['name']}! Hesabınız oluşturuldu ve oturumunuz açıldı."
    elif updated:
        success = "Profil bilgileriniz başarıyla güncellendi."

    return _render(
        request,
        "user/profile.html",
        {
            "title": "Profilim (/me)",
            "user": user,
            "jobs_count": len(my_jobs),
            "apps_count": len(my_apps),
            "success": success,
        },
    )


@router.post("/me", response_class=HTMLResponse, include_in_schema=False)
async def update_my_profile(
    request: Request,
    name: str = Form(""),
    email: str = Form(""),
    department: str = Form(""),
    password: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_user_optional(request)
    if not user:
        return _redirect("/login?next=/me")

    try:
        pw = password.strip() if password and password.strip() else None
        user_model.update(
            user["id"],
            UserUpdate(name=name, email=email, department=department, password=pw),
            allow_role_change=False,
            db=db,
        )
    except (ValidationError, ValueError) as e:
        my_jobs = job_model.get_by_user_id(user["id"], db=db)
        my_apps = application_model.get_by_user_id(user["id"], db=db)
        return _render(
            request,
            "user/profile.html",
            {
                "title": "Profilim (/me)",
                "user": {**user, "name": name, "email": email, "department": department},
                "jobs_count": len(my_jobs),
                "apps_count": len(my_apps),
                "error": str(e),
            },
            status.HTTP_400_BAD_REQUEST,
        )
    return _redirect("/me?updated=1")


@router.get("/my-jobs", response_class=HTMLResponse, include_in_schema=False)
async def my_jobs_page(
    request: Request,
    created: Optional[int] = None,
    deleted: Optional[int] = None,
    db: Session = Depends(get_db),
):
    user = get_current_user_optional(request)
    if not user:
        return _redirect("/login?next=/my-jobs")

    jobs = job_model.get_by_user_id(user["id"], db=db)
    jobs_with_applicants = []
    for j in jobs:
        applicants = application_model.get_applicants_by_job_id(j["id"], db=db)
        jobs_with_applicants.append({**j, "applicants": applicants})

    success = None
    if created:
        success = "Yeni iş ilanınız başarıyla yayınlandı."
    elif deleted:
        success = "İş ilanınız silindi."

    return _render(
        request,
        "user/my_jobs.html",
        {
            "title": "İş İlanlarım (/my-jobs)",
            "jobs": jobs_with_applicants,
            "success": success,
        },
    )


@router.post("/my-jobs", response_class=HTMLResponse, include_in_schema=False)
async def create_my_job(
    request: Request,
    title: str = Form(""),
    company: str = Form(""),
    city: str = Form(""),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_user_optional(request)
    if not user:
        return _redirect("/login?next=/my-jobs")

    try:
        job_model.create(
            user_id=user["id"],
            job_data=JobPostingCreate(
                title=title.strip(),
                company=company.strip(),
                city=city.strip() or None,
                description=description.strip() or None,
            ),
            db=db,
        )
    except (ValidationError, ValueError) as e:
        jobs = job_model.get_by_user_id(user["id"], db=db)
        jobs_with_applicants = [{**j, "applicants": application_model.get_applicants_by_job_id(j["id"], db=db)} for j in jobs]
        return _render(
            request,
            "user/my_jobs.html",
            {
                "title": "İş İlanlarım (/my-jobs)",
                "jobs": jobs_with_applicants,
                "error": str(e),
                "form": {"title": title, "company": company, "city": city, "description": description},
            },
            status.HTTP_400_BAD_REQUEST,
        )
    return _redirect("/my-jobs?created=1")


@router.post("/my-jobs/{job_id}/delete", include_in_schema=False)
async def delete_my_job(request: Request, job_id: int, db: Session = Depends(get_db)):
    user = get_current_user_optional(request)
    if not user:
        return _redirect("/login?next=/my-jobs")
    job = job_model.get_by_id(job_id, db=db)
    if job and (job["user_id"] == user["id"] or user["role"] == "admin"):
        job_model.delete(job_id, db=db)
    return _redirect("/my-jobs?deleted=1")


@router.get("/my-applications", response_class=HTMLResponse, include_in_schema=False)
async def my_applications_page(
    request: Request,
    withdrawn: Optional[int] = None,
    db: Session = Depends(get_db),
):
    user = get_current_user_optional(request)
    if not user:
        return _redirect("/login?next=/my-applications")

    apps = application_model.get_by_user_id(user["id"], db=db)
    all_jobs = {j["id"]: j for j in job_model.get_all(db=db)}
    enriched = [
        {**a, "job": all_jobs.get(a["job_posting_id"])}
        for a in apps
    ]
    success = "Başvurunuz geri çekildi." if withdrawn else None
    return _render(
        request,
        "user/my_applications.html",
        {
            "title": "Başvurularım (/my-applications)",
            "applications": enriched,
            "success": success,
        },
    )


@router.post("/my-applications/{app_id}/delete", include_in_schema=False)
async def withdraw_my_application(request: Request, app_id: int, db: Session = Depends(get_db)):
    user = get_current_user_optional(request)
    if not user:
        return _redirect("/login?next=/my-applications")
    app_rec = application_model.get_by_id(app_id, db=db)
    if app_rec and (app_rec["user_id"] == user["id"] or user["role"] == "admin"):
        application_model.delete(app_id, db=db)
    return _redirect("/my-applications?withdrawn=1")


# ===================================================================
# 3. ADMIN PANEL (Item #5)
# ===================================================================

@router.get("/admin", response_class=HTMLResponse, include_in_schema=False)
async def admin_dashboard(
    request: Request,
    msg: Optional[str] = None,
    err: Optional[str] = None,
    db: Session = Depends(get_db),
):
    user = get_current_user_optional(request)
    if not user:
        return _redirect("/login?next=/admin")
    if user.get("role") != "admin":
        return _render(
            request,
            "404.html",
            {
                "title": "403 - Erişim Reddedildi",
                "path": "/admin",
                "reason": "403 Forbidden: Bu yönetim paneline yalnızca 'admin' rolüne sahip kullanıcılar erişebilir.",
            },
            status.HTTP_403_FORBIDDEN,
        )

    users = user_model.get_all(order_by_id=True, db=db)
    jobs = job_model.get_all(db=db)
    apps = application_model.get_all(db=db)
    user_map = {u["id"]: u for u in users}
    job_map = {j["id"]: j for j in jobs}

    stats = {
        "total_users": len(users),
        "admin_count": sum(1 for u in users if u.get("role") == "admin"),
        "graduate_count": sum(1 for u in users if u.get("role") != "admin"),
        "total_jobs": len(jobs),
        "total_applications": len(apps),
    }

    return _render(
        request,
        "admin/dashboard.html",
        {
            "title": "Admin Yönetim Paneli (/admin)",
            "stats": stats,
            "users": users,
            "jobs": jobs,
            "applications": apps,
            "user_map": user_map,
            "job_map": job_map,
            "success": msg,
            "error": err,
        },
    )


@router.post("/admin/users/{user_id}/role", include_in_schema=False)
async def admin_change_user_role(
    request: Request,
    user_id: int,
    role: str = Form("graduate"),
    db: Session = Depends(get_db),
):
    user = get_current_user_optional(request)
    if not user:
        return _redirect("/login?next=/admin")
    if user.get("role") != "admin":
        return _redirect("/me")

    try:
        user_model.update_role(user_id, role, db=db)
        return _redirect(f"/admin?msg=Kullanıcı+%23{user_id}+rolü+'{role}'+olarak+güncellendi.")
    except ValueError as e:
        return _redirect(f"/admin?err={str(e)}")


@router.post("/admin/users/{user_id}/delete", include_in_schema=False)
async def admin_delete_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = get_current_user_optional(request)
    if not user or user.get("role") != "admin":
        return _redirect("/login?next=/admin")

    if user_id == user["id"]:
        return _redirect("/admin?err=Kendi+admin+hesabınızı+silemezsiniz.")

    try:
        user_model.delete(user_id, db=db)
        return _redirect(f"/admin?msg=Kullanıcı+%23{user_id}+silindi.")
    except ValueError as e:
        return _redirect(f"/admin?err={str(e)}")


@router.post("/admin/jobs/{job_id}/delete", include_in_schema=False)
async def admin_delete_job(request: Request, job_id: int, db: Session = Depends(get_db)):
    user = get_current_user_optional(request)
    if not user or user.get("role") != "admin":
        return _redirect("/login?next=/admin")
    job_model.delete(job_id, db=db)
    return _redirect(f"/admin?msg=İlan+%23{job_id}+silindi.")


@router.post("/admin/applications/{app_id}/status", include_in_schema=False)
async def admin_update_app_status(
    request: Request,
    app_id: int,
    status_val: str = Form(..., alias="status"),
    db: Session = Depends(get_db),
):
    user = get_current_user_optional(request)
    if not user or user.get("role") != "admin":
        return _redirect("/login?next=/admin")
    application_model.update_status(app_id, status_val, db=db)
    return _redirect(f"/admin?msg=Başvuru+%23{app_id}+durumu+'{status_val}'+yapıldı.")
