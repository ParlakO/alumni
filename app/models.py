from typing import List, Optional
from pydantic import BaseModel, Field


# ===================================================================
# WEEK 2 & WEEK 3: Pydantic Data Schemas (Validation & Serialization)
# ===================================================================

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Osman Parlak")
    email: str = Field(..., min_length=5, max_length=120, example="osman@example.com")
    department: str = Field(..., min_length=2, max_length=100, example="MIS")


class UserCreate(BaseModel):
    """Week 3: Schema for user creation with optional manual ID."""
    id: Optional[int] = Field(None, description="Opsiyonel ID. Belirtilmezse otomatik siradaki ID verilir.")
    name: str = Field(..., min_length=2, max_length=100, example="Osman Parlak")
    email: str = Field(..., min_length=5, max_length=120, example="osman@example.com")
    department: str = Field(..., min_length=2, max_length=100, example="MIS")


class UserUpdate(BaseModel):
    """Week 3: Schema for full replacement (PUT) - all fields required."""
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=120)
    department: str = Field(..., min_length=2, max_length=100)


class UserPatch(BaseModel):
    """Week 3: Schema for partial update (PATCH) - all fields optional."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = Field(None, min_length=5, max_length=120)
    department: Optional[str] = Field(None, min_length=2, max_length=100)


class User(UserBase):
    """Schema for returning user data with guaranteed ID."""
    id: int


# ===================================================================
# WEEK 4: UserModel (In-Memory Data Model with CRUD Functions - No DB)
# ===================================================================

class UserModel:
    """
    User Model without database connection.
    Encapsulates all in-memory CRUD operations, business rules, and validations.
    Shared by both UserController and ApiUserController.
    """

    def __init__(self):
        # Week 2 & 3: Initial seed data
        self._users: List[dict] = [
            {"id": 1, "name": "Osman Parlak", "email": "osman@example.com", "department": "MIS"},
            {"id": 2, "name": "Ahmet Yilmaz", "email": "ahmet@example.com", "department": "Computer Engineering"}
        ]

    # CRUD - Read All (Week 2 & Week 3)
    def get_all(
        self,
        search: Optional[str] = None,
        department: Optional[str] = None,
        order_by_id: bool = True
    ) -> List[dict]:
        """Returns all users with optional filtering, ordered by ID."""
        results = list(self._users)

        if department:
            dept_lower = department.lower()
            results = [u for u in results if u.get("department", "").lower() == dept_lower]

        if search:
            q = search.lower()
            results = [
                u for u in results
                if q in u.get("name", "").lower()
                or q in u.get("email", "").lower()
                or q in u.get("department", "").lower()
            ]

        if order_by_id:
            results.sort(key=lambda u: u["id"])

        return results

    # CRUD - Read One by ID (Week 2)
    def get_by_id(self, user_id: int) -> Optional[dict]:
        """Finds and returns a user by ID, or None if not found."""
        return next((u for u in self._users if u["id"] == user_id), None)

    # Check Existence (Week 3)
    def exists_by_id(self, user_id: int) -> bool:
        """Checks if a user with the given ID already exists."""
        return any(u["id"] == user_id for u in self._users)

    # CRUD - Create (Week 3)
    def create(self, user_data: UserCreate) -> dict:
        """
        Creates a new user.
        Raises ValueError if explicit ID already exists.
        Auto-generates sequential ID if ID is omitted.
        """
        if user_data.id is not None:
            if self.exists_by_id(user_data.id):
                raise ValueError("User ID already exists")
            assigned_id = user_data.id
        else:
            assigned_id = max([u["id"] for u in self._users], default=0) + 1

        new_user = {
            "id": assigned_id,
            "name": user_data.name,
            "email": user_data.email,
            "department": user_data.department,
        }
        self._users.append(new_user)
        return new_user

    # CRUD - Update (PUT - Week 3)
    def update(self, user_id: int, user_data: UserUpdate) -> Optional[dict]:
        """
        Replaces user data completely.
        Returns the updated user dict or None if not found.
        """
        index = next((idx for idx, u in enumerate(self._users) if u["id"] == user_id), -1)
        if index == -1:
            return None

        updated_user = {
            "id": user_id,
            "name": user_data.name,
            "email": user_data.email,
            "department": user_data.department,
        }
        self._users[index] = updated_user
        return updated_user

    # CRUD - Patch (PATCH - Week 3)
    def patch(self, user_id: int, user_data: UserPatch) -> Optional[dict]:
        """
        Partially updates provided fields.
        Returns updated user dict or None if not found.
        """
        user = self.get_by_id(user_id)
        if not user:
            return None

        if user_data.name is not None:
            user["name"] = user_data.name
        if user_data.email is not None:
            user["email"] = user_data.email
        if user_data.department is not None:
            user["department"] = user_data.department

        return user

    # CRUD - Delete (Week 3)
    def delete(self, user_id: int) -> bool:
        """
        Deletes a user by ID.
        Returns True if deleted, False if user does not exist.
        """
        index = next((idx for idx, u in enumerate(self._users) if u["id"] == user_id), -1)
        if index == -1:
            return False

        self._users.pop(index)
        return True


# Singleton instance of UserModel without DB
user_model = UserModel()
