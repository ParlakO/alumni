from typing import List, Optional, Union
from fastapi import APIRouter, HTTPException, Request, status, Response, Depends, Query
from sqlalchemy.orm import Session
from app.auth import get_current_user_optional, require_auth, require_admin
from app.database import get_db
from app.models import (
    User,
    UserCreate,
    UserUpdate,
    UserPatch,
    UserWithJobs,
    JobPostingCreate,
    JobPostingResponse,
    ApplicationResponse,
    user_model,
    job_model,
    application_model
)

# ===================================================================
# WEEK 4, 5, 6, 7: ApiUserController (/api/users)
# Manages users, nested job postings (/api/users/:id/jobs),
# and eager-loaded include queries (/api/users/:id?include=jobs)
# with Role-Based & Ownership Authorization.
# ===================================================================

router = APIRouter(
    prefix="/api/users",
    tags=["API Users & Nested Routes (ApiUserController)"]
)


# --- 1. GET /api/users (List all users: guest=no, graduate=yes, admin=yes) ---
@router.get("", response_model=List[User], summary="[ApiUserController] List users ordered by ID")
async def get_api_users(
    search: Optional[str] = None,
    department: Optional[str] = None,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Returns all users ordered by ID (never returns password_hash).
    Requires authentication (graduate or admin).
    """
    return user_model.get_all(search=search, department=department, order_by_id=True, db=db)


# --- 2. GET /api/users/:id (Include: One answer, two tables) ---
@router.get(
    "/{user_id}",
    response_model=Union[UserWithJobs, User],
    summary="[ApiUserController] Get one user by ID (supports ?include=jobs)"
)
async def get_api_user_by_id(
    user_id: int,
    include: Optional[str] = Query(None, description="Set to 'jobs' to include user's job postings via LEFT JOIN"),
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Fetches a single user by ID. Requires authentication (graduate or admin).
    """
    include_jobs = (include == "jobs")
    user = user_model.get_by_id(user_id, include_jobs=include_jobs, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# --- 3. POST /api/users (Sign up / Create user: guest=yes, graduate=no, admin=yes) ---
@router.post("", response_model=User, status_code=status.HTTP_201_CREATED, summary="[ApiUserController] Create a user in database")
async def create_api_user(
    user_in: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Creates a new user.
    Permission matrix: guest=yes (always role='graduate'), graduate=no (403), admin=yes.
    """
    current_user = get_current_user_optional(request)
    if current_user and current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed")

    # Guests cannot self-assign admin role
    if not current_user or current_user.get("role") != "admin":
        user_in = user_in.model_copy(update={"role": "graduate"})

    try:
        return user_model.create(user_in, db=db)
    except ValueError as e:
        code = status.HTTP_409_CONFLICT if "Email" in str(e) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=str(e))


# --- 4. PUT /api/users/:id (Change profile: guest=no, graduate=own, admin=yes) ---
@router.put("/{user_id}", response_model=User, summary="[ApiUserController] Replace a user in DB (Full Update)")
async def update_api_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Completely replaces user fields in database.
    Graduate can only update their own profile; Admin can update any profile.
    """
    is_admin = current_user.get("role") == "admin"
    if not is_admin and current_user["id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed")

    try:
        updated_user = user_model.update(user_id, user_in, allow_role_change=is_admin, db=db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user


# --- 5. PATCH /api/users/:id (Partial Update: guest=no, graduate=own, admin=yes) ---
@router.patch("/{user_id}", response_model=User, summary="[ApiUserController] Partially update a user in DB")
async def patch_api_user(
    user_id: int,
    user_in: UserPatch,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Partially updates user fields in database.
    Graduate can only update their own profile; Admin can update any profile.
    """
    is_admin = current_user.get("role") == "admin"
    if not is_admin and current_user["id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed")

    try:
        patched_user = user_model.patch(user_id, user_in, allow_role_change=is_admin, db=db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not patched_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return patched_user


# --- 6. DELETE /api/users/:id (Delete user: guest=no, graduate=no, admin=yes) ---
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="[ApiUserController] Delete a user from DB")
async def delete_api_user(
    user_id: int,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Deletes user by ID (Admin only).
    Enforces RESTRICT deletion rule: returns 409 Conflict if user has active job postings.
    """
    try:
        success = user_model.delete(user_id, db=db)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# ===================================================================
# NESTED ROUTES — Whose posting? The URL says (and Auth verifies!)
# ===================================================================

# --- 7. POST /api/users/:id/jobs (Post a job: guest=no, graduate=own, admin=yes) ---
@router.post(
    "/{user_id}/jobs",
    response_model=JobPostingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[Nested Route] Create job posting for user specified in URL"
)
async def create_user_job(
    user_id: int,
    job_in: JobPostingCreate,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Creates a job posting for user (:id).
    Graduate A posting for user B -> 403 {"error": "not allowed"}.
    Admin may post for any user.
    """
    if current_user.get("role") != "admin" and current_user["id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed")

    try:
        return job_model.create(user_id=user_id, job_data=job_in, db=db)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- 8. GET /api/users/:id/jobs (List jobs belonging to user) ---
@router.get(
    "/{user_id}/jobs",
    response_model=List[JobPostingResponse],
    summary="[Nested Route] List all job postings belonging to user"
)
async def get_user_jobs(
    user_id: int,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Returns all job postings posted by user (:id)."""
    if not user_model.exists_by_id(user_id, db=db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return job_model.get_by_user_id(user_id=user_id, db=db)


# --- 9. GET /api/users/:id/applications (List applications made by user) ---
@router.get(
    "/{user_id}/applications",
    response_model=List[ApplicationResponse],
    summary="[Nested Route] List all job applications submitted by user"
)
async def get_user_applications(
    user_id: int,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Returns all job applications submitted by user (:id). Graduate may only view own applications."""
    if current_user.get("role") != "admin" and current_user["id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed")
    if not user_model.exists_by_id(user_id, db=db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return application_model.get_by_user_id(user_id=user_id, db=db)
