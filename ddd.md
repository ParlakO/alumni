# 📊 Veri Tasarımı Dokümantasyonu (Data Design Documentation - DDD)

Bu doküman, **Üniversite Mezun Takip Sistemi (Alumni Tracking System)** uygulamasının veri mimarisini, varlık şemalarını (`users`, `job_postings`, `applications`), veri ilişkilerini (One-to-Many, Many-to-Many), Pydantic veri modellerini, nested route tasarımlarını, silme kurallarını (Cascade vs Restrict) ve yaşam döngüsünü detaylandıran resmi veri tasarım dokümantasyonudur (Data Design Document - DDD).

> **📌 Tasarım İlkesi (Design First, Then The Code):**
> Geliştirme süreci her zaman dokümantasyon ve veri tasarımı ile başlar:
> `ddd.md` ➔ `migration` ➔ `models` ➔ `nested routes` ➔ `include` ➔ `applications`

---

## 📑 İçindekiler
- [1. Veri Mimarisi Özeti](#1-veri-mimarisi-özeti)
- [2. Varlık ve Alan Tanımları (Entity Schema)](#2-varlık-ve-alan-tanımları-entity-schema)
  - [2.1. `users` Tablosu (Mezun Varlığı)](#21-users-tablosu-mezun-varlığı)
  - [2.2. `job_postings` Tablosu (İş İlanları Varlığı)](#22-job_postings-tablosu-iş-ilanları-varlığı)
  - [2.3. `applications` Tablosu (İş Başvuruları - Ara Bağlantı Tablosu)](#23-applications-tablosu-iş-başvuruları---ara-bağlantı-tablosu)
  - [2.4. Varlık İlişkileri ve Kardinalite (ER Modeli)](#24-varlık-ilişkileri-ve-kardinalite-er-modeli)
  - [2.5. Yabancı Anahtar Silme Politikası (Cascade vs Restrict Kararı)](#25-yabancı-anahtar-silme-politikası-cascade-vs-restrict-kararı)
- [3. Pydantic Şemaları ve Veri Transfer Nesneleri (DTO)](#3-pydantic-şemaları-ve-veri-transfer-nesneleri-dto)
  - [3.1 - 3.5. `User` Şemaları](#31---35-user-şemaları)
  - [3.6. `JobPosting` Şemaları](#36-jobposting-şemaları)
  - [3.7. `Application` Şemaları](#37-application-şemaları)
  - [3.8. `UserWithJobsResponse` (Include / Nested DTO)](#38-userwithjobsresponse-include--nested-dto)
- [4. Bellek İçi Veri Depolama (In-Memory Storage)](#4-bellek-içi-veri-depolama-in-memory-storage)
- [5. CRUD, Nested Route ve Doğrulama İş Kuralları](#5-crud-nested-route-ve-doğrulama-iş-kuralları)
  - [5.1 - 5.6. Temel CRUD Kuralları](#51---56-temel-crud-kuralları)
  - [5.7. Nested Route Kuralı: `POST /api/users/:id/jobs`](#57-nested-route-kuralı-post-apiusersidjobs)
  - [5.8. Include / Birleşik Sorgulama Kuralı: `GET /api/users/:id`](#58-include--birleşik-sorgulama-kuralı-get-apiusersid)
  - [5.9. Çoktan-Çoka Başvuru ve Mükerrerlik Kuralı: `POST /api/jobs/:id/applications`](#59-çoktan-çoka-başvuru-ve-mükerrerlik-kuralı-post-apijobsidapplications)
- [6. Konteyner Yaşam Döngüsü ve "Forgetting Test" (Statelessness)](#6-konteyner-yaşam-döngüsü-ve-forgetting-test-statelessness)
- [7. Veritabanı Göçü ve SQLAlchemy Modelleri](#7-veritabanı-göçü-ve-sqlalchemy-modelleri)
  - [7.1. SQLAlchemy ORM Modelleri](#71-sqlalchemy-orm-modelleri)
  - [7.2. Alembic Migrasyon Stratejisi ("A new file — never edit the old one")](#72-alembic-migrasyon-stratejisi-a-new-file--never-edit-the-old-one)
- [8. Veri Üretim Fabrikası ve Tohumlama (Factory & Seeder Pattern)](#8-veri-üretim-fabrikası-ve-tohumlama-factory--seeder-pattern)

---

## 1. Veri Mimarisi Özeti

Proje, **MVC (Model-View-Controller)** mimarisinin Model katmanını saf Python nesneleri, **Pydantic v2** veri şemaları ve kalıcı **SQLAlchemy ORM + SQLite** altyapısıyla yönetecek şekilde tasarlanmıştır.

- **Kaynak Dosyalar:** [`app/models.py`](app/models.py), [`app/database.py`](app/database.py)
- **Temel Varlıklar:** `users`, `job_postings`, `applications`
- **İlişki Türleri:** 
  - `users` ➔ `job_postings` (1:N - One-to-Many: Bir mezun birden çok iş ilanı açabilir)
  - `users` ➔ `applications` ➔ `job_postings` (N:M - Many-to-Many: Mezunlar ilanlara başvurabilir)

```
                  ┌──────────────────────────────────────────────┐
                  │                 HTTP Request                 │
                  └───────────────────────┬──────────────────────┘
                                          │
                                          ▼
                  ┌──────────────────────────────────────────────┐
                  │        Pydantic DTO (Validation Layer)       │
                  │   UserCreate / JobPostingCreate / AppCreate  │
                  └───────────────────────┬──────────────────────┘
                                          │ Validated Data
                                          ▼
                  ┌──────────────────────────────────────────────┐
                  │          Model Layer (Business Logic)        │
                  │  - User Varlık Kontrolü (404 Denetimi)       │
                  │  - Unique Constraint Denetimi (409 Conflict) │
                  │  - Eager Loading / Include (LEFT JOIN)       │
                  └───────────────────────┬──────────────────────┘
                                          │
                                          ▼
                  ┌──────────────────────────────────────────────┐
                  │         SQLAlchemy ORM / SQLite DB           │
                  │   users  ◄──(1:N)──  job_postings            │
                  │     ▲                      ▲                 │
                  │     └────(N:M via apps)────┘                 │
                  └──────────────────────────────────────────────┘
```

---

## 2. Varlık ve Alan Tanımları (Entity Schema)

Sistemde birbiriyle ilişkili 3 temel tablo yer alır:

### 2.1. `users` Tablosu (Mezun Varlığı)
Sisteme kayıtlı mezunları temsil eder.

| Alan Adı (Field) | Veri Tipi | Zorunlu mu? | Anahtar | Örnek Değer | Açıklama |
|:---|:---|:---:|:---:|:---|:---|
| **`id`** | `Integer` | Evet | **PK** | `1` | Kullanıcının benzersiz kimlik numarası (Primary Key). |
| **`name`** | `String` | Evet | - | `"Ada"` | Mezunun ad ve soyadı. |
| **`email`** | `String` | Evet | `Unique` | `"ada@iu.edu.tr"` | Mezunun iletişim e-posta adresi. |
| **`department`** | `String` | Evet | - | `"Computer Engineering"` | Mezun olunan üniversite bölümü. |

**Örnek Veri Seti:**
| id | name | email | department |
|:---:|:---|:---|:---|
| 1 | Ada | `ada@iu.edu.tr` | Computer Engineering |
| 2 | Can | `can@iu.edu.tr` | MIS |
| 3 | Elif | `elif@iu.edu.tr` | Data Science |

---

### 2.2. `job_postings` Tablosu (İş İlanları Varlığı)
Mezunlar tarafından paylaşılan iş ilanlarını temsil eder. Bir ilanı mutlaka bir kullanıcı yayınlar.

| Alan Adı (Field) | Veri Tipi | Zorunlu mu? | Anahtar | Örnek Değer | Açıklama |
|:---|:---|:---:|:---:|:---|:---|
| **`id`** | `Integer` | Evet | **PK** | `10` | İlanın benzersiz kimlik numarası. |
| **`user_id`** | `Integer` | Evet | **FK** | `1` | İlanı oluşturan mezunun kimliği (`users.id` referansı). |
| **`title`** | `String` | Evet | - | `"Backend Intern"` | İlan pozisyon başlığı. |
| **`company`** | `String` | Evet | - | `"Acme"` | İlanı açan şirket/kurum adı. |

**Kural:**
- `one user ➔ many postings`: Bir kullanıcı birden fazla iş ilanı oluşturabilir.
- `each posting ➔ exactly one user`: Her ilanın tam olarak bir sahibi vardır.
- `user_id` yabancı anahtardır (`FK ➔ users.id`).

**Örnek Veri Seti:**
| id | user_id | title | company |
|:---:|:---:|:---|:---|
| 10 | 1 | Backend Intern | Acme |
| 11 | 1 | Data Analyst | Acme |
| 12 | 2 | QA Tester | TechCorp |
| 13 | 1 | Junior Developer | Acme |

---

### 2.3. `applications` Tablosu (İş Başvuruları - Ara Bağlantı Tablosu)
Kullanıcılar ile iş ilanları arasındaki çoktan-çoka (Many-to-Many) ilişkiyi sağlayan ara tablodur (join table).

| Alan Adı (Field) | Veri Tipi | Zorunlu mu? | Anahtar / Kısıtlama | Örnek Değer | Açıklama |
|:---|:---|:---:|:---:|:---|:---|
| **`id`** | `Integer` | Evet | **PK** | `1` | Başvurunun benzersiz kimlik numarası. |
| **`user_id`** | `Integer` | Evet | **FK** | `3` | Başvuran mezunun kimliği (`users.id` referansı). |
| **`job_posting_id`**| `Integer` | Evet | **FK** | `10` | Başvurulan ilanın kimliği (`job_postings.id` referansı). |
| **`status`** | `String` | Evet | - | `"applied"` | Başvuru durumu (`applied`, `interview`, `accepted`, `rejected`). |

**Bileşik Kısıtlama (Composite Unique Constraint):**
- `UNIQUE (user_id, job_posting_id)`
- **Amaç:** Bir mezunun aynı ilana ikinci kez başvurmasını engellemek. Aynı kombinasyon tekrar eklenmek istendiğinde sistem **`409 Conflict`** döndürür.

**Örnek Veri Seti:**
| id | user_id | job_posting_id | status | Açıklama |
|:---:|:---:|:---:|:---:|:---|
| 1 | 3 | 10 | `applied` | Elif (3), 10 numaralı ilana başvurdu. |
| 2 | 2 | 10 | `applied` | Can (2), 10 numaralı ilana başvurdu (10 no'lu ilanda 2 başvuran var). |
| 3 | 3 | 12 | `interview`| Elif (3), 12 numaralı ilana başvurdu. |

---

### 2.4. Varlık İlişkileri ve Kardinalite (ER Modeli)

```
       ┌────────────────────────┐
       │         users          │
       │────────────────────────│
       │ PK  id                 │◄────────┐
       │     name               │         │
       │     email              │         │
       │     department         │         │
       └───────────┬────────────┘         │
                   │ 1                    │
                   │                      │
                   │ N                    │
       ┌───────────▼────────────┐         │
       │      job_postings      │         │
       │────────────────────────│         │
       │ PK  id                 │◄──┐     │
       │ FK  user_id ───────────┘   │     │
       │     title                  │     │
       │     company                │     │
       └───────────┬────────────┘   │     │
                   │ 1              │     │
                   │                │     │
                   │ N              │     │
       ┌───────────▼────────────┐   │     │
       │      applications      │   │     │
       │────────────────────────│   │     │
       │ PK  id                 │   │     │
       │ FK  user_id ───────────┼───┼─────┘
       │ FK  job_posting_id ────┼───┘
       │     status             │
       │ UNIQUE(user, posting)  │
       └────────────────────────┘
```

1. **One-to-Many (1:N):** `users` ➔ `job_postings`
   - Bir mezun birden çok ilan açabilir (`hasMany`).
   - Her ilan bir mezuna aittir (`belongsTo`).
2. **Many-to-Many (N:M):** `users` ➔ `job_postings` (via `applications`)
   - Bir mezun birden çok ilana başvurabilir.
   - Bir ilana birden çok mezun başvurabilir.

---

### 2.5. Yabancı Anahtar Silme Politikası (Cascade vs Restrict Kararı)

> **Karar Noktası (Decision Point):** *"deleting a user who has postings: cascade or restrict — you decide, in ddd.md"*

İlanı bulunan bir kullanıcı (`users`) silinmek istendiğinde sistemin sergileyeceği davranış:

| Strateji | Davranış | Avantajı | Dezavantajı |
|:---|:---|:---|:---|
| **`CASCADE`** | Kullanıcı silindiğinde, açtığı tüm `job_postings` ve bunlara bağlı `applications` otomatik silinir. | Yetim (orphaned) kayıt bırakmaz, temizlik otomatiktir. | İlana başvurmuş diğer mezunların başvuru geçmişi kaybolabilir; kazara veri kaybı riski yüksektir. |
| **`RESTRICT`** *(Önerilen / Varsayılan)* | Aktif ilanı bulunan bir kullanıcının silinmesine veritabanı seviyesinde izin verilmez (`Foreign Key Constraint Failure`). | İlanların ve başvuru süreçlerinin bütünlüğünü korur; yanlışlıkla veri silinmesini engeller. | Kullanıcı silinmeden önce ilanlarının manuel silinmesini veya devredilmesini gerektirir. |

**Mimari Kararımız:**
- `job_postings.user_id` için **`RESTRICT`** (veya `NO ACTION`) kuralı benimsenmiştir. Aktif ilanı olan mezun silinmeye çalışıldığında API `400 Bad Request` veya `409 Conflict` ("Kullanıcıya ait aktif iş ilanları bulunduğundan silinemez") yanıtı döner.
- `applications.user_id` ve `applications.job_posting_id` için ise bir ilan meşru olarak silindiğinde ilgili başvuruların temizlenmesi amacıyla **`CASCADE`** uygulanabilir.

---

## 3. Pydantic Şemaları ve Veri Transfer Nesneleri (DTO)

### 3.1 - 3.5. `User` Şemaları
[`app/models.py`](app/models.py) dosyasında tanımlı temel mezun şemalarıdır:
- `UserBase`, `UserCreate`, `UserUpdate`, `UserPatch`, `User`

### 3.6. `JobPosting` Şemaları
İlan oluşturma ve yanıt süreçlerini yönetir:

```python
class JobPostingBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=150, example="Junior Developer")
    company: str = Field(..., min_length=2, max_length=100, example="Acme")

class JobPostingCreate(JobPostingBase):
    """
    POST /api/users/:id/jobs için istek gövdesi.
    user_id gövdede yer ALMAZ, URL parametresinden (:id) alınır.
    """
    pass

class JobPostingResponse(JobPostingBase):
    """İstemciye dönülen ilan modeli."""
    id: int
    user_id: int
```

### 3.7. `Application` Şemaları
İş başvuruları için DTO tanımları:

```python
class ApplicationCreate(BaseModel):
    """
    POST /api/jobs/:id/applications için istek gövdesi.
    job_posting_id URL parametresinden (:id) alınır.
    """
    userId: int = Field(..., description="Başvuruyu yapan mezunun user_id değeri")

class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    job_posting_id: int
    status: str = Field(default="applied")
```

### 3.8. `UserWithJobsResponse` (Include / Nested DTO)
`GET /api/users/:id` ile kullanıcının kendi ilanlarıyla birlikte tek seferde dönülmesi şeması:

```python
class UserWithJobsResponse(BaseModel):
    id: int
    name: str
    email: str
    department: Optional[str] = None
    jobs: List[JobPostingResponse] = []
```

---

## 4. Bellek İçi Veri Depolama (In-Memory Storage)

İlk geliştirme aşamasında bellek içi testler için başlangıç tohum verileri aşağıdaki yapıda tutulur:

```python
self._users: List[dict] = [
    {"id": 1, "name": "Ada", "email": "ada@iu.edu.tr", "department": "Computer Engineering"},
    {"id": 2, "name": "Can", "email": "can@iu.edu.tr", "department": "MIS"},
    {"id": 3, "name": "Elif", "email": "elif@iu.edu.tr", "department": "Data Science"}
]

self._job_postings: List[dict] = [
    {"id": 10, "user_id": 1, "title": "Backend Intern", "company": "Acme"},
    {"id": 11, "user_id": 1, "title": "Data Analyst", "company": "Acme"},
    {"id": 12, "user_id": 2, "title": "QA Tester", "company": "TechCorp"},
    {"id": 13, "user_id": 1, "title": "Junior Developer", "company": "Acme"}
]

self._applications: List[dict] = [
    {"id": 1, "user_id": 3, "job_posting_id": 10, "status": "applied"},
    {"id": 2, "user_id": 2, "job_posting_id": 10, "status": "applied"},
    {"id": 3, "user_id": 3, "job_posting_id": 12, "status": "interview"}
]
```

---

## 5. CRUD, Nested Route ve Doğrulama İş Kuralları

### 5.1 - 5.6. Temel CRUD Kuralları
- ID çakışma denetimi (`400 Bad Request`)
- Bulunamayan kayıtlar için `404 Not Found`
- Başarılı oluşturma (`201 Created`), silme (`204 No Content`)

---

### 5.7. Nested Route Kuralı: `POST /api/users/:id/jobs`
> **Kural (Whose Posting? The URL Says):** İlanın kime ait olduğunu URL yolu belirler.

```
POST /api/users/:id/jobs ──► Controller ──► Model (User.exists(:id)?)
                                                 │
                                                 ├──► [HAYIR] ──► 404 User Not Found
                                                 │
                                                 └──► [EVET]  ──► INSERT INTO job_postings
                                                                  (user_id, title, company)
                                                                  VALUES (:id, ...)
                                                                  ──► 201 Created
```

1. **Path Parametresi:** `:id` (örn: `/api/users/1/jobs` ➔ `user_id = 1`).
2. **Body:** Yalnızca `{ "title": "Junior Developer", "company": "Acme" }` gönderilir. Body kesinlikle `user_id` içermez.
3. **Validasyon:**
   - Model katmanı kullanıcının veritabanında var olup olmadığını sorgular (`exists_by_id(user_id)`).
   - Kullanıcı yoksa derhal **`404 Not Found`** ("User not found") fırlatılır.
   - Kullanıcı varsa `job_postings` tablosuna `user_id` ile yeni kayıt eklenir ve **`201 Created`** yanıtı ile oluşturulan kayıt döndürülür.

---

### 5.8. Include / Birleşik Sorgulama Kuralı: `GET /api/users/:id`
> **Kural (One Answer, Two Tables):** Tek bir sorguyla hem kullanıcı bilgisi hem de kullanıcının açtığı iş ilanları döner.

- **Sorgu:** `GET /api/users/1`
- **ORM / Pseudo-Code:** `User.find(1, { include: 'jobs' })`
- **Üretilen SQL:**
  ```sql
  SELECT users.id, users.name, users.email,
         job_postings.id AS job_id, job_postings.title, job_postings.company
  FROM users
  LEFT JOIN job_postings
    ON job_postings.user_id = users.id
  WHERE users.id = 1;
  ```
- **İstemciye Dönen JSON Çıktısı:**
  ```json
  {
    "id": 1,
    "name": "Ada",
    "jobs": [
      { "id": 10, "title": "Backend Intern", "company": "Acme" },
      { "id": 11, "title": "Data Analyst", "company": "Acme" },
      { "id": 13, "title": "Junior Developer", "company": "Acme" }
    ]
  }
  ```

---

### 5.9. Çoktan-Çoka Başvuru ve Mükerrerlik Kuralı: `POST /api/jobs/:id/applications`
> **Kural (Unique Applications & 409 Conflict):** Bir mezun aynı ilana yalnızca 1 kez başvurabilir.

- **İstek:** `POST /api/jobs/12/applications`
- **Gövde:** `{ "userId": 1 }`
- **İş Akışı:**
  1. İlanın (`job_posting_id = 12`) ve kullanıcının (`user_id = 1`) varlığı kontrol edilir (Yoksa `404 Not Found`).
  2. `applications` tablosunda `(user_id=1, job_posting_id=12)` kaydı aranır.
  3. **Mükerrerlik Denetimi:** Eğer kayıt zaten varsa veritabanı benzersizlik kısıtlaması (`UNIQUE (user_id, job_posting_id)`) devreye girer ve istemciye **`409 Conflict`** ("User has already applied to this job posting") yanıtı iletilir.
  4. İlk başvuru ise kayıt eklenir ve **`201 Created`** durumuyla başvuru bilgisi döndürülür.

---

### 5.10. İki Liste Prensibi: Başvurular (`applications`) vs. Başvuranlar (`applicants`)
> **Kural (The Two Lists):** Bir ilana kimlerin başvurduğunu sorgularken iki farklı görünüm ihtiyacı vardır:
1. **Başvuru Kayıtları Listesi (`GET /api/jobs/:id/applications`):**
   - Ara tablodaki ilişkisel veriyi döner (`id`, `user_id`, `job_posting_id`, `status`).
   - Örnek: `[{ "id": 1, "user_id": 3, "job_posting_id": 10, "status": "applied" }]`
2. **Başvuran Kullanıcılar Listesi (`GET /api/jobs/:id/applicants`):**
   - İlana başvuran gerçek mezun kullanıcı profillerini (`User` nesneleri) döner.
   - Örnek: `[{ "id": 3, "name": "Elif", "email": "elif@iu.edu.tr", "department": "Data Science" }]`

---

### 5.11. Doğrudan Başvuru Yönetimi (Direct Application CRUD)
- **`GET /api/applications`:** Sistemdeki tüm başvuruları listeler.
- **`GET /api/applications/:id`:** Belirli bir başvurunun detayını getirir.
- **`PATCH /api/applications/:id`:** Başvuru durumunu günceller (`applied` ➔ `interview` ➔ `accepted` / `rejected`).
- **`DELETE /api/applications/:id`:** Mezunun başvurusunu geri çekmesini sağlar (`204 No Content`).

---

## 6. Konteyner Yaşam Döngüsü ve "Forgetting Test" (Statelessness)

- Bellek içi modda çalışırken konteyner her yeniden başlatıldığında (`docker compose down && docker compose up`) veriler sıfırlanarak tohum verilerine döner.
- Kalıcı SQLite veritabanı ve Docker Volume ile veriler kalıcı hale getirilir.

---

## 7. Veritabanı Göçü ve SQLAlchemy Modelleri

### 7.1. SQLAlchemy ORM Modelleri ([`app/database.py`](app/database.py))

```python
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class UserRecord(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    department = Column(String(100), nullable=False)

    # 1:N İlişki - Bir kullanıcının birden çok ilanı olur
    jobs = relationship("JobPostingRecord", back_populates="owner", cascade="all, delete-orphan")
    # N:M İlişki - Başvurular
    applications = relationship("ApplicationRecord", back_populates="applicant")


class JobPostingRecord(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    title = Column(String(150), nullable=False)
    company = Column(String(100), nullable=False)

    owner = relationship("UserRecord", back_populates="jobs")
    applications = relationship("ApplicationRecord", back_populates="job_posting", cascade="all, delete-orphan")


class ApplicationRecord(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False, default="applied")

    __table_args__ = (
        UniqueConstraint("user_id", "job_posting_id", name="uq_user_job_application"),
    )

    applicant = relationship("UserRecord", back_populates="applications")
    job_posting = relationship("JobPostingRecord", back_populates="applications")
```

---

### 7.2. Alembic Migrasyon Stratejisi ("A new file — never edit the old one")

> **Altın Kural:** Mevcut migrasyon dosyası (`alembic/versions/*_create_users_table.py`) kesinlikle **DÜZENLENMEZ**. Veritabanı evrimi her zaman geriye dönük izlenebilir yeni bir migrasyon dosyası ile yapılır.

```bash
# 1. Yeni migrasyon revizyonu üret
alembic revision -m "create job_postings and applications tables"

# 2. Şemayı veritabanına uygula
alembic upgrade head
```

---

## 8. Veri Üretim Fabrikası ve Tohumlama (Factory & Seeder Pattern)

- [`app/factory.py`](app/factory.py) genişletilerek `JobPostingFactory` ve `ApplicationFactory` entegre edilebilir.
- [`seed.py`](seed.py) çalıştırıldığında örnek olarak Ada, Can ve Elif kullanıcıları ile birlikte görseldeki 4 iş ilanı ve 3 iş başvurusu otomatik olarak tohumlanabilir.
