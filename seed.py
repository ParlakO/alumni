"""
Database Seeder Script (Week 5 & 6: Factory & Seeder)
Populates the SQLite database with realistic alumni, job postings, and applications.

Usage:
    python seed.py               # Adds 50 alumni, 15 job postings, and 25 applications
    python seed.py --count 100   # Scales number of records
    python seed.py --reset       # Clears existing data and seeds fresh records
"""

import sys
import argparse
from sqlalchemy import func
from app.database import (
    SessionLocal,
    UserRecord,
    JobPostingRecord,
    ApplicationRecord,
    Base,
    engine
)
from app.factory import UserFactory, JobPostingFactory, ApplicationFactory


def seed_database_all(
    users_count: int = 50,
    jobs_count: int = 15,
    apps_count: int = 25,
    reset: bool = False
) -> dict:
    """
    Seeds users, job_postings, and applications in foreign key order.
    Can be run multiple times safely.
    """
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        if reset:
            print("[INFO] Resetting database in proper foreign key dependency order...")
            # 1. Delete applications first
            db.query(ApplicationRecord).delete()
            # 2. Delete job_postings second
            db.query(JobPostingRecord).delete()
            # 3. Delete users third
            db.query(UserRecord).delete()
            db.commit()

        # --- 1. Seed Users ---
        max_user_id = db.query(func.max(UserRecord.id)).scalar() or 0
        start_user_id = max_user_id + 1

        print(f"[SEED] Generating {users_count} alumni (Starting from ID #{start_user_id})...")
        user_data = UserFactory.create_batch(count=users_count, start_id=start_user_id)
        user_objects = [
            UserRecord(
                id=u["id"],
                name=u["name"],
                email=u["email"],
                department=u["department"]
            )
            for u in user_data
        ]
        db.add_all(user_objects)
        db.commit()

        # Collect all active user IDs
        all_user_ids = [u.id for u in db.query(UserRecord.id).all()]

        # --- 2. Seed Job Postings ---
        max_job_id = db.query(func.max(JobPostingRecord.id)).scalar() or 0
        start_job_id = max_job_id + 1

        print(f"[SEED] Generating {jobs_count} job postings (Starting from ID #{start_job_id})...")
        job_data = JobPostingFactory.create_batch(
            user_ids=all_user_ids,
            count=jobs_count,
            start_id=start_job_id
        )
        job_objects = [
            JobPostingRecord(
                id=j["id"],
                user_id=j["user_id"],
                title=j["title"],
                company=j["company"]
            )
            for j in job_data
        ]
        db.add_all(job_objects)
        db.commit()

        # Collect all active job IDs
        all_job_ids = [j.id for j in db.query(JobPostingRecord.id).all()]

        # --- 3. Seed Applications ---
        max_app_id = db.query(func.max(ApplicationRecord.id)).scalar() or 0
        start_app_id = max_app_id + 1

        print(f"[SEED] Generating {apps_count} unique applications (Starting from ID #{start_app_id})...")
        app_data = ApplicationFactory.create_batch(
            user_ids=all_user_ids,
            job_ids=all_job_ids,
            count=apps_count,
            start_id=start_app_id
        )
        app_objects = [
            ApplicationRecord(
                id=a["id"],
                user_id=a["user_id"],
                job_posting_id=a["job_posting_id"],
                status=a["status"]
            )
            for a in app_data
        ]
        db.add_all(app_objects)
        db.commit()

        totals = {
            "users": db.query(UserRecord).count(),
            "jobs": db.query(JobPostingRecord).count(),
            "applications": db.query(ApplicationRecord).count()
        }
        print(f"[SUCCESS] Database seeding complete! Totals: {totals}")
        return totals


# Backward-compatible alias for existing callers
def seed_users(count: int = 50, reset: bool = False) -> int:
    result = seed_database_all(users_count=count, jobs_count=count // 3, apps_count=count // 2, reset=reset)
    return result["users"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Alumni Tracking System Database Seeder")
    parser.add_argument("--count", type=int, default=50, help="Number of alumni records to seed (default: 50)")
    parser.add_argument("--reset", action="store_true", help="Clear existing records before seeding")

    args = parser.parse_args()
    seed_database_all(users_count=args.count, reset=args.reset)
