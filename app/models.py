from typing import List, Optional, Any
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
# ===================================================================
# WEEK 4 & WEEK 5: UserModel (Database-Backed CRUD Model via SQLAlchemy)
# ===================================================================

from sqlalchemy import func, or_
from app.database import SessionLocal, UserRecord, seed_database


class UserModel:
    """
    User Model backed by SQLAlchemy and SQLite database.
    Encapsulates all persistent CRUD operations, business rules, and validations.
    Maintains 100% backward compatibility with UserController and ApiUserController.
    """

    def __init__(self):
        # Initialize tables and seed records if database is empty
        seed_database()

    @staticmethod
    def _get_session(db: Optional[Any] = None):
        from sqlalchemy.orm import Session as SQLAlchemySession
        if isinstance(db, SQLAlchemySession):
            return db, False
        return SessionLocal(), True

    # CRUD - Read All (Week 2 & Week 3 & Week 5)
    def get_all(
        self,
        search: Optional[str] = None,
        department: Optional[str] = None,
        order_by_id: bool = True,
        db: Optional[Any] = None
    ) -> List[dict]:
        """Returns all users with optional filtering, ordered by ID."""
        session, close_needed = self._get_session(db)
        try:
            query = session.query(UserRecord)

            if department:
                query = query.filter(func.lower(UserRecord.department) == department.lower())

            if search:
                pattern = f"%{search.lower()}%"
                query = query.filter(
                    or_(
                        func.lower(UserRecord.name).like(pattern),
                        func.lower(UserRecord.email).like(pattern),
                        func.lower(UserRecord.department).like(pattern)
                    )
                )

            if order_by_id:
                query = query.order_by(UserRecord.id.asc())

            records = query.all()
            return [u.to_dict() for u in records]
        finally:
            if close_needed:
                session.close()

    # CRUD - Read One by ID (Week 2 & Week 5)
    def get_by_id(self, user_id: int, db: Optional[Any] = None) -> Optional[dict]:
        """Finds and returns a user by ID, or None if not found."""
        session, close_needed = self._get_session(db)
        try:
            record = session.query(UserRecord).filter(UserRecord.id == user_id).first()
            return record.to_dict() if record else None
        finally:
            if close_needed:
                session.close()

    # Check Existence (Week 3 & Week 5)
    def exists_by_id(self, user_id: int, db: Optional[Any] = None) -> bool:
        """Checks if a user with the given ID already exists."""
        session, close_needed = self._get_session(db)
        try:
            return session.query(UserRecord).filter(UserRecord.id == user_id).first() is not None
        finally:
            if close_needed:
                session.close()

    # CRUD - Create (Week 3 & Week 5)
    def create(self, user_data: UserCreate, db: Optional[Any] = None) -> dict:
        """
        Creates a new user in the database.
        Raises ValueError if explicit ID already exists.
        Auto-generates sequential ID if ID is omitted.
        """
        session, close_needed = self._get_session(db)
        try:
            if user_data.id is not None:
                if session.query(UserRecord).filter(UserRecord.id == user_data.id).first() is not None:
                    raise ValueError("User ID already exists")
                assigned_id = user_data.id
            else:
                max_id = session.query(func.max(UserRecord.id)).scalar() or 0
                assigned_id = max_id + 1

            new_record = UserRecord(
                id=assigned_id,
                name=user_data.name,
                email=user_data.email,
                department=user_data.department
            )
            session.add(new_record)
            session.commit()
            session.refresh(new_record)
            return new_record.to_dict()
        finally:
            if close_needed:
                session.close()

    # CRUD - Update (PUT - Week 3 & Week 5)
    def update(self, user_id: int, user_data: UserUpdate, db: Optional[Any] = None) -> Optional[dict]:
        """
        Replaces user data completely.
        Returns the updated user dict or None if not found.
        """
        session, close_needed = self._get_session(db)
        try:
            record = session.query(UserRecord).filter(UserRecord.id == user_id).first()
            if not record:
                return None

            record.name = user_data.name
            record.email = user_data.email
            record.department = user_data.department
            session.commit()
            session.refresh(record)
            return record.to_dict()
        finally:
            if close_needed:
                session.close()

    # CRUD - Patch (PATCH - Week 3 & Week 5)
    def patch(self, user_id: int, user_data: UserPatch, db: Optional[Any] = None) -> Optional[dict]:
        """
        Partially updates provided fields.
        Returns updated user dict or None if not found.
        """
        session, close_needed = self._get_session(db)
        try:
            record = session.query(UserRecord).filter(UserRecord.id == user_id).first()
            if not record:
                return None

            if user_data.name is not None:
                record.name = user_data.name
            if user_data.email is not None:
                record.email = user_data.email
            if user_data.department is not None:
                record.department = user_data.department

            session.commit()
            session.refresh(record)
            return record.to_dict()
        finally:
            if close_needed:
                session.close()

    # CRUD - Delete (Week 3 & Week 5)
    def delete(self, user_id: int, db: Optional[Any] = None) -> bool:
        """
        Deletes a user by ID.
        Returns True if deleted, False if user does not exist.
        """
        session, close_needed = self._get_session(db)
        try:
            record = session.query(UserRecord).filter(UserRecord.id == user_id).first()
            if not record:
                return False

            session.delete(record)
            session.commit()
            return True
        finally:
            if close_needed:
                session.close()


# Singleton instance of UserModel with Database backing
user_model = UserModel()

