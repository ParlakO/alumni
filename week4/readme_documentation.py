"""
===================================================================
                FastAPI User Management API
===================================================================

MVC (Model-View-Controller) Architecture Mapping:
-------------------------------------------------

1. Model (Data Layer & Validation):
   - Pydantic Models (`User`, `UserUpdate`): Define data schema, data 
     types, and automatic validation for input payloads.
   - `users_db`: Acts as the in-memory data store holding `User` models.

2. View (Presentation Layer):
   - `response_model` parameter in routes: Defines how data is structured 
     and filtered for the output response.
   - FastAPI Serialization: Converts Pydantic objects into standard JSON 
     responses delivered back to the client along with HTTP status codes.

3. Controller (Routing & Request Logic):
   - Endpoint Functions (`health_check`, `get_users`, `create_user`, 
     `update_user_put`, `update_user_patch`, `delete_user`): Process incoming 
     HTTP requests, apply business logic/validation, manipulate the data model, 
     and trigger responses.

Endpoints Overview:
-------------------
- GET    /api/health            -> Service health status
- GET    /api/users             -> Fetch all users
- POST   /api/users             -> Create a new user
- PUT    /api/users/{user_id}   -> Full update of a user
- PATCH  /api/users/{user_id}   -> Partial update of a user
- DELETE /api/users/{user_id}   -> Delete a user by ID
===================================================================
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    email: str
    department: Optional[str] = None

# Kullanıcı Güncelleme için (Alanların hepsi opsiyonel)
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None

users_db: List[User] = [
    User(id=1, name="Osman Parlak", email="osman@example.com", department="MIS"),
    User(id=2, name="Ahmet Yilmaz", email="ahmet@example.com", department="Computer Engineering")
]

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "API is healthy and running"}

# 1. Aşama: Tüm Kullanıcıları Listele (GET /api/users)
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

# 2. Aşama: Kullanıcı Güncelleme (PUT /api/users/{user_id}) - Tüm Alanları Yeniler
@app.put("/api/users/{user_id}", response_model=User)
def update_user_put(user_id: int, updated_user: User):
    for index, existing_user in enumerate(users_db):
        if existing_user.id == user_id:
            users_db[index] = updated_user
            return updated_user
    raise HTTPException(status_code=404, detail="User not found")

# 2. Aşama Alternatifi: Kısmi Güncelleme (PATCH /api/users/{user_id}) - Sadece Gönderilen Alanı Değiştirir
@app.patch("/api/users/{user_id}", response_model=User)
def update_user_patch(user_id: int, user_update: UserUpdate):
    for existing_user in users_db:
        if existing_user.id == user_id:
            stored_user_data = existing_user.model_dump()
            update_data = user_update.model_dump(exclude_unset=True)
            stored_user_data.update(update_data)
            
            updated_user = User(**stored_user_data)
            existing_user.name = updated_user.name
            existing_user.email = updated_user.email
            existing_user.department = updated_user.department
            return existing_user
            
    raise HTTPException(status_code=404, detail="User not found")

# Kullanıcı Silme (DELETE /api/users/{user_id})
@app.delete("/api/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    for index, existing_user in enumerate(users_db):
        if existing_user.id == user_id:
            users_db.pop(index)
            return
    raise HTTPException(status_code=404, detail="User not found")