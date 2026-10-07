from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Response
from app.models import User, UserCreate, UserUpdate, UserPatch, user_model

# ===================================================================
# WEEK 4: ApiUserController (/api/users)
# Dedicated controller for pure REST API consumers
# ===================================================================

router = APIRouter(
    prefix="/api/users",
    tags=["API Users (ApiUserController)"]
)


# --- WEEK 2 & 3: GET /api/users (List users ordered by ID) ---
@router.get("", response_model=List[User], summary="[ApiUserController] List users ordered by ID")
async def get_api_users(search: Optional[str] = None, department: Optional[str] = None):
    """
    [Week 2 & 3 & 4] Returns all users ordered by ID using UserModel.get_all().
    """
    return user_model.get_all(search=search, department=department, order_by_id=True)


# --- WEEK 2: GET /api/users/:id (Get one user) ---
@router.get("/{user_id}", response_model=User, summary="[ApiUserController] Get one user by ID")
async def get_api_user_by_id(user_id: int):
    """
    [Week 2 & 4] Fetches a single user by ID using UserModel.get_by_id().
    """
    user = user_model.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# --- WEEK 3: POST /api/users (Create an in-memory user) ---
@router.post("", response_model=User, status_code=status.HTTP_201_CREATED, summary="[ApiUserController] Create an in-memory user")
async def create_api_user(user_in: UserCreate):
    """
    [Week 3 & 4] Creates a new user in-memory using UserModel.create().
    Returns 400 Bad Request if ID already exists.
    """
    try:
        return user_model.create(user_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# --- WEEK 3: PUT /api/users/:id (Replace a user) ---
@router.put("/{user_id}", response_model=User, summary="[ApiUserController] Replace a user (Full Update)")
async def update_api_user(user_id: int, user_in: UserUpdate):
    """
    [Week 3 & 4] Completely replaces user fields using UserModel.update().
    Returns 404 Not Found if user doesn't exist.
    """
    updated_user = user_model.update(user_id, user_in)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user


# --- WEEK 3: PATCH /api/users/:id (Partially update a user) ---
@router.patch("/{user_id}", response_model=User, summary="[ApiUserController] Partially update a user")
async def patch_api_user(user_id: int, user_in: UserPatch):
    """
    [Week 3 & 4] Partially updates user fields using UserModel.patch().
    Returns 404 Not Found if user doesn't exist.
    """
    patched_user = user_model.patch(user_id, user_in)
    if not patched_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return patched_user


# --- WEEK 3: DELETE /api/users/:id (Delete a user) ---
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="[ApiUserController] Delete a user")
async def delete_api_user(user_id: int):
    """
    [Week 3 & 4] Deletes user by ID using UserModel.delete().
    Returns 204 No Content on success, or 404 Not Found.
    """
    success = user_model.delete(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
