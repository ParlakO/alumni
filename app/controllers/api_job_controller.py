from typing import List
from fastapi import APIRouter, HTTPException, status, Response, Depends
from sqlalchemy.orm import Session
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
# WEEK 6: ApiJobController (/api/jobs)
# Direct routes for job postings and applications.
# Handles Many-to-Many applications and duplicate 409 Conflict enforcement.
# ===================================================================

router = APIRouter(
    prefix="/api/jobs",
    tags=["API Jobs & Applications (ApiJobController)"]
)


# --- 1. GET /api/jobs (Direct Route: List all job postings) ---
@router.get("", response_model=List[JobPostingResponse], summary="[Direct Route] List all job postings")
async def get_all_jobs(db: Session = Depends(get_db)):
    """[Direct Route] Returns all job postings in the system ordered by ID."""
    return job_model.get_all(db=db)


# --- 2. GET /api/jobs/:id (Direct Route: Get one job posting) ---
@router.get("/{job_id}", response_model=JobPostingResponse, summary="[Direct Route] Get job posting by ID")
async def get_job_by_id(job_id: int, db: Session = Depends(get_db)):
    """[Direct Route] Returns a single job posting by ID. Returns 404 if not found."""
    job = job_model.get_by_id(job_id, db=db)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found")
    return job


# --- 3. DELETE /api/jobs/:id (Direct Route: Delete a job posting) ---
@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT, summary="[Direct Route] Delete job posting")
async def delete_job(job_id: int, db: Session = Depends(get_db)):
    """[Direct Route] Deletes a job posting and its cascaded applications."""
    deleted = job_model.delete(job_id, db=db)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ===================================================================
# APPLICATIONS (Many-to-Many via Join Table)
# ===================================================================

# --- 4. POST /api/jobs/:id/applications (Apply to a job posting) ---
@router.post(
    "/{job_id}/applications",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[Applications Route] Apply to a job posting (enforces UNIQUE & 409 Conflict)"
)
async def apply_to_job(
    job_id: int,
    application_in: ApplicationCreate,
    db: Session = Depends(get_db)
):
    """
    [Week 6: Applications Route]
    - Request body: { "userId": 1 }
    - If job or user does not exist -> 404 Not Found
    - If user has already applied -> 409 Conflict (UNIQUE constraint)
    - If successful -> 201 Created
    """
    try:
        return application_model.apply(
            job_posting_id=job_id,
            user_id=application_in.userId,
            db=db
        )
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        # Enforces UNIQUE (user_id, job_posting_id) -> twice: 409 Conflict
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


# --- 5. GET /api/jobs/:id/applications (List applicants for a job) ---
@router.get(
    "/{job_id}/applications",
    response_model=List[ApplicationResponse],
    summary="[Applications Route] List all applications for a job posting"
)
async def get_job_applications(
    job_id: int,
    db: Session = Depends(get_db)
):
    """Returns all applications submitted for job posting (:id)."""
    job = job_model.get_by_id(job_id, db=db)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found")
    return application_model.get_by_job_id(job_posting_id=job_id, db=db)


# --- 6. GET /api/jobs/:id/applicants (List applicant users for a job) ---
@router.get(
    "/{job_id}/applicants",
    response_model=List[User],
    summary="[Applications Route] List all applicant users who applied for a job"
)
async def get_job_applicants(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Returns the list of User objects (applicants) who applied to job posting (:id).
    (Week 06: 'the two lists of applicants and applications')
    """
    try:
        return application_model.get_applicants_by_job_id(job_posting_id=job_id, db=db)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
