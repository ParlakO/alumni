from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

# Mezun Modeli (Data Schema)
class Alumni(BaseModel):
    id: int
    name: str
    graduation_year: int
    department: str
    company: Optional[str] = None

# Örnek Veri Hafızası (In-Memory List)
alumni_db: List[Alumni] = [
    Alumni(id=1, name="Ahmet Yilmaz", graduation_year=2022, department="MIS", company="Tech Co"),
    Alumni(id=2, name="Ayse Kaya", graduation_year=2023, department="MIS", company="Data Corp")
]

# --- 1. & 2. Hafta Route'ları ---
@app.get("/")
def read_root():
    return {"message": "Welcome to Alumni Tracking System"}

@app.get("/hello")
def say_hello():
    return {"message": "Hello, World!"}

@app.get("/hello/{name}")
def say_hello_name(name: str):
    return {"message": f"Hello, {name}"}

@app.get("/sum/{a}/{b}")
def calculate_sum(a: int, b: int):
    return {"a": a, "b": b, "result": a + b}

@app.get("/about")
def get_about():
    return {
        "project": "Alumni Tracking System",
        "course": "Web Programming - YBSB3001",
        "author": "Osman Parlak"
    }

# --- 3. Hafta: HTTP Yöntemleri & CRUD ---

# 1. READ ALL (GET) - Tüm mezunları getir
@app.get("/alumni", response_model=List[Alumni])
def get_all_alumni():
    return alumni_db

# 2. READ ONE (GET) - ID ile mezun getir
@app.get("/alumni/{alumni_id}", response_model=Alumni)
def get_alumni(alumni_id: int):
    for item in alumni_db:
        if item.id == alumni_id:
            return item
    raise HTTPException(status_code=404, detail="Alumni not found")

# 3. CREATE (POST) - Yeni mezun ekle
@app.post("/alumni", response_model=Alumni, status_code=201)
def create_alumni(alumni: Alumni):
    for item in alumni_db:
        if item.id == alumni.id:
            raise HTTPException(status_code=400, detail="Alumni ID already exists")
    alumni_db.append(alumni)
    return alumni

# 4. UPDATE (PUT) - Mezun bilgilerini güncelle
@app.put("/alumni/{alumni_id}", response_model=Alumni)
def update_alumni(alumni_id: int, updated_alumni: Alumni):
    for index, item in enumerate(alumni_db):
        if item.id == alumni_id:
            alumni_db[index] = updated_alumni
            return updated_alumni
    raise HTTPException(status_code=404, detail="Alumni not found")

# 5. DELETE (DELETE) - Mezun kaydını sil
@app.delete("/alumni/{alumni_id}")
def delete_alumni(alumni_id: int):
    for index, item in enumerate(alumni_db):
        if item.id == alumni_id:
            deleted_item = alumni_db.pop(index)
            return {"message": f"Alumni {deleted_item.name} deleted successfully"}
    raise HTTPException(status_code=404, detail="Alumni not found")