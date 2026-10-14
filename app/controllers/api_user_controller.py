from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Response, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserCreate, UserUpdate, UserPatch, user_model

# ===================================================================
# WEEK 4 & 5: ApiUserController (/api/users)
# Dedicated controller with real-time Database Session connection (SQLAlchemy)
# ===================================================================

router = APIRouter(
    prefix="/api/users",
    tags=["API Users (ApiUserController)"]
)


# --- WEEK 2, 3, 5: GET /api/users (List users ordered by ID via DB) ---
@router.get("", response_model=List[User], summary="[ApiUserController] List users ordered by ID")
async def get_api_users(
    search: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    [Week 2 & 3 & 4 & 5] Returns all users ordered by ID from database.
    """
    return user_model.get_all(search=search, department=department, order_by_id=True, db=db)


# --- WEEK 2, 4, 5: GET /api/users/:id (Get one user from DB) ---
@router.get("/{user_id}", response_model=User, summary="[ApiUserController] Get one user by ID")
async def get_api_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """
    [Week 2 & 4 & 5] Fetches a single user by ID from database.
    """
    user = user_model.get_by_id(user_id, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# --- WEEK 3, 4, 5: POST /api/users (Create a persistent user in DB) ---
@router.post("", response_model=User, status_code=status.HTTP_201_CREATED, summary="[ApiUserController] Create a user in database")
async def create_api_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    [Week 3 & 4 & 5] Creates a new user in database using UserModel.create().
    Returns 400 Bad Request if ID already exists.
    """
    try:
        return user_model.create(user_in, db=db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# --- WEEK 3, 4, 5: PUT /api/users/:id (Replace a user in DB) ---
@router.put("/{user_id}", response_model=User, summary="[ApiUserController] Replace a user in DB (Full Update)")
async def update_api_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    """
    [Week 3 & 4 & 5] Completely replaces user fields in database.
    Returns 404 Not Found if user doesn't exist.
    """
    updated_user = user_model.update(user_id, user_in, db=db)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user


# --- WEEK 3, 4, 5: PATCH /api/users/:id (Partially update a user in DB) ---
@router.patch("/{user_id}", response_model=User, summary="[ApiUserController] Partially update a user in DB")
async def patch_api_user(user_id: int, user_in: UserPatch, db: Session = Depends(get_db)):
    """
    [Week 3 & 4 & 5] Partially updates user fields in database.
    Returns 404 Not Found if user doesn't exist.
    """
    patched_user = user_model.patch(user_id, user_in, db=db)
    if not patched_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return patched_user


# --- WEEK 3, 4, 5: DELETE /api/users/:id (Delete a user from DB) ---
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="[ApiUserController] Delete a user from DB")
async def delete_api_user(user_id: int, db: Session = Depends(get_db)):
    """
    [Week 3 & 4 & 5] Deletes user by ID from database.
    Returns 204 No Content on success, or 404 Not Found.
    """
    success = user_model.delete(user_id, db=db)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
