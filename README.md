# 🎓 Üniversite Mezun Takip Sistemi (Alumni Tracking System API)

Bu proje, **İstanbul Üniversitesi Web Programlama (YBSB3001)** dersi kapsamında geliştirilmiş bir RESTful Mezun Takip Sistemi API'sidir. 

Projenin temel odağı; **REST API mimarisi**, **HTTP metodları (GET, POST, PUT, PATCH, DELETE)**, **HTTP durum kodları**, **Pydantic ile veri doğrulama**, **MVC (Model-View-Controller) prensipleri** ve **Docker ile container ortamında çalıştırma** pratikleridir.

---

## 🌟 Key Features (Temel Özellikler)

- **🏛️ MVC Mimari Yapısı:** Model (Pydantic & In-Memory Store), View (JSON Yanıtları & Swagger UI) ve Controller (Route İşleyicileri) katmanlarının açık ayrımı.
- **⚡ Kapsamlı REST API:** 
  - Tam CRUD operasyonları (Oluşturma, Okuma, Tam/Kısmi Güncelleme, Silme).
  - Standart HTTP durum kodları (`200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `404 Not Found`, `422 Unprocessable Entity`).
- **🛡️ Veri Doğrulama & Çakışma Yönetimi:**
  - Pydantic şemaları ile istek gövdesi (request body) ve tip doğrulaması.
  - POST isteklerinde mükerrer ID kontrolü (`400 User ID already exists`).
- **🔢 Sıralı Kullanıcı Listeleme:** `GET /api/users` uç noktasında mezunların ID'ye göre sıralı (`ordered by ID`) döndürülmesi.
- **📚 Etkileşimli API Dokümantasyonu:** Swagger UI (`/docs`) ve ReDoc (`/redoc`) üzerinden anında uç nokta testi.
- **🐳 Docker Desteği:** `docker compose up --build` ile harici bağımlılık kurmadan tek komutla ayağa kaldırma.
- **💻 Basit & Odaklı Mimari:** Okul projesi gereksinimlerine uygun olarak karmaşık veritabanı kurulumları yerine eğitim amaçlı In-Memory (bellek içi) veri yapısı.

---

## 🏗️ MVC (Model-View-Controller) Architecture

Projede uygulanan MVC deseninin FastAPI ve REST API üzerindeki karşılığı:

```
                  ┌─────────────────────────────────────────┐
                  │          İstemci (Client / Postman)     │
                  └──────────────────┬──────────────────────┘
                                     │  HTTP İstekleri (GET, POST, PUT...)
                                     ▼
                  ┌─────────────────────────────────────────┐
                  │             CONTROLLER                  │
                  │        FastAPI Routes (main.py)         │
                  │ - Endpoint yönlendirme                  │
                  │ - İstek doğrulama ve iş mantığı         │
                  │ - HTTP durum kodlarının belirlenmesi    │
                  └─────────────┬───────────────────────────┘
                                │
        ┌───────────────────────┴───────────────────────┐
        ▼                                               ▼
┌──────────────────────────────┐        ┌──────────────────────────────┐
│            MODEL             │        │             VIEW             │
│   Veri & Şema Katmanı        │        │        Sunum Katmanı         │
│   (models.py & users_db)     │        │     (JSON & Swagger UI)      │
│ - UserBase, UserCreate       │        │ - JSON API Yanıtları         │
│ - UserUpdate, UserPatch      │        │ - Swagger UI (/docs)         │
│ - In-Memory `users_db` Liste │        │ - Hafif Web Arayüzü          │
└──────────────────────────────┘        └──────────────────────────────┘
```

### 1. Model (Veri ve Şema Katmanı)
- **Dosya:** [`app/models.py`](file:///c:/Users/osman.parlak.ISTBTC/alumni/app/models.py)
- **Görevi:** Verinin yapısını, kurallarını ve tiplerini belirler.
  - `UserBase`: Ortak mezun alanları (`name`, `email`, `department`).
  - `UserCreate`: Yeni mezun kaydı için Pydantic modeli (opsiyonel ID).
  - `UserUpdate`: PUT ile tam güncelleme şeması (tüm alanlar zorunlu).
  - `UserPatch`: PATCH ile kısmi güncelleme şeması (alanlar opsiyonel).
  - `users_db`: Ders gereksinimine uygun in-memory (bellek içi) kullanıcı listesi.

### 2. View (Sunum Katmanı)
- **Görevi:** İstemcinin aldığı görsel veya yapısal çıktıyı yönetir.
  - **JSON Yanıtları:** FastAPI'nin `response_model` ile Pydantic modellerini otomatik serileştirip JSON olarak sunması.
  - **Swagger UI (`/docs`):** API uç noktalarını listeleyen ve doğrudan test imkânı sunan etkileşimli dokümantasyon arayüzü.
  - **Web Test Arayüzü:** Tarayıcı üzerinden yapılan istekler için temel arayüz.

### 3. Controller (Yönlendirme ve İş Mantığı Katmanı)
- **Dosya:** [`app/main.py`](file:///c:/Users/osman.parlak.ISTBTC/alumni/app/main.py)
- **Görevi:** HTTP isteklerini karşılar, URL parametrelerini çözer, Model üzerinde gerekli değişiklikleri yapar ve uygun HTTP yanıtını döner.
  - Hata durumlarında `HTTPException` fırlatarak doğru durum kodlarını (`400`, `404`) üretir.

---

## 📌 API Endpoints (Uç Noktalar)

| HTTP Metodu | Uç Nokta (Endpoint) | Açıklama | Başarılı Yanıt Kodu | Hata Kodları |
|:---|:---|:---|:---:|:---:|
| `GET` | `/` | API welcome message | `200 OK` | - |
| `GET` | `/hello` | Generic greeting (`{"message": "Hello, World!"}`) | `200 OK` | - |
| `GET` | `/hello/:name` | Named greeting (`{"message": "Hello, :name!"}`) | `200 OK` | - |
| `GET` | `/sum/:a/:b` | Sum of two integers (`{"a": a, "b": b, "sum": a + b}`) | `200 OK` | `422` (Geçersiz int) |
| `GET` | `/about` | Project information (Ders, mimari ve proje bilgisi) | `200 OK` | - |
| `GET` | `/api/health` | Health check (`{"status": "ok", ...}`) | `200 OK` | - |
| `POST` | `/api/users` | Create an in-memory user (Mükerrer ID kontrolü) | `201 Created` | `400` (ID çakışması) |
| `GET` | `/api/users` | List users ordered by ID | `200 OK` | - |
| `GET` | `/api/users/:id` | Get one user by ID | `200 OK` | `404` (Bulunamadı) |
| `PUT` | `/api/users/:id` | Replace a user (Tam güncelleme) | `200 OK` | `404` (Bulunamadı) |
| `PATCH` | `/api/users/:id` | Partially update a user (Kısmi güncelleme) | `200 OK` | `404` (Bulunamadı) |
| `DELETE` | `/api/users/:id` | Delete a user by ID | `204 No Content` | `404` (Bulunamadı) |

---

## 🚀 Çalıştırma Talimatları

### Seçenek 1: Docker ile Çalıştırma (Önerilen)

Projeyi container ortamında ayağa kaldırmak için:

```bash
docker compose up --build
```

Arka planda çalıştırmak için:
```bash
docker compose up -d --build
```

Kapatmak için:
```bash
docker compose down
```

### Seçenek 2: Yerel Python ile Çalıştırma

Gereksinim: Python 3.9+

1. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

2. Sunucuyu başlatın:
   ```bash
   python main.py
   ```
   *(Varsayılan port: 3000)*

3. Testleri çalıştırın:
   ```bash
   python test_api.py
   ```

---

## 🧪 Örnek Test İstekleri (cURL)

```bash
# 1. Genel Karşılama ve Yardımcı Uç Noktalar
curl http://localhost:3000/hello
curl http://localhost:3000/hello/Osman
curl http://localhost:3000/sum/10/25
curl http://localhost:3000/about
curl http://localhost:3000/api/health

# 2. Kullanıcı Ekleme (POST - 201 Created)
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"id": 3, "name": "Ali Veli", "email": "ali@example.com", "department": "MIS"}'

# 3. Sıralı Kullanıcı Listesi (GET - 200 OK)
curl http://localhost:3000/api/users

# 4. Tek Kullanıcı Getirme (GET - 200 OK)
curl http://localhost:3000/api/users/3

# 5. Tam Güncelleme (PUT - 200 OK)
curl -X PUT http://localhost:3000/api/users/3 \
  -H "Content-Type: application/json" \
  -d '{"name": "Ali Veli Guncel", "email": "ali.guncel@example.com", "department": "Computer Engineering"}'

# 6. Kısmi Güncelleme (PATCH - 200 OK)
curl -X PATCH http://localhost:3000/api/users/3 \
  -H "Content-Type: application/json" \
  -d '{"department": "Industrial Engineering"}'

# 7. Kullanıcı Silme (DELETE - 204 No Content)
curl -X DELETE http://localhost:3000/api/users/3
```

---

## 📂 Proje Dizin Yapısı

```
alumni/
├── app/
│   ├── __init__.py
│   ├── main.py          # Controller: FastAPI route işleyicileri & REST endpoints
│   ├── models.py        # Model: Pydantic veri şemaları & validasyon
│   └── static/          # View: Statik dosyalar ve web arayüzü
├── Dockerfile           # Docker container konfigürasyonu
├── docker-compose.yml   # Docker Compose servis tanımı
├── requirements.txt     # Python bağımlılıkları (FastAPI, Uvicorn, Pydantic)
├── main.py              # Yerel çalıştırma giriş noktası
├── test_api.py          # Uç noktaları test eden birim test scripti
└── README.md            # Proje dokümantasyonu
```

---

## 👤 Proje Bilgileri
- **Öğrenci:** Osman Parlak
- **Ders:** YBSB3001 - Web Programlama
- **Üniversite:** İstanbul Üniversitesi
