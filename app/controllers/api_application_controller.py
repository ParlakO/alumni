from typing import List
from fastapi import APIRouter, HTTPException, status, Response, Depends
from sqlalchemy.orm import Session
from app.auth import require_auth
from app.database import get_db
from app.models import (
    ApplicationResponse,
    ApplicationStatusUpdate,
    application_model,
    job_model,
)

# ===================================================================
# ApiApplicationController (/api/applications)
# Direct CRUD operations for applications table with Role & Ownership checks.
# ===================================================================

router = APIRouter(
    prefix="/api/applications",
    tags=["API Applications (ApiApplicationController)"]
)


# --- 1. GET /api/applications (Admin: all, Graduate: own + own jobs) ---
@router.get("", response_model=List[ApplicationResponse], summary="[Direct Route] List applications")
async def get_all_applications(
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Admin receives all applications.
    Graduate receives their own submitted applications plus applications to jobs they posted.
    """
    all_apps = application_model.get_all(db=db)
    if current_user.get("role") == "admin":
        return all_apps

    my_job_ids = {j["id"] for j in job_model.get_by_user_id(current_user["id"], db=db)}
    return [
        a for a in all_apps
        if a["user_id"] == current_user["id"] or a["job_posting_id"] in my_job_ids
    ]


# --- 2. GET /api/applications/:id ---
@router.get("/{application_id}", response_model=ApplicationResponse, summary="[Direct Route] Get application by ID")
async def get_application_by_id(
    application_id: int,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Returns a single application by ID (admin, applicant, or job owner)."""
    app_record = application_model.get_by_id(application_id, db=db)
    if not app_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    if current_user.get("role") != "admin":
        job = job_model.get_by_id(app_record["job_posting_id"], db=db)
        is_owner = job is not None and job["user_id"] == current_user["id"]
        if app_record["user_id"] != current_user["id"] and not is_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed")
    return app_record


# --- 3. PATCH /api/applications/:id (Admin or Job Owner) ---
@router.patch("/{application_id}", response_model=ApplicationResponse, summary="[Direct Route] Update application status")
async def update_application_status(
    application_id: int,
    status_in: ApplicationStatusUpdate,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Updates the status of an application (admin or job posting owner)."""
    app_record = application_model.get_by_id(application_id, db=db)
    if not app_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    if current_user.get("role") != "admin":
        job = job_model.get_by_id(app_record["job_posting_id"], db=db)
        if not job or job["user_id"] != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed")

    updated_app = application_model.update_status(application_id, status_in.status, db=db)
    return updated_app


# --- 4. DELETE /api/applications/:id (Admin or Applicant) ---
@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT, summary="[Direct Route] Withdraw application")
async def delete_application(
    application_id: int,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Withdraws or deletes an application by ID (admin or applicant only)."""
    app_record = application_model.get_by_id(application_id, db=db)
    if not app_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    if current_user.get("role") != "admin" and app_record["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed")

    application_model.delete(application_id, db=db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
