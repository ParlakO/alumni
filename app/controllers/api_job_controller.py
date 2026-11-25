from typing import List, Optional
from fastapi import APIRouter, Body, HTTPException, status, Response, Depends
from sqlalchemy.orm import Session
from app.auth import require_auth
from app.database import get_db
from app.models import (
    User,
    JobPostingResponse,
    ApplicationCreate,
    ApplicationResponse,
    job_model,
    application_model
)

# ===================================================================
# ApiJobController (/api/jobs)
# Direct routes for job postings and applications with Role & Ownership checks.
# ===================================================================

router = APIRouter(
    prefix="/api/jobs",
    tags=["API Jobs & Applications (ApiJobController)"]
)


# --- 1. GET /api/jobs (Public: guest=yes, graduate=yes, admin=yes) ---
@router.get("", response_model=List[JobPostingResponse], summary="[Direct Route] List all job postings")
async def get_all_jobs(db: Session = Depends(get_db)):
    """[Public] Returns all job postings in the system ordered by ID."""
    return job_model.get_all(db=db)


# --- 2. GET /api/jobs/:id (Public: guest=yes, graduate=yes, admin=yes) ---
@router.get("/{job_id}", response_model=JobPostingResponse, summary="[Direct Route] Get job posting by ID")
async def get_job_by_id(job_id: int, db: Session = Depends(get_db)):
    """[Public] Returns a single job posting by ID. Returns 404 if not found."""
    job = job_model.get_by_id(job_id, db=db)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found")
    return job


# --- 3. DELETE /api/jobs/:id (Owner or Admin only) ---
@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT, summary="[Direct Route] Delete job posting")
async def delete_job(
    job_id: int,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Deletes a job posting (only owner or admin)."""
    job = job_model.get_by_id(job_id, db=db)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found")
    if current_user.get("role") != "admin" and job["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed")

    job_model.delete(job_id, db=db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ===================================================================
# APPLICATIONS (Many-to-Many via Join Table)
# ===================================================================

# --- 4. POST /api/jobs/:id/applications (guest=no, graduate=self, admin=no) ---
@router.post(
    "/{job_id}/applications",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[Applications Route] Apply to a job posting (graduate self only)"
)
async def apply_to_job(
    job_id: int,
    application_in: Optional[ApplicationCreate] = Body(default=None),
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Applies the logged-in graduate to job posting (:id).
    - Admin -> 403 not allowed (admins do not apply to jobs).
    - Any `userId` in the request body is IGNORED; the applicant is ALWAYS the logged-in user.
    - Duplicate application -> 409 Conflict.
    """
    if current_user.get("role") != "graduate":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed")

    try:
        return application_model.apply(
            job_posting_id=job_id,
            user_id=current_user["id"],
            db=db
        )
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# --- 5. GET /api/jobs/:id/applications (Authenticated) ---
@router.get(
    "/{job_id}/applications",
    response_model=List[ApplicationResponse],
    summary="[Applications Route] List all applications for a job posting"
)
async def get_job_applications(
    job_id: int,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Returns all applications submitted for job posting (:id)."""
    job = job_model.get_by_id(job_id, db=db)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found")
    return application_model.get_by_job_id(job_posting_id=job_id, db=db)


# --- 6. GET /api/jobs/:id/applicants (Authenticated) ---
@router.get(
    "/{job_id}/applicants",
    response_model=List[User],
    summary="[Applications Route] List all applicant users who applied for a job"
)
async def get_job_applicants(
    job_id: int,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Returns the list of User objects (applicants, without password_hash) who applied to job (:id)."""
    try:
        return application_model.get_applicants_by_job_id(job_posting_id=job_id, db=db)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
