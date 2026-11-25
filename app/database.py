import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Database URL: default to SQLite in the project directory
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./alumni.db")

# SQLite needs connect_args={"check_same_thread": False} for multi-threaded FastAPI
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UserRecord(Base):
    """
    SQLAlchemy ORM Model representing the 'users' database table.
    Has a 1:N relationship with JobPostingRecord (hasMany).
    Has a N:M relationship with JobPostingRecord via ApplicationRecord (many-to-many).
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    department = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False, default="")
    role = Column(String(30), nullable=False, default="graduate")

    # 1:N Relationship (one user -> many job postings)
    jobs = relationship("JobPostingRecord", back_populates="owner", cascade="all, delete-orphan")

    # N:M Relationship via applications join table
    applications = relationship("ApplicationRecord", back_populates="applicant", cascade="all, delete-orphan")
    applied_jobs = relationship("JobPostingRecord", secondary="applications", back_populates="applicants", viewonly=True)

    def to_dict(self, include_jobs: bool = False) -> dict:
        """Serializes user safely. NEVER includes password_hash."""
        data = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "department": self.department,
            "role": self.role or "graduate"
        }
        if include_jobs and self.jobs is not None:
            data["jobs"] = [job.to_dict() for job in self.jobs]
        return data


class JobPostingRecord(Base):
    """
    SQLAlchemy ORM Model representing the 'job_postings' database table.
    Belongs to a single UserRecord (belongsTo) with foreign key user_id.
    """
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    title = Column(String(120), nullable=False)
    company = Column(String(100), nullable=False)
    city = Column(String(100), nullable=True)
    description = Column(String(500), nullable=True)

    # Relationships
    owner = relationship("UserRecord", back_populates="jobs")
    applications = relationship("ApplicationRecord", back_populates="job_posting", cascade="all, delete-orphan")
    applicants = relationship("UserRecord", secondary="applications", back_populates="applied_jobs", viewonly=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "company": self.company,
            "city": self.city,
            "description": self.description
        }


class ApplicationRecord(Base):
    """
    SQLAlchemy ORM Model representing the 'applications' join table.
    Enforces N:M relationship between users and job_postings.
    Guarantees uniqueness via UNIQUE (user_id, job_posting_id).
    """
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="applied")

    __table_args__ = (
        UniqueConstraint("user_id", "job_posting_id", name="uq_user_job_application"),
    )

    # Relationships
    applicant = relationship("UserRecord", back_populates="applications")
    job_posting = relationship("JobPostingRecord", back_populates="applications")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "job_posting_id": self.job_posting_id,
            "status": self.status
        }


def get_db():
    """Dependency for providing a transactional database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_database():
    """Initializes tables and seeds default records (including admin & graduates with bcrypt passwords)."""
    from sqlalchemy import inspect, text
    from app.auth import hash_password

    Base.metadata.create_all(bind=engine)

    # Ensure legacy SQLite databases get new auth columns seamlessly if migration hasn't run yet
    inspector = inspect(engine)
    if "users" in inspector.get_table_names():
        existing_cols = {c["name"] for c in inspector.get_columns("users")}
        with engine.begin() as conn:
            if "password_hash" not in existing_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT ''"))
            if "role" not in existing_cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(30) NOT NULL DEFAULT 'graduate'"))

    with SessionLocal() as db:
        if db.query(UserRecord).count() == 0:
            seed_users = [
                UserRecord(
                    id=1,
                    name="Ada",
                    email="ada@iu.edu.tr",
                    department="Computer Engineering",
                    password_hash=hash_password("secret123"),
                    role="graduate",
                ),
                UserRecord(
                    id=2,
                    name="Can",
                    email="can@iu.edu.tr",
                    department="MIS",
                    password_hash=hash_password("secret123"),
                    role="graduate",
                ),
                UserRecord(
                    id=3,
                    name="Elif",
                    email="elif@iu.edu.tr",
                    department="Data Science",
                    password_hash=hash_password("secret123"),
                    role="graduate",
                ),
                UserRecord(
                    id=4,
                    name="Osman Parlak",
                    email="osman@iu.edu.tr",
                    department="Yönetim Bilişim Sistemleri",
                    password_hash=hash_password("admin123"),
                    role="admin",
                ),
            ]
            db.add_all(seed_users)
            db.commit()

            seed_jobs = [
                JobPostingRecord(id=10, user_id=1, title="Backend Intern", company="Acme", city="Istanbul", description="Backend developer intern"),
                JobPostingRecord(id=11, user_id=1, title="Data Analyst", company="Acme", city="Ankara", description="Data analysis and reporting"),
                JobPostingRecord(id=12, user_id=2, title="QA Tester", company="TechCorp", city="Izmir", description="Manual and automated testing"),
                JobPostingRecord(id=13, user_id=1, title="Junior Developer", company="Acme", city=None, description=None),
            ]
            db.add_all(seed_jobs)
            db.commit()

            seed_applications = [
                ApplicationRecord(id=1, user_id=3, job_posting_id=10, status="applied"),
                ApplicationRecord(id=2, user_id=2, job_posting_id=10, status="applied"),
                ApplicationRecord(id=3, user_id=3, job_posting_id=12, status="interview"),
            ]
            db.add_all(seed_applications)
            db.commit()
        else:
            # Backfill missing password hashes for pre-existing users & ensure an admin exists
            updated = False
            default_grad_hash = None
            for u in db.query(UserRecord).all():
                if not u.password_hash:
                    if default_grad_hash is None:
                        default_grad_hash = hash_password("secret123")
                    u.password_hash = default_grad_hash
                    updated = True
                if not u.role:
                    u.role = "graduate"
                    updated = True
            has_admin = db.query(UserRecord).filter(UserRecord.role == "admin").first() is not None
            if not has_admin:
                admin_user = db.query(UserRecord).filter(UserRecord.email == "osman@iu.edu.tr").first()
                if admin_user:
                    admin_user.role = "admin"
                    admin_user.password_hash = hash_password("admin123")
                else:
                    db.add(UserRecord(
                        name="Osman Parlak",
                        email="osman@iu.edu.tr",
                        department="Yönetim Bilişim Sistemleri",
                        password_hash=hash_password("admin123"),
                        role="admin",
                    ))
                updated = True
            if updated:
                db.commit()
