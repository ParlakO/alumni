import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.models import User, UserCreate, UserPatch, UserUpdate

app = FastAPI(
    title="Alumni Tracking System API",
    description="University Alumni Management System API with MVC Architecture (Web Programming YBSB3001).",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to static frontend files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# In-Memory Database (Initial Data: Week 2 & 3)
users_db: List[dict] = [
    {"id": 1, "name": "Osman Parlak", "email": "osman@example.com", "department": "MIS"},
    {"id": 2, "name": "Ahmet Yilmaz", "email": "ahmet@example.com", "department": "Computer Engineering"}
]


# ===================================================================
# 1. Core & Utility Endpoints
# ===================================================================

# GET / -> API welcome message
@app.get("/", summary="API Welcome Message / Web Interface")
async def read_root(request: Request):
    """
    Returns the web page in browser or API welcome message for API/JSON clients.
    """
    accept_header = request.headers.get("accept", "")
    format_param = request.query_params.get("format", "")

    # If queried as JSON or not requesting HTML, return welcome message
    if format_param == "json" or ("application/json" in accept_header and "text/html" not in accept_header):
        return {"message": "Welcome to the Alumni Tracking System API!"}

    # Serve the frontend UI if available
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)

    return {"message": "Welcome to the Alumni Tracking System API!"}


# GET /hello -> Generic greeting
@app.get("/hello", summary="Generic Greeting")
async def get_hello():
    """Returns a generic greeting message."""
    return {"message": "Hello, World!"}


# GET /hello/:name -> Named greeting
@app.get("/hello/{name}", summary="Named Greeting")
async def get_hello_name(name: str):
    """Returns a personalized greeting message."""
    return {"message": f"Hello, {name}!"}


# GET /sum/:a/:b -> Sum of two integers
@app.get("/sum/{a}/{b}", summary="Sum of Two Integers")
async def get_sum(a: int, b: int):
    """Calculates and returns the sum of two integers."""
    return {"a": a, "b": b, "sum": a + b}


# GET /about -> Project information
@app.get("/about", summary="Project Information")
async def get_about():
    """Returns metadata and information about the Alumni Tracking System project."""
    return {
        "project": "Alumni Tracking System",
        "course": "YBSB3001 - Web Programming",
        "institution": "Istanbul University",
        "architecture": "MVC (Model-View-Controller)",
        "framework": "FastAPI (Python 3.11+)",
        "container": "Docker & Docker Compose",
        "version": "1.0.0",
        "author": "Osman Parlak",
        "description": "A modern university alumni tracking portal with full RESTful CRUD capabilities."
    }


# GET /api/health -> Health check
@app.get("/api/health", summary="Health Check")
async def health_check():
    """Returns API health status."""
    return {"status": "ok", "message": "Alumni System API is healthy and running"}


# ===================================================================
# 2. Alumni Users CRUD Endpoints (Controller Layer)
# ===================================================================

# GET /api/users -> List users ordered by ID
@app.get("/api/users", response_model=List[User], summary="List Users Ordered by ID")
async def get_users(search: Optional[str] = None, department: Optional[str] = None):
    """
    Returns the list of alumni users, strictly ordered by ID.
    Supports optional search query and department filter.
    """
    results = users_db
    if department:
        results = [u for u in results if u.get("department", "").lower() == department.lower()]
    if search:
        s = search.lower()
        results = [
            u for u in results
            if s in u.get("name", "").lower() or s in u.get("email", "").lower() or s in u.get("department", "").lower()
        ]
    return sorted(results, key=lambda u: u["id"])


# GET /api/users/:id -> Get one user
@app.get("/api/users/{user_id}", response_model=User, summary="Get One User")
async def get_user_by_id(user_id: int):
    """Fetches a single alumni user by ID."""
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# POST /api/users -> Create an in-memory user
@app.post("/api/users", response_model=User, status_code=status.HTTP_201_CREATED, summary="Create an In-Memory User")
async def create_user(user_in: UserCreate):
    """
    Creates a new alumni user in the in-memory database.
    If ID is provided, checks for uniqueness (400 if duplicate).
    If ID is omitted, auto-generates the next sequential ID.
    """
    if user_in.id is not None:
        exists = any(u["id"] == user_in.id for u in users_db)
        if exists:
            raise HTTPException(status_code=400, detail="User ID already exists")
        assigned_id = user_in.id
    else:
        assigned_id = max([u["id"] for u in users_db], default=0) + 1

    new_user = {
        "id": assigned_id,
        "name": user_in.name,
        "email": user_in.email,
        "department": user_in.department,
    }
    users_db.append(new_user)
    return new_user


# PUT /api/users/:id -> Replace a user
@app.put("/api/users/{user_id}", response_model=User, summary="Replace a User")
async def update_user(user_id: int, user_in: UserUpdate):
    """
    Replaces an existing user completely with the provided payload.
    """
    index = next((idx for idx, u in enumerate(users_db) if u["id"] == user_id), -1)
    if index == -1:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = {
        "id": user_id,
        "name": user_in.name,
        "email": user_in.email,
        "department": user_in.department,
    }
    users_db[index] = updated_user
    return updated_user


# PATCH /api/users/:id -> Partially update a user
@app.patch("/api/users/{user_id}", response_model=User, summary="Partially Update a User")
async def patch_user(user_id: int, user_in: UserPatch):
    """
    Partially updates specific fields of an existing user.
    """
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_in.name is not None:
        user["name"] = user_in.name
    if user_in.email is not None:
        user["email"] = user_in.email
    if user_in.department is not None:
        user["department"] = user_in.department

    return user


# DELETE /api/users/:id -> Delete a user
@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a User")
async def delete_user(user_id: int):
    """
    Deletes an alumni user by ID from the in-memory store.
    """
    index = next((idx for idx, u in enumerate(users_db) if u["id"] == user_id), -1)
    if index == -1:
        raise HTTPException(status_code=404, detail="User not found")

    users_db.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 3000))
    print(f"Alumni System Server running on port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
