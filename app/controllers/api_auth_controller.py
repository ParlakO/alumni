from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.auth import (
    create_access_token,
    get_current_user_optional,
    require_admin,
    require_auth,
)
from app.database import get_db
from app.models import (
    AuthMeResponse,
    AuthTokenResponse,
    User,
    UserCreate,
    UserLogin,
    UserRegister,
    UserRoleUpdate,
    application_model,
    job_model,
    user_model,
)

# ===================================================================
# Authentication & Admin API Controller (/api/register, /api/login,
# /api/logout, /api/me, /api/admin/*)
# ===================================================================

router = APIRouter(
    prefix="/api",
    tags=["Authentication & Admin (ApiAuthController)"]
)


@router.post(
    "/register",
    response_model=AuthTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new graduate account"
)
async def api_register(
    payload: UserRegister,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Registers a new user with role='graduate' and bcrypt-hashed password.
    Permission matrix: guest=yes, graduate=no (403), admin=yes.
    """
    current_user = get_current_user_optional(request)
    if current_user and current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed")

    try:
        created_user = user_model.create(
            UserCreate(
                name=payload.name,
                email=payload.email,
                department=payload.department,
                password=payload.password,
                role="graduate",
            ),
            db=db,
        )
    except ValueError as e:
        code = status.HTTP_409_CONFLICT if "Email" in str(e) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(e))

    token = create_access_token(created_user)
    if not current_user:
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            samesite="lax",
            max_age=60 * 60 * 24,
        )
    return {"token": token, "user": created_user}


@router.post(
    "/login",
    response_model=AuthTokenResponse,
    summary="Log in with email and password to receive a JWT"
)
async def api_login(
    payload: UserLogin,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Verifies email + password against stored bcrypt hash.
    Returns 401 {"error": "invalid email or password"} for both unknown email and wrong password.
    """
    user = user_model.authenticate(payload.email, payload.password, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid email or password",
        )

    token = create_access_token(user)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24,
    )
    return {"token": token, "user": user}


@router.post("/logout", summary="Log out and clear session cookie")
async def api_logout(response: Response):
    """Clears the access_token cookie."""
    response.delete_cookie("access_token")
    return {"message": "logged out"}


@router.get("/me", response_model=AuthMeResponse, summary="Get current authenticated user")
async def api_me(current_user: dict = Depends(require_auth)):
    """Returns { id, name, email, department, role } for the currently logged-in user."""
    return current_user


@router.get("/admin/stats", summary="[Admin] Get system overview statistics")
async def api_admin_stats(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Returns counts of users, admins, graduates, job postings, and applications."""
    users = user_model.get_all(db=db)
    jobs = job_model.get_all(db=db)
    apps = application_model.get_all(db=db)
    return {
        "total_users": len(users),
        "admin_count": sum(1 for u in users if u.get("role") == "admin"),
        "graduate_count": sum(1 for u in users if u.get("role") != "admin"),
        "total_jobs": len(jobs),
        "total_applications": len(apps),
    }


@router.patch(
    "/admin/users/{user_id}/role",
    response_model=User,
    summary="[Admin] Assign or change a user's role"
)
async def api_admin_update_role(
    user_id: int,
    role_in: UserRoleUpdate,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Changes a user's role between 'graduate' and 'admin'."""
    try:
        updated = user_model.update_role(user_id, role_in.role, db=db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated
