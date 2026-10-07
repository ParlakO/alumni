# 🎓 Üniversite Mezun Takip Sistemi (Alumni Tracking System API)

Bu proje, **İstanbul Üniversitesi Web Programlama (YBSB3001)** dersi kapsamında geliştirilmiş; **MVC (Model-View-Controller)** mimarisiyle yapılandırılmış, veritabanı bağlantısı gerektirmeyen bellek içi (In-Memory) **UserModel**, iki ayrı kontrolcü (**UserController** ve **ApiUserController**) ve **Docker** desteği sunan bir RESTful web uygulamasıdır.

---

## 📅 Haftalık Gelişim Adımları (Week Breakdown)

Proje, ders müfredatındaki 4 haftalık kazanımları açık ve modüler biçimde yansıtır:

| Hafta | Konu | İlgili Dosyalar & Fonksiyonlar | Açıklama |
|:---|:---|:---|:---|
| **Week 1** | Temel Yönlendirme (Routing) & Karşılama | [`app/main.py`](file:///c:/Users/osman.parlak.ISTBTC/alumni/app/main.py) | `GET /`, `GET /hello`, `GET /hello/:name`, `GET /sum/:a/:b`, `GET /about`, `GET /api/health` |
| **Week 2** | Bellek İçi Veri Yapısı & Okuma İşlemleri | [`app/models.py`](file:///c:/Users/osman.parlak.ISTBTC/alumni/app/models.py) | In-Memory veri listesi, `GET /api/users` (listeleme) ve `GET /api/users/:id` |
| **Week 3** | Tam CRUD Operasyonları & Validasyon | [`app/models.py`](file:///c:/Users/osman.parlak.ISTBTC/alumni/app/models.py) | POST (oluşturma), PUT (tam güncelleme), PATCH (kısmi güncelleme), DELETE (silme), Pydantic validasyonu ve HTTP durum kodları (`201`, `204`, `400`, `404`) |
| **Week 4** | MVC Mimarisi, Çift Kontrolcü & View Katmanı | [`app/controllers/`](file:///c:/Users/osman.parlak.ISTBTC/alumni/app/controllers/), [`app/views/`](file:///c:/Users/osman.parlak.ISTBTC/alumni/app/views/) | DB bağlantısız **UserModel** CRUD metotları, **UserController** (`/users`), **ApiUserController** (`/api/users`), View katmanı: `GET /users` (listeleme) ve `POST /users` (oluşturma) HTML sayfası |

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

### 🔹 UserController Uç Noktaları (`/users` - Week 4)
| HTTP Metodu | Uç Nokta | Açıklama | Başarılı Yanıt | Hata Yanıtları |
|:---|:---|:---|:---:|:---:|
| `GET` | `/users` | **Listing** – mezun listesini HTML sayfası olarak render eder (View) | `200 OK` (HTML) | - |
| `GET` | `/users/:id` | Get one user by ID | `200 OK` | `404 Not Found` |
| `POST` | `/users` | **Creating** – HTML formundan (`application/x-www-form-urlencoded`) kullanıcı oluşturur | `303 See Other` → `/users` | `400` (HTML, hata mesajlı) |
| `PUT` | `/users/:id` | Replace user (Tam güncelleme) | `200 OK` | `404 Not Found` |
| `PATCH` | `/users/:id` | Partially update user (Kısmi güncelleme) | `200 OK` | `404 Not Found` |
| `DELETE` | `/users/:id` | Delete user by ID | `204 No Content` | `404 Not Found` |

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

---

## 📁 Proje Dosya Yapısı

```
alumni/
├── app/
│   ├── __init__.py
│   ├── main.py                          # Ana uygulama, Week 1 rotaları & Controller kayıtları
│   ├── models.py                        # Model: UserModel (No DB, CRUD fonksiyonları) & Pydantic şemaları
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
├── requirements.txt                     # Python bağımlılıkları (FastAPI, Uvicorn, Pydantic, Jinja2, python-multipart)
├── main.py                              # Yerel çalıştırma giriş noktası
├── test_api.py                          # UserModel & her iki Controller'ı test eden test paketi
└── README.md                            # Proje dokümantasyonu
```

---

## 👤 Proje Bilgileri
- **Öğrenci:** Osman Parlak
- **Ders:** YBSB3001 - Web Programlama
- **Üniversite:** İstanbul Üniversitesi
