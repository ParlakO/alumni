"""
Database Seeder Script (Week 5: Factory & Seeder)
Populates the SQLite database with realistic alumni records using UserFactory.

Usage:
    python seed.py               # Adds 50 realistic alumni records
    python seed.py --count 100   # Adds 100 realistic alumni records
    python seed.py --reset       # Clears existing data and seeds fresh 50 records
"""

import sys
import argparse
from sqlalchemy import func
from app.database import SessionLocal, UserRecord, Base, engine
from app.factory import UserFactory


def seed_users(count: int = 50, reset: bool = False) -> int:
    """
    Seeds the database with `count` alumni records.
    """
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        if reset:
            print("[INFO] Resetting existing user records...")
            db.query(UserRecord).delete()
            db.commit()

        # Check existing max ID
        max_id = db.query(func.max(UserRecord.id)).scalar() or 0
        start_id = max_id + 1

        print(f"[SEED] Generating {count} alumni records using UserFactory (Starting from ID #{start_id})...")
        batch_data = UserFactory.create_batch(count=count, start_id=start_id)

        user_objects = [
            UserRecord(
                id=item["id"],
                name=item["name"],
                email=item["email"],
                department=item["department"]
            )
            for item in batch_data
        ]

        db.add_all(user_objects)
        db.commit()

        total = db.query(UserRecord).count()
        print(f"[SUCCESS] Successfully seeded {count} alumni! Total records in database: {total}")
        return total


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Alumni Tracking System Database Seeder")
    parser.add_argument("--count", type=int, default=50, help="Number of alumni records to seed (default: 50)")
    parser.add_argument("--reset", action="store_true", help="Clear existing records before seeding")

    args = parser.parse_args()
    seed_users(count=args.count, reset=args.reset)
