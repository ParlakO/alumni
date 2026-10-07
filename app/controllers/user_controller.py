import os
from typing import Optional
from fastapi import APIRouter, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.models import User, UserCreate, UserUpdate, UserPatch, user_model

# ===================================================================
# WEEK 4: UserController (/users)
# Web controller that uses the VIEW LAYER (Jinja2 templates).
#   GET  /users -> listing  (renders app/views/users/index.html)
#   POST /users -> creating (HTML form submit -> redirect to GET /users)
# ===================================================================

VIEWS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "views")
templates = Jinja2Templates(directory=VIEWS_DIR)

router = APIRouter(
    prefix="/users",
    tags=["Users (UserController)"]
)


def _render_users_page(request: Request, status_code: int = 200, error: Optional[str] = None,
                       success: Optional[str] = None, form: Optional[dict] = None) -> HTMLResponse:
    """Helper: Controller asks Model for data, then passes it to the View."""
    return templates.TemplateResponse(
        request,
        "users/index.html",
        {
            "title": "Mezun Listesi",
            "users": user_model.get_all(order_by_id=True),
            "error": error,
            "success": success,
            "form": form or {},
        },
        status_code=status_code,
    )


# --- WEEK 4 (View): GET /users => listing ---
@router.get("", response_class=HTMLResponse, summary="[UserController] List users (HTML view)")
async def list_users_view(request: Request, created: Optional[int] = None):
    """
    [Week 4 - View Layer] Renders the users list page (users/index.html), ordered by ID.
    """
    success = f"Mezun #{created} başarıyla oluşturuldu." if created is not None else None
    return _render_users_page(request, success=success)


# --- WEEK 4 (View): POST /users => creating ---
@router.post("", response_class=HTMLResponse, summary="[UserController] Create user (HTML form)")
async def create_user_view(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    department: str = Form(...),
    id: Optional[str] = Form(None),
):
    """
    [Week 4 - View Layer] Handles the HTML form submit.
    Success -> 303 redirect to GET /users (Post/Redirect/Get pattern).
    Failure -> re-renders the view with an error message (400).
    """
    form = {"id": id, "name": name, "email": email, "department": department}

    try:
        user_id = int(id) if id not in (None, "") else None
        user_in = UserCreate(id=user_id, name=name, email=email, department=department)
        new_user = user_model.create(user_in)
    except ValidationError as e:
        first = e.errors()[0]
        field = first["loc"][-1] if first.get("loc") else "form"
        return _render_users_page(request, status_code=400, error=f"Geçersiz alan '{field}': {first['msg']}", form=form)
    except ValueError as e:
        # int() conversion error or "User ID already exists"
        return _render_users_page(request, status_code=400, error=str(e), form=form)

    return RedirectResponse(url=f"/users?created={new_user['id']}", status_code=status.HTTP_303_SEE_OTHER)


# ===================================================================
# WEEK 3 & 4: Remaining JSON CRUD routes on /users (via UserModel)
# ===================================================================

# --- WEEK 2: GET /users/:id (Get one user) ---
@router.get("/{user_id}", response_model=User, summary="[UserController] Get one user by ID")
async def get_user_by_id(user_id: int):
    """[Week 2 & 4] Fetches a single user by ID using UserModel.get_by_id()."""
    user = user_model.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# --- WEEK 3: PUT /users/:id (Replace user) ---
@router.put("/{user_id}", response_model=User, summary="[UserController] Replace user (Full Update)")
async def update_user(user_id: int, user_in: UserUpdate):
    """[Week 3 & 4] Completely replaces user fields using UserModel.update()."""
    updated_user = user_model.update(user_id, user_in)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user


# --- WEEK 3: PATCH /users/:id (Partially update user) ---
@router.patch("/{user_id}", response_model=User, summary="[UserController] Partially update user")
async def patch_user(user_id: int, user_in: UserPatch):
    """[Week 3 & 4] Partially updates user fields using UserModel.patch()."""
    patched_user = user_model.patch(user_id, user_in)
    if not patched_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return patched_user


# --- WEEK 3: DELETE /users/:id (Delete user) ---
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="[UserController] Delete user")
async def delete_user(user_id: int):
    """[Week 3 & 4] Deletes user by ID using UserModel.delete()."""
    if not user_model.delete(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
