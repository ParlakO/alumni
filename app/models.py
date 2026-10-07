from typing import Optional
from pydantic import BaseModel, Field

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Osman Parlak")
    email: str = Field(..., min_length=5, max_length=120, example="osman@example.com")
    department: str = Field(..., min_length=2, max_length=100, example="MIS")

class UserCreate(BaseModel):
    id: Optional[int] = Field(None, description="Opsiyonel ID. Belirtilmezse otomatik artırılır.")
    name: str = Field(..., min_length=2, max_length=100, example="Osman Parlak")
    email: str = Field(..., min_length=5, max_length=120, example="osman@example.com")
    department: str = Field(..., min_length=2, max_length=100, example="MIS")

class UserUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=120)
    department: str = Field(..., min_length=2, max_length=100)

class UserPatch(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = Field(None, min_length=5, max_length=120)
    department: Optional[str] = Field(None, min_length=2, max_length=100)

class User(UserBase):
    id: int
