import random
from typing import List, Optional
from app.database import UserRecord


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
        """
        Generates a batch of fake alumni records.
        """
        records = []
        for i in range(count):
            uid = (start_id + i) if start_id is not None else None
            records.append(cls.create_fake_user(user_id=uid))
        return records
