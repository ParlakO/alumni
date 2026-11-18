# 🎓 Üniversite Mezun Takip Sistemi (Alumni Tracking System API)

Bu proje, **İstanbul Üniversitesi Web Programlama (YBSB3001)** dersi kapsamında geliştirilmiş; **MVC (Model-View-Controller)** mimarisiyle yapılandırılmış, veritabanı bağlantısı gerektirmeyen bellek içi (In-Memory) **UserModel**, iki ayrı kontrolcü (**UserController** ve **ApiUserController**) ve **Docker** desteği sunan bir RESTful web uygulamasıdır.

---

> 📚 **Corporate Standards & Documentation:**
> - 🎨 **[Brand Identity Guidelines (brand.md)](#brand-md):** Corporate values, logo, typography & tone of voice ([`brand.md`](brand.md)).
> - 📐 **[Design System Specification (DESIGN.MD)](#design-md):** UI/UX design tokens & components compliant with `styles.refero.design` & `VoltAgent/awesome-design-md` ([`DESIGN.MD`](DESIGN.MD)).
> - 📊 **[Data Design Documentation (ddd.md)](ddd.md):** 1:N & N:M relational schemas, DTOs & RESTRICT policies.

---

## 📅 Haftalık Gelişim Adımları (Week Breakdown)

Proje, ders müfredatındaki 6 haftalık kazanımları açık ve modüler biçimde yansıtır:

| Week | Topic | Relevant Files & Functions | Description |
|:---|:---|:---|:---|
| **Week 1** | Basic Routing & Greetings | [`app/main.py`](app/main.py) | `GET /`, `GET /hello`, `GET /hello/:name`, `GET /sum/:a/:b`, `GET /about`, `GET /api/health` |
| **Week 2** | In-Memory Data Structures & Read Operations | [`app/models.py`](app/models.py) | In-Memory data list, `GET /api/users` (listing) and `GET /api/users/:id` |
| **Week 3** | Full CRUD Operations & Validation | [`app/models.py`](app/models.py) | POST (creation), PUT (full update), PATCH (partial update), DELETE, Pydantic validation & HTTP status codes (`201`, `204`, `400`, `404`) |
| **Week 4** | MVC Architecture, Dual Controllers & View Layer | [`app/controllers/`](app/controllers/), [`app/views/`](app/views/) | Standalone **UserModel** CRUD methods, **UserController** (`/users`), **ApiUserController** (`/api/users`), View layer: `GET /users` (listing) & `POST /users` (creation) HTML pages |
| **Week 5** | Database Migration & Persistent Storage | [`app/database.py`](app/database.py), [`alembic/`](alembic/) | SQLite database, SQLAlchemy ORM model (`UserRecord`), Alembic migrations (`upgrade head`) with schema versioning |
| **Week 6** | Relational Data & Advanced Routing | [`ddd.md`](ddd.md), [`alembic/`](alembic/), [`app/database.py`](app/database.py), [`app/models.py`](app/models.py), [`app/controllers/`](app/controllers/) | - **Relational Data:** `job_postings` (1:N One-to-Many / hasMany / belongsTo) and `applications` (N:M Many-to-Many Join Table, `UNIQUE(user_id, job_posting_id)` with `409 Conflict`).<br>- **New Migration:** *"A new file — never edit the old one"* rule.<br>- **Deletion Rule:** `RESTRICT` strategy (Active job posting prevents deleting user; `409 Conflict`).<br>- **Nested Routes:** `POST /api/users/:id/jobs` (owner from URL path, 404/201), `GET /api/users/:id/jobs`.<br>- **Include (Join):** `GET /api/users/:id?include=jobs` (`LEFT JOIN`).<br>- **Two Lists Principle:** `GET /api/jobs/:id/applications` vs `GET /api/jobs/:id/applicants`.<br>- **Seeding:** `JobPostingFactory` and `ApplicationFactory` (`seed.py`).<br>- **🏠 Homework:** *UI for Job Postings & Applications:* Interactive portal (`/static/index.html`). |
| **Middlewares & Guardians** | Logger, 404 Guardian, 5xx Guardian & Validation Rules | [`app/middleware.py`](app/middleware.py), [`app/logger.py`](app/logger.py), [`app/views/404.html`](app/views/404.html), [`logs/error.logs`](logs/error.logs) | - **Logger Middleware:** Live request logging in `time method route res type duration` format.<br>- **Validation Rules:** `title required` (max 120 chars), `company required`, optional `city` & `description`.<br>- **404 Guardian:** Reasoned 404 error responses & generic browser redirect (`/404`).<br>- **5xx Guardian:** System crash prevention & stack trace logging to `logs/error.logs`. |
| **Design & Brand** | Brand Guidelines & Design System Specification | [`brand.md`](brand.md), [`DESIGN.MD`](DESIGN.MD) | - **Brand Identity:** Mission, core values, typography, and tone of voice ([`brand.md`](brand.md)).<br>- **Design System:** Design tokens, glassmorphism, responsive grid & components compliant with `styles.refero.design` & `VoltAgent/awesome-design-md` ([`DESIGN.MD`](DESIGN.MD)). |


---

## 🌟 Key Features (Temel Özellikler)

- **🏛️ MVC Mimari Ayrımı:**
  - **Model:** Harici veritabanı bağlantısı olmaksızın CRUD operasyonlarını yöneten `UserModel` sınıfı ve Pydantic veri modelleri.
  - **View:** Jinja2 şablonu [`app/views/users/index.html`](file:///c:/Users/osman.parlak.ISTBTC/alumni/app/views/users/index.html) (`GET /users` listeleme + `POST /users` form), JSON API çıktıları ve Swagger UI (`/docs`).
  - **Controllers:** `/users` rotasını yöneten `UserController` ve `/api/users` rotasını yöneten `ApiUserController`.
- **⚡ Kapsamlı REST API:** 
  - Standart HTTP durum kodları (`200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `404 Not Found`, `422 Unprocessable Entity`).
- **🛡️ Veri Doğrulama ve Mükerrer Kayıt Denetimi:**
  - Manuel girilen ID mevcutsa `400 Bad Request ("User ID already exists")` yanıtı.
  - ID belirtilmezse otomatik artan ID ataması.
- **🔢 Sıralı Listeleme:** Kullanıcıların ID'ye göre sıralı (`ordered by ID`) listelenmesi.
- **📚 Etkileşimli Swagger Dokümantasyonu:** Uç noktaların kontrolcü ve haftalara göre gruplandığı Swagger UI (`/docs`).
- **🐳 Docker & Docker Compose Desteği:** `docker compose up --build` ile ortam bağımsız tek komutla çalıştırma.

---

## <a id="brand-md"></a>🎨 Brand Identity Guidelines (brand.md)

Corporate identity, brand voice, typography, and visual standards are documented in [`brand.md`](brand.md):
- **Brand Name:** AlumniTrack (Istanbul University Alumni Tracking System)
- **Mission & Values:** Transparent, relational, and modern bridge between academia and industry.
- **Typography & Colors:** Plus Jakarta Sans & JetBrains Mono, deep royal indigo (`#4f46e5`) and emerald growth (`#10b981`) palette.
- 🔗 **Full Guide:** [`brand.md`](brand.md)

---

## <a id="design-md"></a>📐 Design System Specification (DESIGN.MD)

Design language is fully structured in [`DESIGN.MD`](DESIGN.MD) adhering to [`styles.refero.design`](https://refero.design) and [`VoltAgent/awesome-design-md`](https://github.com/VoltAgent/awesome-design-md):
- **Design Philosophy:** Layered depth, sleek dark glassmorphism, developer-first technical clarity, and high information density.
- **Components:** Sticky navigation bar, hero showcase, 4-column live statistics grid, multi-entity tabs (Alumni / Jobs / Applications), interactive modals, and toast notification system.
- 🔗 **Full Specification:** [`DESIGN.MD`](DESIGN.MD)

---

## 🏗️ MVC (Model-View-Controller) Architecture

```
                                  ┌───────────────────────────┐
                                  │   İstemci / API Client    │
                                  └─────────────┬─────────────┘
                                                │ HTTP İstekleri
                                                ▼
              ┌───────────────────────────────────────────────────────────────────┐
              │                        CONTROLLER KATMANI                         │
              │  ┌──────────────────────────────┐ ┌─────────────────────────────┐ │
              │  │       UserController         │ │      ApiUserController      │ │
              │  │         (/users)             │ │         (/api/users)        │ │
              │  └──────────────┬───────────────┘ └──────────────┬──────────────┘ │
              └─────────────────┼────────────────────────────────┼────────────────┘
                                │                                │
                                └───────────────┬────────────────┘
                                                │ CRUD Fonksiyon Çağrıları
                                                ▼
                      ┌───────────────────────────────────────────────────┐
                      │                   MODEL KATMANI                   │
                      │               UserModel (No DB)                   │
                      │  - get_all(), get_by_id(), exists_by_id()         │
                      │  - create(), update(), patch(), delete()          │
                      │  - In-Memory _users Listesi & Pydantic Schemas    │
                      └─────────────────────────┬─────────────────────────┘
                                                │ Veri Yanıtı
                                                ▼
                      ┌───────────────────────────────────────────────────┐
                      │                    VIEW KATMANI                   │
                      │  - FastAPI JSON Serializer & HTTP Durum Kodları   │
                      │  - Swagger UI Dokümantasyonu (/docs)              │
                      └───────────────────────────────────────────────────┘
```

### 1. Model (Veritabanı Bağlantısız `UserModel`)
- **Dosya:** [`app/models.py`](file:///c:/Users/osman.parlak.ISTBTC/alumni/app/models.py)
- **Detaylı Veri Tasarımı Dokümanı:** 📊 [Data Design Documentation (ddd.md)](ddd.md) (Şemalar, kısıtlamalar, veri yaşam döngüsü ve unutma testi)
- **Açıklama:** Harici bir veritabanı sürücüsü gerektirmeksizin tüm veri manipülasyonunu ve iş kurallarını kendi üzerinde toplayan nesne tabanlı sınıf:
  - `get_all(search, department, order_by_id)`: Kullanıcıları filtreler ve ID sırasıyla listeler.
  - `get_by_id(user_id)`: Tek bir kullanıcıyı bulur.
  - `exists_by_id(user_id)`: ID çakışma kontrolü yapar.
  - `create(user_data)`: Yeni kullanıcı ekler.
  - `update(user_id, user_data)`: PUT için tüm alanları günceller.
  - `patch(user_id, user_data)`: PATCH için kısmi güncelleme yapar.
  - `delete(user_id)`: Kullanıcıyı bellekten siler.

### 2. Controllers (İki Ayrı Kontrolcü)
- **`ApiUserController` ([`app/controllers/api_user_controller.py`](file:///c:/Users/osman.parlak.ISTBTC/alumni/app/controllers/api_user_controller.py)):**
  - Rota Öneki: `/api/users`
  - Swagger Grubu: `API Users (ApiUserController)`
  - Görevi: REST API tüketicileri için JSON tabanlı CRUD uç noktalarını yönetir.
- **`UserController` ([`app/controllers/user_controller.py`](file:///c:/Users/osman.parlak.ISTBTC/alumni/app/controllers/user_controller.py)):**
  - Rota Öneki: `/users`
  - Swagger Grubu: `Users (UserController)`
  - Görevi: **View katmanını** kullanır. `GET /users` → Model'den kullanıcıları alıp `users/index.html` şablonunu render eder; `POST /users` → HTML formunu işler, `UserModel.create()` çağırır ve `303` ile `GET /users`'a yönlendirir (Post/Redirect/Get). Hata durumunda form, hata mesajıyla `400` olarak tekrar gösterilir.

### 3. View (Week 4)
- **Dosya:** [`app/views/users/index.html`](file:///c:/Users/osman.parlak.ISTBTC/alumni/app/views/users/index.html)
- Controller'dan gelen `users`, `error`, `success` değişkenlerini Jinja2 ile HTML'e dönüştürür (çıktılar otomatik escape edilir).

---

## 📌 API Endpoints (Uç Noktalar)

### 🔹 Genel ve Yardımcı Uç Noktalar (Week 1)
| HTTP Metodu | Uç Nokta (Endpoint) | Açıklama | Başarılı Durum Kodu |
|:---|:---|:---|:---:|
| `GET` | `/` | API welcome message (veya test web arayüzü) | `200 OK` |
| `GET` | `/hello` | Generic greeting (`{"message": "Hello, World!"}`) | `200 OK` |
| `GET` | `/hello/:name` | Named greeting (`{"message": "Hello, :name!"}`) | `200 OK` |
| `GET` | `/sum/:a/:b` | Sum of two integers (`{"a": a, "b": b, "sum": a + b}`) | `200 OK` |
| `GET` | `/about` | Project information (Ders, mimari ve yazar bilgileri) | `200 OK` |
| `GET` | `/api/health` | Health check (`{"status": "ok", ...}`) | `200 OK` |

### 🔹 ApiUserController Uç Noktaları (`/api/users` - Week 2, 3, 4)
| HTTP Metodu | Uç Nokta | Açıklama | Başarılı Yanıt | Hata Yanıtları |
|:---|:---|:---|:---:|:---:|
| `GET` | `/api/users` | List users ordered by ID | `200 OK` | - |
| `GET` | `/api/users/:id` | Get one user by ID | `200 OK` | `404 Not Found` |
| `POST` | `/api/users` | Create an in-memory user | `201 Created` | `400 Bad Request` |
| `PUT` | `/api/users/:id` | Replace a user (Tam güncelleme) | `200 OK` | `404 Not Found` |
| `PATCH` | `/api/users/:id` | Partially update a user (Kısmi güncelleme) | `200 OK` | `404 Not Found` |
| `DELETE` | `/api/users/:id` | Delete a user by ID | `204 No Content` | `404 Not Found` |

### 🔹 UserController Uç Noktaları (`/users` - Week 4 MVC View Layer)
| HTTP Metodu | Uç Nokta | Açıklama | Başarılı Yanıt | Hata Yanıtları |
|:---|:---|:---|:---:|:---:|
| `GET` | `/users` | **Listing** – Tüm mezunları listeler ve ekleme formu sunar (`users/index.html`) | `200 OK` (HTML) | - |
| `POST` | `/users` | **Creating** – Formdan yeni mezun ekler (`UserModel.create()`) ve yönlendirir | `303 See Other` → `/users` | `400` (Hata mesajlı form) |
| `GET` | `/users/:id` | **Show** – Tek bir mezunun detay sayfasını gösterir (`users/show.html`) | `200 OK` (HTML) | `404` (`users/not_found.html`) |
| `GET` | `/users/:id/edit` | **Edit Form** – Mezun güncelleme formunu açar (`users/edit.html`) | `200 OK` (HTML) | `404` (`users/not_found.html`) |
| `PUT` | `/users/:id` | **Full Update** – Tüm alanları günceller (`_method=PUT` formu) | `303 See Other` → `/users/:id` | `400` (Eksik alan) / `404` |
| `PATCH` | `/users/:id` | **Partial Update** – Sadece dolu alanları günceller (`_method=PATCH` formu) | `303 See Other` → `/users/:id` | `400` / `404` |
| `DELETE` | `/users/:id` | **Delete** – Mezunu siler (`_method=DELETE` formu) | `303 See Other` → `/users` | `404` (`users/not_found.html`) |

### 🔹 ApiJobController, ApiApplicationController & Nested Uç Noktaları (Week 6 - Jobs & Applications)
| HTTP Metodu | Uç Nokta | Açıklama | Başarılı Yanıt | Hata Yanıtları |
|:---|:---|:---|:---:|:---:|
| `POST` | `/api/users/:id/jobs` | **Nested Route:** Belirtilen mezun adına iş ilanı açar (`body: {title, company}`) | `201 Created` | `404 Not Found` |
| `GET` | `/api/users/:id/jobs` | **Nested Route:** Belirtilen mezunun açtığı tüm iş ilanlarını listeler | `200 OK` | `404 Not Found` |
| `GET` | `/api/users/:id?include=jobs` | **Include (Join):** Kullanıcıyı açtığı iş ilanlarıyla birlikte tek sorguda döner | `200 OK` | `404 Not Found` |
| `GET` | `/api/jobs` | **Direct Route:** Sistemdeki tüm iş ilanlarını listeler | `200 OK` | - |
| `GET` | `/api/jobs/:id` | **Direct Route:** Belirli bir iş ilanının detayını getirir | `200 OK` | `404 Not Found` |
| `DELETE` | `/api/jobs/:id` | **Direct Route:** İş ilanını ve bağlı başvuruları siler | `204 No Content` | `404 Not Found` |
| `POST` | `/api/jobs/:id/applications` | **Many-to-Many:** İlana başvuru yapar (`body: {userId}`). Mükerrer başvuruda `409` döner | `201 Created` | `404` / `409 Conflict` |
| `GET` | `/api/jobs/:id/applications` | **Two Lists (1):** İlanın başvuru kayıtlarını listeler | `200 OK` | `404 Not Found` |
| `GET` | `/api/jobs/:id/applicants` | **Two Lists (2):** İlana başvuran gerçek mezun kullanıcı profillerini listeler | `200 OK` | `404 Not Found` |
| `GET` | `/api/users/:id/applications` | **Nested Route:** Mezunun başvurduğu tüm ilanları listeler | `200 OK` | `404 Not Found` |
| `GET` | `/api/applications` | **Direct Route:** Sistemdeki tüm başvuruları listeler | `200 OK` | - |
| `PATCH` | `/api/applications/:id` | **Direct Route:** Başvuru durumunu günceller (`applied`, `interview`, `accepted`, `rejected`) | `200 OK` | `404 Not Found` |
| `DELETE` | `/api/applications/:id` | **Direct Route:** Başvuruyu geri çeker / siler | `204 No Content` | `404 Not Found` |

> 🏠 **Week 6 Homework (Ödev - UI for Job Postings & Applications):**
> Hafta 6 kapsamında geliştirilen ilişkisel veri modelleri (`job_postings` ve `applications`) için modern web kullanıcı arayüzü portalı (`/static/index.html`) geliştirilmiştir. Bu arayüz; iş ilanlarını listeleme, ilan açma modalı, ilana tek tıkla başvuru yapma (`UNIQUE` kısıtlaması ile mükerrer başvurularda `409 Conflict` uyarısı) ve başvuranları inceleme işlevlerini interaktif olarak sunmaktadır.


---

## 📊 Veri Tasarımı & Unutma Testi (Data Design Documentation - DDD)

Projenin veri mimarisi, Pydantic DTO şemaları, bellek içi veri depolama kuralları ve durumsuz (stateless) konteyner yaşam döngüsü hakkında kapsamlı dokümantasyon hazırlanmıştır:

👉 **[📊 Data Design Documentation (ddd.md)](ddd.md)**

### 💡 Konteyner Kalıcılık / "Forgetting Test" Özeti:
Projede harici bir veritabanı veya kalıcı Docker Volume bulunmadığından veriler **RAM** üzerinde yaşar. Bu durum şu adımlarla test edilebilir:
1. `docker compose up -d` ile sistem ayağa kaldırılır (2 tohum kayıt yüklüdür).
2. `POST /api/users` ile yeni bir mezun eklenir (toplam 3 kayıt olur).
3. `docker compose down` ile konteyner yok edildiğinde RAM boşaltılır.
4. Tekrar `docker compose up -d` yapıldığında yeni eklenen kaydın **unutulduğu** ve sistemin ilk 2 kayda sıfırlandığı doğrulanır.

Detaylı şemalar, model alanları ve doğrulama kuralları için lütfen **[ddd.md](ddd.md)** dosyasını inceleyiniz.

---

## 🛡️ Middlewares, Guardians & Hata Yönetim Mimarisi

Ders tahtasında belirtilen yönergelere tam uyumlu olarak sisteme middleware ve hata yakalama koruyucuları (guardians) dahil edilmiştir:

```
[İstemci İstekleri]
        │
        ▼
[Logger Middleware] ──────────► Terminal: "10:20:30 POST /users 201 18ms"
        │
        ▼
[404 Guardian] ───────────────► API: 404 Reason JSON | Web: 303 Redirect /404
        │
        ▼
[Method Override] ────────────► Form PUT / PATCH / DELETE desteği
        │
        ▼
[Controller / Routes] ────────► Validasyon Kontrolleri (400 Bad Request)
        │
        ▼
[5xx Guardian] ───────────────► logs/error.logs + Standart 500 JSON / 500 HTML
```

### 1. Postman ile Geçersiz İstekleri Deneme (Invalid Requests)
İsteklerin doğrulanması için Pydantic ve özel doğrulama yakalayıcı devrededir:
- **Eksik Alan Gönderimi:**
  ```json
  POST /api/users/1/jobs
  { "company": "Acme" }
  ```
  Yanıt: `400 Bad Request` ➔ `{"status_code": 400, "error": "Bad Request", "reason": "title: Field required"}`
- **Karakter Sınır Aşımı (Title > 120 Karakter):**
  ```json
  POST /api/users/1/jobs
  { "title": "Çok uzun başlık...", "company": "Acme" }
  ```
  Yanıt: `400 Bad Request` ➔ `{"status_code": 400, "error": "Bad Request", "reason": "title: String should have at most 120 characters"}`

### 2. JobPosting Kuralları (Model & DDD)
- `title required`: Başlık zorunludur.
- `max 120 characters`: Başlık en fazla 120 karakter olabilir.
- `company required`: Şirket alanı zorunludur.
- `city, description are optional`: Şehir ve açıklama alanları isteğe bağlıdır (opsiyonel).

### 3. Logger Middleware (Terminal Günlüğü)
Tüm istekleri yakalayıp terminal ekranına belirtilen formatta canlı log basar:
`time method route res type duration`
```text
10:20:30 POST /users 201 18ms
10:20:35 GET /api/jobs 200 6ms
10:20:40 GET /api/non-existent 404 2ms
```

### 4. 404 Guardian Middleware
- 404 Not Found durumlarında istemciye mutlaka açıklayıcı bir gerekçe (`reason`) döner.
```json
{
  "status_code": 404,
  "error": "Not Found",
  "reason": "The requested resource or endpoint '/api/xyz' was not found.",
  "path": "/api/xyz"
}
```

### 5. 5xx Guardian
- Sunucu kaynaklı öngörülemeyen hatalarda (500 Internal Server Error) sunucunun çökmesini engeller, kullanıcıya güvenli ve standart bir hata yanıtı döner.

### 6. Dosya Hata Günlüğü (`logs/error.logs`)
- 5xx hataları ve yakalanan istisnalar; zaman damgası, HTTP metodu, rota ve tam Python stack trace'i ile birlikte otomatik olarak `logs/error.logs` dosyasına kaydedilir.

### 7. Generic 404 Sayfası ve Yönlendirme (Web Redirect)
- Web tarayıcılarından gelen geçersiz sayfa istekleri otomatik olarak `303 See Other` koduyla generic `/404` rotasına yönlendirilir ve kullanıcıya modern bir 404 HTML sayfası (`app/views/404.html`) sunulur.

---

## 🚀 Çalıştırma Talimatları

### 1. Docker ile Çalıştırma:
```bash
docker compose up --build
```
- 📚 **Swagger UI Dokümanları:** [http://localhost:3000/docs](http://localhost:3000/docs)
- 🌐 **Web Arayüzü:** [http://localhost:3000](http://localhost:3000)
- 📝 **Week 4 View (Listeleme + Ekleme):** [http://localhost:3000/users](http://localhost:3000/users)
- 🔍 **Generic 404 Sayfası:** [http://localhost:3000/404](http://localhost:3000/404)

### 2. Yerel Python ile Çalıştırma:
```bash
pip install -r requirements.txt
python main.py
```

### 3. Test Paketlerini Çalıştırma:
```bash
# 1. Temel API, MVC ve İlişkisel Rota Testleri:
python test_api.py

# 2. Middleware, Guardian, 404/5xx ve Loglama Testleri:
python test_middlewares.py
```

### 4. Veritabanı Migrasyonları (Alembic):
```bash
# Veritabanını en güncel revizyona yükseltme
python -m alembic upgrade head

# Yeni bir şema değişikliği için otomatik migrasyon üretme
python -m alembic revision --autogenerate -m "aciklama"
```

### 5. Veri Fabrikası & Tohumlama (Factory & Seeder - 50 Mezun):
```bash
# 50 adet gerçekçi mezun kaydını veritabanına ekler
python seed.py --count 50

# Veritabanını sıfırlayıp taze 50 kayıt yüklemek için
python seed.py --reset --count 50
```

---

## 📁 Proje Dosya Yapısı

```
alumni/
├── alembic/                             # Alembic şema migrasyon dizini
│   ├── versions/                        # Versiyonlanmış göç dosyaları (DDL scriptleri)
│   │   ├── 4b4900ce1c26_create_users_table.py
│   │   ├── 8f1c4e2a3b5d_create_job_postings_and_applications_tables.py
│   │   └── c3d8f7a1b2c4_add_city_and_description_to_job_postings.py
│   └── env.py                           # Alembic çalışma ortamı ve model bağlayıcı
├── alembic.ini                          # Alembic ana yapılandırma dosyası
├── app/
│   ├── __init__.py
│   ├── database.py                      # SQLAlchemy motoru, SessionLocal, UserRecord & JobPostingRecord
│   ├── factory.py                       # UserFactory & JobPostingFactory (Factory Pattern)
│   ├── logger.py                        # Terminal biçimlendirici ve logs/error.logs dosya yazıcısı
│   ├── middleware.py                    # LoggerMiddleware & Guardian404Middleware
│   ├── main.py                          # Ana uygulama, Middlewares, Guardians & rotalar
│   ├── models.py                        # Model: UserModel, JobPostingModel & Pydantic şemaları
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── api_application_controller.py # /api/applications uç noktaları
│   │   ├── api_job_controller.py         # /api/jobs uç noktaları
│   │   ├── api_user_controller.py        # /api/users uç noktaları
│   │   └── user_controller.py            # /users (HTML View) uç noktaları
│   ├── views/
│   │   ├── 404.html                     # Generic 404 HTML sayfası
│   │   ├── 500.html                     # Generic 500 HTML sayfası
│   │   ├── layout.html                  # Ortak Jinja2 ana şablonu
│   │   └── users/                       # Kullanıcı CRUD HTML şablonları
│   └── static/                          # Statik HTML/CSS/JS dosyaları
├── logs/
│   └── error.logs                       # 5xx ve sistem hata günlükleri
├── Dockerfile                           # Docker yapılandırma dosyası
├── docker-compose.yml                   # Docker Compose servis tanımı
├── requirements.txt                     # Python bağımlılıkları (FastAPI, SQLAlchemy, Alembic, httpx vb.)
├── .env.example                         # Örnek çevre değişkenleri şablonu
├── main.py                              # Yerel çalıştırma giriş noktası
├── seed.py                              # Veritabanı tohumlama CLI betiği
├── test_api.py                          # UserModel & Controller test paketi
├── test_middlewares.py                  # Logger, Guardian, 404 & 5xx test paketi
├── brand.md                             # Marka kimliği ve iletişim standartları
├── DESIGN.MD                            # Tasarım sistemi spesifikasyonu (styles.refero.design & VoltAgent)
├── ddd.md                               # Data Design Documentation
└── README.md                            # Proje dokümantasyonu
```

---

## 👤 Proje Bilgileri
- **Öğrenci:** Osman Parlak
- **Ders:** YBSB3001 - Web Programlama
- **Üniversite:** İstanbul Üniversitesi
