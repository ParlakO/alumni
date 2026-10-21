from typing import List
from fastapi import APIRouter, HTTPException, status, Response, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import (
    ApplicationResponse,
    ApplicationStatusUpdate,
    application_model
)

# ===================================================================
# WEEK 6: ApiApplicationController (/api/applications)
# Direct CRUD operations for applications table.
# Supports listing, viewing, updating status, and withdrawing applications.
# ===================================================================

router = APIRouter(
    prefix="/api/applications",
    tags=["API Applications (ApiApplicationController)"]
)


# --- 1. GET /api/applications (Direct Route: List all applications) ---
@router.get("", response_model=List[ApplicationResponse], summary="[Direct Route] List all applications")
async def get_all_applications(db: Session = Depends(get_db)):
    """Returns all applications in the system ordered by ID."""
    return application_model.get_all(db=db)


# --- 2. GET /api/applications/:id (Direct Route: Get one application) ---
@router.get("/{application_id}", response_model=ApplicationResponse, summary="[Direct Route] Get application by ID")
async def get_application_by_id(application_id: int, db: Session = Depends(get_db)):
    """Returns a single application by ID. Returns 404 if not found."""
    app_record = application_model.get_by_id(application_id, db=db)
    if not app_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return app_record


# --- 3. PATCH /api/applications/:id (Direct Route: Update status) ---
@router.patch("/{application_id}", response_model=ApplicationResponse, summary="[Direct Route] Update application status")
async def update_application_status(
    application_id: int,
    status_in: ApplicationStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Updates the status of an application (e.g., 'applied' -> 'interview' -> 'accepted' / 'rejected').
    """
    updated_app = application_model.update_status(application_id, status_in.status, db=db)
    if not updated_app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return updated_app


# --- 4. DELETE /api/applications/:id (Direct Route: Withdraw application) ---
@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT, summary="[Direct Route] Withdraw application")
async def delete_application(application_id: int, db: Session = Depends(get_db)):
    """Withdraws or deletes an application by ID."""
    success = application_model.delete(application_id, db=db)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
