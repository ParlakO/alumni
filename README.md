# 🎓 Üniversite Mezun Takip Sistemi (Alumni Tracking System API)

Bu proje, **İstanbul Üniversitesi Web Programlama (YBSB3001)** dersi kapsamında geliştirilmiş; **MVC (Model-View-Controller)** mimarisiyle yapılandırılmış, veritabanı bağlantısı gerektirmeyen bellek içi (In-Memory) **UserModel**, iki ayrı kontrolcü (**UserController** ve **ApiUserController**) ve **Docker** desteği sunan bir RESTful web uygulamasıdır.

---

## 📅 Haftalık Gelişim Adımları (Week Breakdown)

Proje, ders müfredatındaki 6 haftalık kazanımları açık ve modüler biçimde yansıtır:

| Hafta | Konu | İlgili Dosyalar & Fonksiyonlar | Açıklama |
|:---|:---|:---|:---|
| **Week 1** | Temel Yönlendirme (Routing) & Karşılama | [`app/main.py`](app/main.py) | `GET /`, `GET /hello`, `GET /hello/:name`, `GET /sum/:a/:b`, `GET /about`, `GET /api/health` |
| **Week 2** | Bellek İçi Veri Yapısı & Okuma İşlemleri | [`app/models.py`](app/models.py) | In-Memory veri listesi, `GET /api/users` (listeleme) ve `GET /api/users/:id` |
| **Week 3** | Tam CRUD Operasyonları & Validasyon | [`app/models.py`](app/models.py) | POST (oluşturma), PUT (tam güncelleme), PATCH (kısmi güncelleme), DELETE (silme), Pydantic validasyonu ve HTTP durum kodları (`201`, `204`, `400`, `404`) |
| **Week 4** | MVC Mimarisi, Çift Kontrolcü & View Katmanı | [`app/controllers/`](app/controllers/), [`app/views/`](app/views/) | DB bağlantısız **UserModel** CRUD metotları, **UserController** (`/users`), **ApiUserController** (`/api/users`), View katmanı: `GET /users` (listeleme) ve `POST /users` (oluşturma) HTML sayfası |
| **Week 5** | Veritabanı Göçü (Migration) & Kalıcı Depolama | [`app/database.py`](app/database.py), [`alembic/`](alembic/) | SQLite veritabanı, SQLAlchemy ORM modeli (`UserRecord`), Alembic migrasyonları (`upgrade head`) ile şema versiyonlama ve persistent veri saklama |
| **Week 6** | İlişkisel Veri & İleri Düzey Yönlendirme (Relational Data & Advanced Routing) | [`ddd.md`](ddd.md), [`alembic/`](alembic/), [`app/database.py`](app/database.py), [`app/models.py`](app/models.py), [`app/controllers/`](app/controllers/) | - **İlişkisel Veri:** `job_postings` (1:N One-to-Many / hasMany / belongsTo) ve `applications` (N:M Many-to-Many Join Table, `UNIQUE(user_id, job_posting_id)` ile mükerrerlikte `409 Conflict`).<br>- **Yeni Migrasyon:** *"A new file — never edit the old one"* kuralıyla yeni Alembic migrasyon revizyonu.<br>- **Silme Kuralı:** `RESTRICT` stratejisi (Aktif iş ilanı olan mezunun silinmesi engellenir; `409 Conflict`).<br>- **Nested Routes:** `POST /api/users/:id/jobs` (İlan sahibini URL yolu söyler, body asla `user_id` taşımaz; 404/201), `GET /api/users/:id/jobs`.<br>- **Include (Join):** `GET /api/users/:id?include=jobs` (`LEFT JOIN` ile tek yanıtta iki tablo).<br>- **İki Liste Prensibi:** `GET /api/jobs/:id/applications` (başvuru kayıtları) vs `GET /api/jobs/:id/applicants` (başvuran mezun profilleri).<br>- **Tohumlama:** `JobPostingFactory` ve `ApplicationFactory` ile ilişkisel verilerin sıralı tohumlanması (`seed.py`).<br>- **🏠 Homework (Ödev):** *UI for Job Postings & Applications:* İş ilanlarını listeleme, ilan oluşturma modalı, ilana tek tıkla başvuru yapma (`409 Conflict` mükerrerlik uyarısı ile) ve başvuranları inceleme işlevlerini sunan interaktif kullanıcı arayüzü portalı (`/static/index.html`). |


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

## 🚀 Çalıştırma Talimatları

### 1. Docker ile Çalıştırma:
```bash
docker compose up --build
```
- 📚 **Swagger UI Dokümanları:** [http://localhost:3000/docs](http://localhost:3000/docs)
- 🌐 **Web Arayüzü:** [http://localhost:3000](http://localhost:3000)
- 📝 **Week 4 View (Listeleme + Ekleme):** [http://localhost:3000/users](http://localhost:3000/users)

### 2. Yerel Python ile Çalıştırma:
```bash
pip install -r requirements.txt
python main.py
```

### 3. Test Paketini Çalıştırma:
```bash
python test_api.py
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
│   └── env.py                           # Alembic çalışma ortamı ve model bağlayıcı
├── alembic.ini                          # Alembic ana yapılandırma dosyası
├── app/
│   ├── __init__.py
│   ├── database.py                      # SQLAlchemy motoru, SessionLocal & UserRecord ORM modeli
│   ├── factory.py                       # UserFactory: Gerçekçi mezun veri üretim fabrikası (Factory Pattern)
│   ├── main.py                          # Ana uygulama, Week 1 rotaları & Controller kayıtları
│   ├── models.py                        # Model: UserModel (DB destekli CRUD) & Pydantic şemaları
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── api_user_controller.py      # Controller 1: /api/users uç noktaları
│   │   └── user_controller.py          # Controller 2: /users uç noktaları
│   ├── views/
│   │   └── users/
│   │       └── index.html              # View (Week 4): GET /users listeleme + POST /users formu
│   └── static/                          # Statik HTML/CSS/JS dosyaları
├── Dockerfile                           # Docker yapılandırma dosyası
├── docker-compose.yml                   # Docker Compose servis tanımı
├── requirements.txt                     # Python bağımlılıkları (FastAPI, SQLAlchemy, Alembic vb.)
├── .env.example                         # Örnek çevre değişkenleri şablonu (şablon)
├── .env                                 # Gerçek çevre değişkenleri (lokal/gizli, gitignore'da)
├── main.py                              # Yerel çalıştırma giriş noktası
├── seed.py                              # 50 mezun tohumlama CLI betiği (Database Seeder)
├── test_api.py                          # UserModel & her iki Controller'ı test eden test paketi
├── ddd.md                               # Data Design Documentation (Veri modelleri, şemalar & migrasyon)
└── README.md                            # Proje dokümantasyonu
```

---

## 👤 Proje Bilgileri
- **Öğrenci:** Osman Parlak
- **Ders:** YBSB3001 - Web Programlama
- **Üniversite:** İstanbul Üniversitesi
