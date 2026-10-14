import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

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
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    department = Column(String(100), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "department": self.department
        }


def get_db():
    """Dependency for providing a transactional database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_database():
    """Initializes tables and seeds default records if table is empty."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.query(UserRecord).count() == 0:
            seed_users = [
                UserRecord(id=1, name="Osman Parlak", email="osman@example.com", department="MIS"),
                UserRecord(id=2, name="Ahmet Yilmaz", email="ahmet@example.com", department="Computer Engineering")
            ]
            db.add_all(seed_users)
            db.commit()
