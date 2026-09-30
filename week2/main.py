from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="Alumni System - Week 2")

class User(BaseModel):
    id: int
    name: str
    email: str
    department: Optional[str] = None

# Örnek başlangıç verileri
users_db: List[User] = [
    User(id=1, name="Osman Parlak", email="osman@example.com", department="MIS"),
    User(id=2, name="Ahmet Yilmaz", email="ahmet@example.com", department="Computer Engineering")
]

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Week 2 API is running"}

@app.get("/api/users", response_model=List[User])
def get_users():
    return users_db

@app.get("/api/users/{user_id}", response_model=User)
def get_user_by_id(user_id: int):
    for user in users_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")