from typing import List, Optional, Union
from fastapi import APIRouter, HTTPException, status, Response, Depends, Query
from sqlalchemy.orm import Session
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
# WEEK 4, 5, 6: ApiUserController (/api/users)
# Manages users, nested job postings (/api/users/:id/jobs),
# and eager-loaded include queries (/api/users/:id?include=jobs).
# ===================================================================

router = APIRouter(
    prefix="/api/users",
    tags=["API Users & Nested Routes (ApiUserController)"]
)


# --- 1. GET /api/users (List all users) ---
@router.get("", response_model=List[User], summary="[ApiUserController] List users ordered by ID")
async def get_api_users(
    search: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Returns all users ordered by ID from database with optional search and department filters.
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
    db: Session = Depends(get_db)
):
    """
    [Week 6: Include] Fetches a single user by ID.
    If ?include=jobs is specified, executes a LEFT JOIN and returns user with their jobs list.
    """
    include_jobs = (include == "jobs")
    user = user_model.get_by_id(user_id, include_jobs=include_jobs, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# --- 3. POST /api/users (Create user) ---
@router.post("", response_model=User, status_code=status.HTTP_201_CREATED, summary="[ApiUserController] Create a user in database")
async def create_api_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Creates a new user. Returns 400 Bad Request if explicit ID already exists."""
    try:
        return user_model.create(user_in, db=db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# --- 4. PUT /api/users/:id (Full Update) ---
@router.put("/{user_id}", response_model=User, summary="[ApiUserController] Replace a user in DB (Full Update)")
async def update_api_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    """Completely replaces user fields in database. Returns 404 Not Found if user doesn't exist."""
    updated_user = user_model.update(user_id, user_in, db=db)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user


# --- 5. PATCH /api/users/:id (Partial Update) ---
@router.patch("/{user_id}", response_model=User, summary="[ApiUserController] Partially update a user in DB")
async def patch_api_user(user_id: int, user_in: UserPatch, db: Session = Depends(get_db)):
    """Partially updates user fields in database."""
    patched_user = user_model.patch(user_id, user_in, db=db)
    if not patched_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return patched_user


# --- 6. DELETE /api/users/:id (Delete user with RESTRICT rule) ---
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="[ApiUserController] Delete a user from DB")
async def delete_api_user(user_id: int, db: Session = Depends(get_db)):
    """
    Deletes user by ID.
    Enforces RESTRICT deletion rule: returns 409 Conflict if user has active job postings.
    """
    try:
        success = user_model.delete(user_id, db=db)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as e:
        # RESTRICT deletion rule violation
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# ===================================================================
# WEEK 6: NESTED ROUTES — Whose posting? The URL says!
# ===================================================================

# --- 7. POST /api/users/:id/jobs (Create job posting for user) ---
@router.post(
    "/{user_id}/jobs",
    response_model=JobPostingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[Nested Route] Create job posting for user specified in URL"
)
async def create_user_job(
    user_id: int,
    job_in: JobPostingCreate,
    db: Session = Depends(get_db)
):
    """
    [Week 6 Nested Route] The URL specifies user_id (:id).
    The request body carries { "title": "...", "company": "..." } and NEVER contains user_id.
    - If user does not exist -> 404 User not found
    - If user exists -> 201 Created with job posting details
    """
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
    db: Session = Depends(get_db)
):
    """
    Returns all job postings posted by user (:id).
    Returns 404 Not Found if user does not exist.
    """
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
    db: Session = Depends(get_db)
):
    """
    Returns all job applications submitted by user (:id).
    Returns 404 Not Found if user does not exist.
    """
    if not user_model.exists_by_id(user_id, db=db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return application_model.get_by_user_id(user_id=user_id, db=db)
