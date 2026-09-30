from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

# Uvicorn'un aradığı 'app' nesnesi burasıdır:
app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    email: str
    department: Optional[str] = None

users_db: List[User] = [
    User(id=1, name="Osman Parlak", email="osman@example.com", department="MIS"),
    User(id=2, name="Ahmet Yilmaz", email="ahmet@example.com", department="Computer Engineering")
]

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "API is healthy and running"}

@app.get("/api/users", response_model=List[User])
def get_users():
    return users_db

@app.post("/api/users", response_model=User, status_code=201)
def create_user(user: User):
    for existing_user in users_db:
        if existing_user.id == user.id:
            raise HTTPException(status_code=400, detail="User ID already exists")
    users_db.append(user)
    return user