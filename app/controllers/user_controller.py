import os
from typing import Optional
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.models import UserCreate, UserUpdate, UserPatch, user_model

# ===================================================================
# WEEK 4: UserController (/users) - Full CRUD with the VIEW LAYER
#
#   GET    /users             -> index   (list + create form)     users/index.html
#   POST   /users             -> create  (form submit)            -> 303 /users
#   GET    /users/{id}        -> show    (one user)               users/show.html
#   GET    /users/{id}/edit   -> edit    (edit form)              users/edit.html
#   PUT    /users/{id}        -> replace (all fields required)    -> 303 /users/{id}
#   PATCH  /users/{id}        -> partial (empty fields ignored)   -> 303 /users/{id}
#   DELETE /users/{id}        -> delete                           -> 303 /users
#
# HTML forms can't send PUT/PATCH/DELETE, so the views submit
# POST /users/{id}?_method=PUT|PATCH|DELETE (see MethodOverrideMiddleware in main.py).
# Data always goes through the Model (UserModel), output through the View (Jinja2).
# ===================================================================

VIEWS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "views")
templates = Jinja2Templates(directory=VIEWS_DIR)

router = APIRouter(
    prefix="/users",
    tags=["Users (UserController)"]
)


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def _render(request: Request, template: str, context: dict, status_code: int = 200) -> HTMLResponse:
    base = {"error": None, "success": None, "form": {}}
    base.update(context)
    return templates.TemplateResponse(request, template, base, status_code=status_code)


def _render_index(request: Request, status_code: int = 200, **context) -> HTMLResponse:
    context.setdefault("title", "Mezun Listesi")
    context["users"] = user_model.get_all(order_by_id=True)
    return _render(request, "users/index.html", context, status_code)


def _render_not_found(request: Request, user_id: int) -> HTMLResponse:
    return _render(request, "users/not_found.html",
                   {"title": "Mezun Bulunamadı", "user_id": user_id}, status.HTTP_404_NOT_FOUND)


def _validation_message(e: ValidationError) -> str:
    first = e.errors()[0]
    field = first["loc"][-1] if first.get("loc") else "form"
    return f"Geçersiz alan '{field}': {first['msg']}"


def _redirect(url: str) -> RedirectResponse:
    # 303 See Other: the browser follows with GET (Post/Redirect/Get pattern)
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


# -------------------------------------------------------------------
# READ (list) - GET /users
# -------------------------------------------------------------------
@router.get("", response_class=HTMLResponse, summary="[UserController] List users (view)")
async def list_users_view(request: Request, created: Optional[int] = None, deleted: Optional[int] = None):
    """[Week 4 - View] Renders users/index.html with all users ordered by ID."""
    success = None
    if created is not None:
        success = f"Mezun #{created} başarıyla oluşturuldu."
    elif deleted is not None:
        success = f"Mezun #{deleted} silindi."
    return _render_index(request, success=success)


# -------------------------------------------------------------------
# CREATE - POST /users
# -------------------------------------------------------------------
@router.post("", response_class=HTMLResponse, summary="[UserController] Create user (form)")
async def create_user_view(
    request: Request,
    name: str = Form(""),
    email: str = Form(""),
    department: str = Form(""),
    id: Optional[str] = Form(None),
):
    """[Week 4 - View] Creates a user from the form. Success -> 303 /users, error -> 400 + view."""
    form = {"id": id, "name": name, "email": email, "department": department}
    try:
        user_id = int(id) if id not in (None, "") else None
        new_user = user_model.create(UserCreate(id=user_id, name=name, email=email, department=department))
    except ValidationError as e:
        return _render_index(request, status.HTTP_400_BAD_REQUEST, error=_validation_message(e), form=form)
    except ValueError as e:
        # int() conversion error or "User ID already exists"
        return _render_index(request, status.HTTP_400_BAD_REQUEST, error=str(e), form=form)
    return _redirect(f"/users?created={new_user['id']}")


# -------------------------------------------------------------------
# EDIT FORM - GET /users/{id}/edit   (declared before /{user_id})
# -------------------------------------------------------------------
@router.get("/{user_id}/edit", response_class=HTMLResponse, summary="[UserController] Edit form (view)")
async def edit_user_view(request: Request, user_id: int):
    """[Week 4 - View] Renders users/edit.html pre-filled with the user's data."""
    user = user_model.get_by_id(user_id)
    if not user:
        return _render_not_found(request, user_id)
    return _render(request, "users/edit.html",
                   {"title": f"Mezun Düzenle #{user_id}", "user_id": user_id, "form": user})


# -------------------------------------------------------------------
# READ (one) - GET /users/{id}
# -------------------------------------------------------------------
@router.get("/{user_id}", response_class=HTMLResponse, summary="[UserController] Show user (view)")
async def show_user_view(request: Request, user_id: int, updated: Optional[str] = None):
    """[Week 4 - View] Renders users/show.html for a single user."""
    user = user_model.get_by_id(user_id)
    if not user:
        return _render_not_found(request, user_id)
    success = f"Mezun #{user_id} güncellendi ({updated})." if updated else None
    return _render(request, "users/show.html",
                   {"title": f"Mezun #{user_id}", "user": user, "success": success})


# -------------------------------------------------------------------
# UPDATE (replace) - PUT /users/{id}
# -------------------------------------------------------------------
@router.put("/{user_id}", response_class=HTMLResponse, summary="[UserController] Replace user (form, PUT)")
async def update_user_view(
    request: Request,
    user_id: int,
    name: str = Form(""),
    email: str = Form(""),
    department: str = Form(""),
):
    """[Week 4 - View] Full replacement; all fields required. Success -> 303 /users/{id}."""
    form = {"name": name, "email": email, "department": department}
    if not user_model.exists_by_id(user_id):
        return _render_not_found(request, user_id)
    try:
        user_model.update(user_id, UserUpdate(name=name, email=email, department=department))
    except ValidationError as e:
        return _render(request, "users/edit.html",
                       {"title": f"Mezun Düzenle #{user_id}", "user_id": user_id, "form": form,
                        "error": "PUT tüm alanları ister. " + _validation_message(e)},
                       status.HTTP_400_BAD_REQUEST)
    return _redirect(f"/users/{user_id}?updated=PUT")


# -------------------------------------------------------------------
# UPDATE (partial) - PATCH /users/{id}
# -------------------------------------------------------------------
@router.patch("/{user_id}", response_class=HTMLResponse, summary="[UserController] Partially update user (form, PATCH)")
async def patch_user_view(
    request: Request,
    user_id: int,
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
):
    """[Week 4 - View] Partial update; empty fields are ignored. Success -> 303 /users/{id}."""
    form = {"name": name, "email": email, "department": department}
    if not user_model.exists_by_id(user_id):
        return _render_not_found(request, user_id)
    try:
        changes = UserPatch(**{k: v for k, v in form.items() if v not in (None, "")})
        user_model.patch(user_id, changes)
    except ValidationError as e:
        return _render(request, "users/edit.html",
                       {"title": f"Mezun Düzenle #{user_id}", "user_id": user_id, "form": form,
                        "error": _validation_message(e)},
                       status.HTTP_400_BAD_REQUEST)
    return _redirect(f"/users/{user_id}?updated=PATCH")


# -------------------------------------------------------------------
# DELETE - DELETE /users/{id}
# -------------------------------------------------------------------
@router.delete("/{user_id}", response_class=HTMLResponse, summary="[UserController] Delete user (form, DELETE)")
async def delete_user_view(request: Request, user_id: int):
    """[Week 4 - View] Deletes the user. Success -> 303 /users, missing -> 404 view."""
    if not user_model.delete(user_id):
        return _render_not_found(request, user_id)
    return _redirect(f"/users?deleted={user_id}")
