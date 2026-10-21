import random
from typing import List, Optional, Set, Tuple


class UserFactory:
    """
    Factory Pattern for generating realistic Alumni (User) data.
    Generates realistic names, email addresses, and university departments.
    """

    FIRST_NAMES = [
        "Osman", "Ahmet", "Mehmet", "Mustafa", "Ali", "Can", "Burak", "Emre", "Murat", "Serkan",
        "Tolga", "Kemal", "Barış", "Deniz", "Eren", "Onur", "Kaan", "Oğuz", "Umut", "Volkan",
        "Ayşe", "Fatma", "Zeynep", "Elif", "Merve", "Büşra", "Ece", "Selin", "Gizem", "İrem",
        "Gamze", "Ebru", "Derya", "Tuğba", "Pelin", "Damla", "Ezgi", "Berna", "Hilal", "Melis"
    ]

    LAST_NAMES = [
        "Parlak", "Yılmaz", "Kaya", "Demir", "Çelik", "Şahin", "Yıldız", "Yıldırım", "Öztürk", "Aydın",
        "Özdemir", "Arslan", "Doğan", "Kılıç", "Aslan", "Çetin", "Kara", "Koç", "Kurt", "Özkan",
        "Şimşek", "Polat", "Korkmaz", "Güneş", "Gül", "Yalçın", "Bulut", "Keskin", "Ünal", "Avcı"
    ]

    DEPARTMENTS = [
        "Yönetim Bilişim Sistemleri",
        "Bilgisayar Mühendisliği",
        "Yazılım Mühendisliği",
        "Endüstri Mühendisliği",
        "Elektrik-Elektronik Mühendisliği",
        "İşletme",
        "İktisat",
        "Hukuk",
        "İletişim Fakültesi",
        "Uluslararası İlişkiler",
        "Matematik",
        "İstatistik"
    ]

    EMAIL_DOMAINS = ["istanbul.edu.tr", "alumni.istanbul.edu.tr", "gmail.com", "outlook.com"]

    @classmethod
    def _slugify(cls, text: str) -> str:
        """Converts Turkish characters to ASCII for clean email generation."""
        mapping = {
            "ç": "c", "Ç": "c", "ğ": "g", "Ğ": "g", "ı": "i", "I": "i", "İ": "i",
            "ö": "o", "Ö": "o", "ş": "s", "Ş": "s", "ü": "u", "Ü": "u"
        }
        clean = text.lower()
        for k, v in mapping.items():
            clean = clean.replace(k, v)
        return clean.replace(" ", ".")

    @classmethod
    def create_fake_user(cls, user_id: Optional[int] = None) -> dict:
        """Generates a single fake alumni record as a dictionary."""
        first_name = random.choice(cls.FIRST_NAMES)
        last_name = random.choice(cls.LAST_NAMES)
        name = f"{first_name} {last_name}"

        slug = f"{cls._slugify(first_name)}.{cls._slugify(last_name)}"
        rand_num = random.randint(10, 999)
        domain = random.choice(cls.EMAIL_DOMAINS)
        email = f"{slug}{rand_num}@{domain}"

        department = random.choice(cls.DEPARTMENTS)

        data = {
            "name": name,
            "email": email,
            "department": department
        }
        if user_id is not None:
            data["id"] = user_id
        return data

    @classmethod
    def create_batch(cls, count: int = 50, start_id: Optional[int] = None) -> List[dict]:
        """Generates a batch of fake alumni records."""
        records = []
        for i in range(count):
            uid = (start_id + i) if start_id is not None else None
            records.append(cls.create_fake_user(user_id=uid))
        return records


class JobPostingFactory:
    """
    Factory Pattern for generating realistic Job Postings.
    Associates each posting with an owner alumni (user_id).
    """

    JOB_TITLES = [
        "Backend Intern",
        "Data Analyst",
        "Junior Developer",
        "QA Tester",
        "Full Stack Engineer",
        "Frontend Developer (React/Vue)",
        "DevOps Engineer",
        "Machine Learning Engineer",
        "Mobile App Developer",
        "Cybersecurity Analyst",
        "Cloud Solutions Architect",
        "Product Specialist"
    ]

    COMPANIES = [
        "Acme Corp",
        "TechCorp",
        "Trendyol",
        "Getir",
        "Google",
        "Microsoft",
        "Garanti BBVA",
        "Hepsiburada",
        "Aselsan",
        "Baykar",
        "Peak Games",
        "Amazon Web Services"
    ]

    @classmethod
    def create_fake_job(cls, user_id: int, job_id: Optional[int] = None) -> dict:
        """Generates a single fake job posting."""
        data = {
            "user_id": user_id,
            "title": random.choice(cls.JOB_TITLES),
            "company": random.choice(cls.COMPANIES)
        }
        if job_id is not None:
            data["id"] = job_id
        return data

    @classmethod
    def create_batch(cls, user_ids: List[int], count: int = 15, start_id: int = 10) -> List[dict]:
        """Generates a batch of job postings distributed among given user IDs."""
        if not user_ids:
            return []
        records = []
        for i in range(count):
            uid = random.choice(user_ids)
            records.append(cls.create_fake_job(user_id=uid, job_id=start_id + i))
        return records


class ApplicationFactory:
    """
    Factory Pattern for generating unique Job Applications.
    Guarantees UNIQUE(user_id, job_posting_id) composite constraint.
    """

    STATUSES = ["applied", "interview", "accepted", "rejected"]

    @classmethod
    def create_batch(
        cls,
        user_ids: List[int],
        job_ids: List[int],
        count: int = 25,
        start_id: int = 1
    ) -> List[dict]:
        """Generates unique applications between users and job postings."""
        if not user_ids or not job_ids:
            return []

        pairs: Set[Tuple[int, int]] = set()
        max_possible = len(user_ids) * len(job_ids)
        target_count = min(count, max_possible)

        while len(pairs) < target_count:
            u = random.choice(user_ids)
            j = random.choice(job_ids)
            pairs.add((u, j))

        records = []
        for idx, (u, j) in enumerate(pairs):
            records.append({
                "id": start_id + idx,
                "user_id": u,
                "job_posting_id": j,
                "status": random.choice(cls.STATUSES)
            })
        return records
