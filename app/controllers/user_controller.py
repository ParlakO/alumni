from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Response
from app.models import User, UserCreate, UserUpdate, UserPatch, user_model

# ===================================================================
# WEEK 4: UserController (/users)
# User controller mounted under /users
# ===================================================================

router = APIRouter(
    prefix="/users",
    tags=["Users (UserController)"]
)


# --- WEEK 2 & 3: GET /users (List users ordered by ID) ---
@router.get("", response_model=List[User], summary="[UserController] List users ordered by ID")
async def get_users(search: Optional[str] = None, department: Optional[str] = None):
    """
    [Week 2 & 3 & 4] Returns all users ordered by ID using UserModel.get_all().
    """
    return user_model.get_all(search=search, department=department, order_by_id=True)


# --- WEEK 2: GET /users/:id (Get one user) ---
@router.get("/{user_id}", response_model=User, summary="[UserController] Get one user by ID")
async def get_user_by_id(user_id: int):
    """
    [Week 2 & 4] Fetches a single user by ID using UserModel.get_by_id().
    """
    user = user_model.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# --- WEEK 3: POST /users (Create user) ---
@router.post("", response_model=User, status_code=status.HTTP_201_CREATED, summary="[UserController] Create user")
async def create_user(user_in: UserCreate):
    """
    [Week 3 & 4] Creates a new user in-memory using UserModel.create().
    """
    try:
        return user_model.create(user_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# --- WEEK 3: PUT /users/:id (Replace user) ---
@router.put("/{user_id}", response_model=User, summary="[UserController] Replace user (Full Update)")
async def update_user(user_id: int, user_in: UserUpdate):
    """
    [Week 3 & 4] Completely replaces user fields using UserModel.update().
    """
    updated_user = user_model.update(user_id, user_in)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user


# --- WEEK 3: PATCH /users/:id (Partially update user) ---
@router.patch("/{user_id}", response_model=User, summary="[UserController] Partially update user")
async def patch_user(user_id: int, user_in: UserPatch):
    """
    [Week 3 & 4] Partially updates user fields using UserModel.patch().
    """
    patched_user = user_model.patch(user_id, user_in)
    if not patched_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return patched_user


# --- WEEK 3: DELETE /users/:id (Delete user) ---
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="[UserController] Delete user")
async def delete_user(user_id: int):
    """
    [Week 3 & 4] Deletes user by ID using UserModel.delete().
    """
    success = user_model.delete(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
