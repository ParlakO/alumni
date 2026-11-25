from typing import List, Optional, Any
from pydantic import BaseModel, Field
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload
from app.database import (
    SessionLocal,
    UserRecord,
    JobPostingRecord,
    ApplicationRecord,
    seed_database
)


# ===================================================================
# Pydantic Data Schemas (Validation & Serialization)
# ===================================================================

# --- 1. User & Auth Schemas ---
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Ada")
    email: str = Field(..., min_length=5, max_length=120, example="ada@iu.edu.tr")
    department: str = Field(..., min_length=2, max_length=100, example="Computer Engineering")
    role: str = Field(default="graduate", example="graduate")


class UserCreate(BaseModel):
    id: Optional[int] = Field(None, description="Opsiyonel ID. Belirtilmezse otomatik siradaki ID verilir.")
    name: str = Field(..., min_length=2, max_length=100, example="Ada")
    email: str = Field(..., min_length=5, max_length=120, example="ada@iu.edu.tr")
    department: str = Field(..., min_length=2, max_length=100, example="Computer Engineering")
    password: str = Field(default="secret123", min_length=6, max_length=128, example="secret123")
    role: str = Field(default="graduate", example="graduate")


class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Ayşe Yılmaz")
    email: str = Field(..., min_length=5, max_length=120, example="ayse@iu.edu.tr")
    department: str = Field(..., min_length=2, max_length=100, example="Yönetim Bilişim Sistemleri")
    password: str = Field(..., min_length=6, max_length=128, example="secret123")


class UserLogin(BaseModel):
    email: str = Field(..., min_length=3, max_length=120, example="ada@iu.edu.tr")
    password: str = Field(..., min_length=1, max_length=128, example="secret123")


class UserRoleUpdate(BaseModel):
    role: str = Field(..., example="admin", description="Role: 'graduate' or 'admin'")


class UserUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=120)
    department: str = Field(..., min_length=2, max_length=100)
    password: Optional[str] = Field(None, min_length=6, max_length=128)
    role: Optional[str] = Field(None)


class UserPatch(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = Field(None, min_length=5, max_length=120)
    department: Optional[str] = Field(None, min_length=2, max_length=100)
    password: Optional[str] = Field(None, min_length=6, max_length=128)
    role: Optional[str] = Field(None)


class User(UserBase):
    id: int


class AuthMeResponse(BaseModel):
    id: int
    name: str
    email: str
    department: str
    role: str


class AuthTokenResponse(BaseModel):
    token: str
    user: User


# --- 2. Job Posting Schemas ---
class JobPostingBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=120, example="Junior Developer")
    company: str = Field(..., min_length=1, max_length=100, example="Acme")
    city: Optional[str] = Field(None, max_length=100, example="Istanbul")
    description: Optional[str] = Field(None, example="Full-stack developer with FastAPI experience")


class JobPostingCreate(JobPostingBase):
    """
    POST /api/users/:id/jobs request body.
    User ID is passed via URL path parameter, not in the body.
    """
    pass


class JobPostingResponse(JobPostingBase):
    id: int
    user_id: int


# --- 3. Application Schemas (Many-to-Many Join Table) ---
class ApplicationCreate(BaseModel):
    """
    POST /api/jobs/:id/applications request body.
    Job Posting ID is passed via URL path parameter (:id).
    userId in body is optional and ignored by the server; applicant is always the logged-in user.
    """
    userId: Optional[int] = Field(None, description="Ignored on authenticated route; server derives applicant from JWT.")


class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    job_posting_id: int
    status: str = "applied"


class ApplicationStatusUpdate(BaseModel):
    status: str = Field(..., example="interview", description="New application status: applied, interview, accepted, rejected")


# --- 4. Include / Nested Schemas ---
class UserWithJobs(User):
    """
    Response model for GET /api/users/:id with include='jobs'.
    One answer containing records from both users and job_postings tables.
    """
    jobs: List[JobPostingResponse] = []


# ===================================================================
# Database-Backed CRUD Models (SQLAlchemy & Repository Pattern)
# ===================================================================

class UserModel:
    """
    User Model backed by SQLAlchemy and SQLite database.
    Encapsulates persistent CRUD operations and business rules.
    """

    def __init__(self):
        seed_database()

    @staticmethod
    def _get_session(db: Optional[Any] = None):
        from sqlalchemy.orm import Session as SQLAlchemySession
        if isinstance(db, SQLAlchemySession):
            return db, False
        return SessionLocal(), True

    def get_all(
        self,
        search: Optional[str] = None,
        department: Optional[str] = None,
        order_by_id: bool = True,
        db: Optional[Any] = None
    ) -> List[dict]:
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

    def get_by_id(
        self,
        user_id: int,
        include_jobs: bool = False,
        db: Optional[Any] = None
    ) -> Optional[dict]:
        """Finds user by ID, optionally eager-loading their job postings (include)."""
        session, close_needed = self._get_session(db)
        try:
            query = session.query(UserRecord)
            if include_jobs:
                query = query.options(joinedload(UserRecord.jobs))
            record = query.filter(UserRecord.id == user_id).first()
            return record.to_dict(include_jobs=include_jobs) if record else None
        finally:
            if close_needed:
                session.close()

    def exists_by_id(self, user_id: int, db: Optional[Any] = None) -> bool:
        session, close_needed = self._get_session(db)
        try:
            return session.query(UserRecord).filter(UserRecord.id == user_id).first() is not None
        finally:
            if close_needed:
                session.close()

    def get_by_email(self, email: str, db: Optional[Any] = None) -> Optional[dict]:
        session, close_needed = self._get_session(db)
        try:
            record = session.query(UserRecord).filter(
                func.lower(UserRecord.email) == email.strip().lower()
            ).first()
            return record.to_dict() if record else None
        finally:
            if close_needed:
                session.close()

    def authenticate(self, email: str, password: str, db: Optional[Any] = None) -> Optional[dict]:
        """Verifies credentials using bcrypt.checkpw and returns safe user dict (without hash)."""
        from app.auth import verify_password
        session, close_needed = self._get_session(db)
        try:
            record = session.query(UserRecord).filter(
                func.lower(UserRecord.email) == email.strip().lower()
            ).first()
            if not record or not verify_password(password, record.password_hash):
                return None
            return record.to_dict()
        finally:
            if close_needed:
                session.close()

    def create(self, user_data: UserCreate, db: Optional[Any] = None) -> dict:
        from app.auth import hash_password, VALID_ROLES
        session, close_needed = self._get_session(db)
        try:
            if user_data.id is not None:
                if session.query(UserRecord).filter(UserRecord.id == user_data.id).first() is not None:
                    raise ValueError("User ID already exists")
                assigned_id = user_data.id
            else:
                max_id = session.query(func.max(UserRecord.id)).scalar() or 0
                assigned_id = max_id + 1

            normalized_email = user_data.email.strip().lower()
            if session.query(UserRecord).filter(func.lower(UserRecord.email) == normalized_email).first() is not None:
                raise ValueError("Email already registered")

            role = (user_data.role or "graduate").strip().lower()
            if role not in VALID_ROLES:
                raise ValueError("Invalid role. Must be 'graduate' or 'admin'")

            new_record = UserRecord(
                id=assigned_id,
                name=user_data.name.strip(),
                email=normalized_email,
                department=user_data.department.strip(),
                password_hash=hash_password(user_data.password),
                role=role
            )
            session.add(new_record)
            session.commit()
            session.refresh(new_record)
            return new_record.to_dict()
        finally:
            if close_needed:
                session.close()

    def update(self, user_id: int, user_data: UserUpdate, allow_role_change: bool = False, db: Optional[Any] = None) -> Optional[dict]:
        from app.auth import hash_password, VALID_ROLES
        session, close_needed = self._get_session(db)
        try:
            record = session.query(UserRecord).filter(UserRecord.id == user_id).first()
            if not record:
                return None
            record.name = user_data.name.strip()
            record.email = user_data.email.strip().lower()
            record.department = user_data.department.strip()
            if user_data.password:
                record.password_hash = hash_password(user_data.password)
            if allow_role_change and user_data.role is not None:
                role = user_data.role.strip().lower()
                if role not in VALID_ROLES:
                    raise ValueError("Invalid role. Must be 'graduate' or 'admin'")
                record.role = role
            session.commit()
            session.refresh(record)
            return record.to_dict()
        finally:
            if close_needed:
                session.close()

    def patch(self, user_id: int, user_data: UserPatch, allow_role_change: bool = False, db: Optional[Any] = None) -> Optional[dict]:
        from app.auth import hash_password, VALID_ROLES
        session, close_needed = self._get_session(db)
        try:
            record = session.query(UserRecord).filter(UserRecord.id == user_id).first()
            if not record:
                return None
            if user_data.name is not None:
                record.name = user_data.name.strip()
            if user_data.email is not None:
                record.email = user_data.email.strip().lower()
            if user_data.department is not None:
                record.department = user_data.department.strip()
            if user_data.password is not None:
                record.password_hash = hash_password(user_data.password)
            if allow_role_change and user_data.role is not None:
                role = user_data.role.strip().lower()
                if role not in VALID_ROLES:
                    raise ValueError("Invalid role. Must be 'graduate' or 'admin'")
                record.role = role
            session.commit()
            session.refresh(record)
            return record.to_dict()
        finally:
            if close_needed:
                session.close()

    def update_role(self, user_id: int, new_role: str, db: Optional[Any] = None) -> Optional[dict]:
        from app.auth import VALID_ROLES
        role = new_role.strip().lower()
        if role not in VALID_ROLES:
            raise ValueError("Invalid role. Must be 'graduate' or 'admin'")
        session, close_needed = self._get_session(db)
        try:
            record = session.query(UserRecord).filter(UserRecord.id == user_id).first()
            if not record:
                return None
            record.role = role
            session.commit()
            session.refresh(record)
            return record.to_dict()
        finally:
            if close_needed:
                session.close()

    def delete(self, user_id: int, db: Optional[Any] = None) -> bool:
        session, close_needed = self._get_session(db)
        try:
            record = session.query(UserRecord).filter(UserRecord.id == user_id).first()
            if not record:
                return False
            # Enforce RESTRICT deletion rule: cannot delete user with active job postings
            has_jobs = session.query(JobPostingRecord).filter(JobPostingRecord.user_id == user_id).first() is not None
            if has_jobs:
                raise ValueError("Cannot delete user: user has active job postings (RESTRICT rule)")
            session.delete(record)
            session.commit()
            return True
        finally:
            if close_needed:
                session.close()


class JobPostingModel:
    """
    CRUD Model for JobPostings.
    Supports nested job creation (POST /api/users/:id/jobs) and filtering by user.
    """

    @staticmethod
    def _get_session(db: Optional[Any] = None):
        from sqlalchemy.orm import Session as SQLAlchemySession
        if isinstance(db, SQLAlchemySession):
            return db, False
        return SessionLocal(), True

    def create(
        self,
        user_id: int,
        job_data: JobPostingCreate,
        db: Optional[Any] = None
    ) -> dict:
        """
        Creates a job posting belonging to the user specified in URL (:id).
        Raises KeyError if user does not exist (handled as 404 Not Found).
        """
        session, close_needed = self._get_session(db)
        try:
            user = session.query(UserRecord).filter(UserRecord.id == user_id).first()
            if not user:
                raise KeyError(f"User with ID {user_id} not found")

            new_job = JobPostingRecord(
                user_id=user_id,
                title=job_data.title,
                company=job_data.company,
                city=job_data.city,
                description=job_data.description
            )
            session.add(new_job)
            session.commit()
            session.refresh(new_job)
            return new_job.to_dict()
        finally:
            if close_needed:
                session.close()

    def get_by_id(self, job_id: int, db: Optional[Any] = None) -> Optional[dict]:
        session, close_needed = self._get_session(db)
        try:
            job = session.query(JobPostingRecord).filter(JobPostingRecord.id == job_id).first()
            return job.to_dict() if job else None
        finally:
            if close_needed:
                session.close()

    def get_all(self, db: Optional[Any] = None) -> List[dict]:
        session, close_needed = self._get_session(db)
        try:
            jobs = session.query(JobPostingRecord).order_by(JobPostingRecord.id.asc()).all()
            return [j.to_dict() for j in jobs]
        finally:
            if close_needed:
                session.close()

    def get_by_user_id(self, user_id: int, db: Optional[Any] = None) -> List[dict]:
        session, close_needed = self._get_session(db)
        try:
            jobs = session.query(JobPostingRecord).filter(
                JobPostingRecord.user_id == user_id
            ).order_by(JobPostingRecord.id.asc()).all()
            return [j.to_dict() for j in jobs]
        finally:
            if close_needed:
                session.close()

    def delete(self, job_id: int, db: Optional[Any] = None) -> bool:
        session, close_needed = self._get_session(db)
        try:
            job = session.query(JobPostingRecord).filter(JobPostingRecord.id == job_id).first()
            if not job:
                return False
            session.delete(job)
            session.commit()
            return True
        finally:
            if close_needed:
                session.close()


class ApplicationModel:
    """
    CRUD Model for Applications (Many-to-Many join table).
    Enforces UNIQUE(user_id, job_posting_id) to prevent duplicate applications (409 Conflict).
    """

    @staticmethod
    def _get_session(db: Optional[Any] = None):
        from sqlalchemy.orm import Session as SQLAlchemySession
        if isinstance(db, SQLAlchemySession):
            return db, False
        return SessionLocal(), True

    def apply(
        self,
        job_posting_id: int,
        user_id: int,
        db: Optional[Any] = None
    ) -> dict:
        """
        Creates an application for user_id to job_posting_id.
        Raises KeyError if user or job does not exist (404).
        Raises ValueError if application already exists (409 Conflict).
        """
        session, close_needed = self._get_session(db)
        try:
            # Check user existence
            if not session.query(UserRecord).filter(UserRecord.id == user_id).first():
                raise KeyError(f"User with ID {user_id} not found")

            # Check job existence
            if not session.query(JobPostingRecord).filter(JobPostingRecord.id == job_posting_id).first():
                raise KeyError(f"Job posting with ID {job_posting_id} not found")

            # Check duplicate application (UNIQUE constraint)
            existing = session.query(ApplicationRecord).filter(
                ApplicationRecord.user_id == user_id,
                ApplicationRecord.job_posting_id == job_posting_id
            ).first()
            if existing:
                raise ValueError("User has already applied to this job posting")

            new_application = ApplicationRecord(
                user_id=user_id,
                job_posting_id=job_posting_id,
                status="applied"
            )
            session.add(new_application)
            session.commit()
            session.refresh(new_application)
            return new_application.to_dict()
        finally:
            if close_needed:
                session.close()

    def get_by_job_id(self, job_posting_id: int, db: Optional[Any] = None) -> List[dict]:
        session, close_needed = self._get_session(db)
        try:
            apps = session.query(ApplicationRecord).filter(
                ApplicationRecord.job_posting_id == job_posting_id
            ).all()
            return [a.to_dict() for a in apps]
        finally:
            if close_needed:
                session.close()

    def get_by_user_id(self, user_id: int, db: Optional[Any] = None) -> List[dict]:
        session, close_needed = self._get_session(db)
        try:
            apps = session.query(ApplicationRecord).filter(
                ApplicationRecord.user_id == user_id
            ).all()
            return [a.to_dict() for a in apps]
        finally:
            if close_needed:
                session.close()

    def get_all(self, db: Optional[Any] = None) -> List[dict]:
        """Returns all applications in the system."""
        session, close_needed = self._get_session(db)
        try:
            apps = session.query(ApplicationRecord).order_by(ApplicationRecord.id.asc()).all()
            return [a.to_dict() for a in apps]
        finally:
            if close_needed:
                session.close()

    def get_by_id(self, application_id: int, db: Optional[Any] = None) -> Optional[dict]:
        """Returns a single application by ID."""
        session, close_needed = self._get_session(db)
        try:
            app = session.query(ApplicationRecord).filter(ApplicationRecord.id == application_id).first()
            return app.to_dict() if app else None
        finally:
            if close_needed:
                session.close()

    def get_applicants_by_job_id(self, job_posting_id: int, db: Optional[Any] = None) -> List[dict]:
        """
        Returns the list of User objects (applicants) who applied to job_posting_id.
        (Week 06: 'the two lists of applicants and applications')
        """
        session, close_needed = self._get_session(db)
        try:
            job = session.query(JobPostingRecord).filter(JobPostingRecord.id == job_posting_id).first()
            if not job:
                raise KeyError(f"Job posting with ID {job_posting_id} not found")
            return [applicant.to_dict() for applicant in job.applicants]
        finally:
            if close_needed:
                session.close()

    def update_status(self, application_id: int, new_status: str, db: Optional[Any] = None) -> Optional[dict]:
        """Updates the status of an application (e.g. applied -> interview -> accepted)."""
        session, close_needed = self._get_session(db)
        try:
            app = session.query(ApplicationRecord).filter(ApplicationRecord.id == application_id).first()
            if not app:
                return None
            app.status = new_status
            session.commit()
            session.refresh(app)
            return app.to_dict()
        finally:
            if close_needed:
                session.close()

    def delete(self, application_id: int, db: Optional[Any] = None) -> bool:
        """Withdraws or deletes an application."""
        session, close_needed = self._get_session(db)
        try:
            app = session.query(ApplicationRecord).filter(ApplicationRecord.id == application_id).first()
            if not app:
                return False
            session.delete(app)
            session.commit()
            return True
        finally:
            if close_needed:
                session.close()


# Singleton instances
user_model = UserModel()
job_model = JobPostingModel()
application_model = ApplicationModel()
