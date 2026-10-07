# 🎓 Üniversite Mezun Takip Sistemi (Alumni Tracking System)

Bu proje, İstanbul Üniversitesi Web Programlama (YBSB3001) dersi kapsamında geliştirilmiş; mezun verilerini takip eden, **MVC (Model-View-Controller)** mimarisiyle yapılandırılmış, modern **Web Kullanıcı Arayüzü** ve **Docker** desteği sunan bir RESTful web uygulamasıdır.

---

## 🌟 Key Features (Temel Özellikler)

- **🏛️ MVC Mimari Deseni:** Model, View ve Controller katmanlarının modern standartlara uygun olarak net bir şekilde ayrılması.
- **⚡ Yüksek Performanslı REST API:** Python FastAPI altyapısıyla asenkron, tip güvenli ve standart HTTP durum kodları (`200`, `201`, `204`, `400`, `404`) ile tam uyumlu uç noktalar.
- **🎨 Modern Web Kullanıcı Arayüzü (Dashboard):**
  - Gerçek zamanlı mezun listeleme, arama ve bölüm bazlı filtreleme.
  - Tablo (Table) ve Kart (Grid Cards) görünüm geçişi.
  - Dinamik modal pencereleri üzerinden Yeni Mezun Ekleme (POST), Tam Güncelleme (PUT) ve Kısmi Güncelleme (PATCH).
  - Güvenli silme onay modalı (DELETE).
  - Canlı REST API işlem konsolu ve otomatik sağlık kontrolü (Health Monitor).
- **🐳 Docker & Docker Compose Entegrasyonu:** Tek bir komutla container ortamında ayağa kalkabilen, üretime ve geliştirmeye hazır yapı.
- **📚 Otomatik İnteraktif API Dokümantasyonu:** Swagger UI (`/docs`) ve ReDoc (`/redoc`) üzerinden anında test edilebilirlik.
- **🛡️ Veri Doğrulama ve Çakışma Koruması:** Pydantic ile gelen verilerin tip denetimi ve mükerrer ID engelleme mantığı.
- **🔢 Sıralı Kullanıcı Listesi:** Mezun kayıtlarının ID'ye göre sıralı sunulması.

---

## 🏗️ MVC (Model-View-Controller) Architecture

Proje, yazılım mühendisliği prensiplerine uygun olarak üç temel katmana ayrılmıştır:

```
                  ┌─────────────────────────────────────────┐
                  │          İstemci / Tarayıcı            │
                  └──────────────────┬──────────────────────┘
                                     │  HTTP Requests (GET, POST, PUT...)
                                     ▼
                  ┌─────────────────────────────────────────┐
                  │             CONTROLLER                  │
                  │   FastAPI Route Handlers (main.py)      │
                  │ - Endpoint routing                      │
                  │ - Business logic & Validation           │
                  │ - HTTP Status Code Management           │
                  └─────────────┬───────────────────────────┘
                                │
        ┌───────────────────────┴───────────────────────┐
        ▼                                               ▼
┌──────────────────────────────┐        ┌──────────────────────────────┐
│            MODEL             │        │             VIEW             │
│   Pydantic & Veri Katmanı    │        │      Sunum Katmanı           │
│   (models.py & users_db)     │        │ (index.html, style.css, JS)  │
│ - UserBase, UserCreate       │        │ - Modern Web Dashboard       │
│ - UserUpdate, UserPatch      │        │ - JSON API Yanıtları         │
│ - In-Memory users_db Store   │        │ - Swagger /docs UI           │
└──────────────────────────────┘        └──────────────────────────────┘
```

### 1. Model (Veri Katmanı ve Doğrulama)
- **Konum:** [`app/models.py`](file:///c:/Users/osman.parlak.ISTBTC/alumni/app/models.py)
- **Görevi:** Veri şemalarını, alan tiplerini ve doğrulama kurallarını tanımlar.
  - `UserBase`: Temel mezun alanlarını (`name`, `email`, `department`) tanımlar.
  - `UserCreate`: Yeni mezun kaydı için giriş şeması (opsiyonel manuel ID desteği ile).
  - `UserUpdate`: Tam güncelleme (PUT) için tüm alanların zorunlu olduğu şema.
  - `UserPatch`: Kısmi güncelleme (PATCH) için opsiyonel alan şeması.
  - `users_db`: Verilerin tutulduğu bellek içi (in-memory) veri deposu.

### 2. View (Sunum Katmanı)
- **Konum:** [`app/static/index.html`](file:///c:/Users/osman.parlak.ISTBTC/alumni/app/static/index.html), [`app/static/style.css`](file:///c:/Users/osman.parlak.ISTBTC/alumni/app/static/style.css), [`app/static/app.js`](file:///c:/Users/osman.parlak.ISTBTC/alumni/app/static/app.js) & JSON Yanıtları
- **Görevi:** Kullanıcıya ve istemcilere sunulan arayüz ve veri formatını yönetir.
  - **Web Dashboard:** Glassmorphism ve Dark Mode estetiğine sahip kullanıcı arayüzü.
  - **JSON Serializer:** FastAPI `response_model` parametreleri ile modellerin standart JSON formatına dönüştürülüp istemciye iletilmesi.
  - **Swagger UI (`/docs`):** API uç noktalarının görsel dokümantasyonu ve test paneli.

### 3. Controller (Yönlendirme ve İş Mantığı Katmanı)
- **Konum:** [`app/main.py`](file:///c:/Users/osman.parlak.ISTBTC/alumni/app/main.py)
- **Görevi:** Gelen HTTP isteklerini yakalar, iş mantığını yürütür, Model katmanını günceller ve uygun HTTP durum kodlarıyla View katmanına yanıt döner.
  - URL eşleştirmesi (Routing) ve parametre ayrıştırma (`user_id`, `name`, `a`, `b`).
  - Hata yönetimi (ID çakışmasında `400 Bad Request`, bulunamadığında `404 Not Found`).

---

## 📌 API Endpoints (Uç Noktalar)

Sistemde tanımlı tüm uç noktaların tam listesi:

| HTTP Metodu | Uç Nokta (Endpoint) | Açıklama | Başarılı Yanıt (Status) | Hata Yanıtları |
|:---|:---|:---|:---:|:---:|
| `GET` | `/` | API welcome message (veya Web Arayüzü) | `200 OK` | - |
| `GET` | `/hello` | Generic greeting | `200 OK` | - |
| `GET` | `/hello/:name` | Named greeting | `200 OK` | - |
| `GET` | `/sum/:a/:b` | Sum of two integers | `200 OK` | `422` (Geçersiz int) |
| `GET` | `/about` | Project information | `200 OK` | - |
| `GET` | `/api/health` | Health check | `200 OK` | - |
| `POST` | `/api/users` | Create an in-memory user | `201 Created` | `400` (ID çakışması) |
| `GET` | `/api/users` | List users ordered by ID | `200 OK` | - |
| `GET` | `/api/users/:id` | Get one user | `200 OK` | `404` (Bulunamadı) |
| `PUT` | `/api/users/:id` | Replace a user (Tam güncelleme) | `200 OK` | `404` (Bulunamadı) |
| `PATCH` | `/api/users/:id` | Partially update a user (Kısmi güncelleme) | `200 OK` | `404` (Bulunamadı) |
| `DELETE` | `/api/users/:id` | Delete a user (Kullanıcı silme) | `204 No Content` | `404` (Bulunamadı) |

---

## 🚀 Docker ile Çalıştırma

Uygulamayı Docker ile çalıştırmak için sisteminizde Docker'ın kurulu ve çalışır durumda olması yeterlidir:

### 1. Docker Compose ile Başlatma:
```bash
docker compose up --build
```

Arka planda (detached modda) çalıştırmak için:
```bash
docker compose up -d --build
```

Durdurmak için:
```bash
docker compose down
```

### 2. Standart Docker CLI ile Başlatma:
```bash
# İmajı oluşturun
docker build -t alumni-tracking-system .

# Konteyneri başlatın (Port 3000)
docker run -p 3000:3000 --name alumni_container alumni-tracking-system
```

Sunucu ayağa kalktıktan sonra aşağıdaki adreslerden erişebilirsiniz:
- 🌐 **Web Arayüzü Portalı:** [http://localhost:3000](http://localhost:3000)
- 📚 **Swagger API Dokümantasyonu:** [http://localhost:3000/docs](http://localhost:3000/docs)
- 🩺 **Sağlık Kontrolü:** [http://localhost:3000/api/health](http://localhost:3000/api/health)

---

## 💻 Yerel Geliştirme Ortamı (Docker Olmadan)

Gereksinim: **Python 3.9+**

1. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

2. Sunucuyu başlatın:
   ```bash
   python main.py
   ```
   *(Varsayılan port `3000`'dir. `PORT` ortam değişkeni ile özelleştirilebilir.)*

3. Birim testleri çalıştırın:
   ```bash
   python test_api.py
   ```

---

## 🧪 Örnek İstekler ve Yanıtlar (cURL)

### 1. Genel ve Karşılama İstekleri:
```bash
# Generic greeting
curl http://localhost:3000/hello
# Yanıt: {"message": "Hello, World!"}

# Named greeting
curl http://localhost:3000/hello/Osman
# Yanıt: {"message": "Hello, Osman!"}

# Sum of two integers
curl http://localhost:3000/sum/15/27
# Yanıt: {"a": 15, "b": 27, "sum": 42}

# Project information
curl http://localhost:3000/about
```

### 2. Yeni Mezun Kullanıcı Oluşturma (POST):
```bash
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"id": 3, "name": "Zeynep Kaya", "email": "zeynep@example.com", "department": "Industrial Engineering"}'
```
*HTTP Yanıtı:* `201 Created`

### 3. Kullanıcıları ID'ye Göre Sıralı Listeleme (GET):
```bash
curl http://localhost:3000/api/users
```

### 4. Tek Bir Kullanıcı Getirme (GET):
```bash
curl http://localhost:3000/api/users/1
```

### 5. Kullanıcı Güncelleme (PUT & PATCH):
```bash
# Tam Değiştirme (PUT)
curl -X PUT http://localhost:3000/api/users/3 \
  -H "Content-Type: application/json" \
  -d '{"name": "Zeynep Kaya Parlak", "email": "zeynep.p@example.com", "department": "Industrial Engineering"}'

# Kısmi Güncelleme (PATCH)
curl -X PATCH http://localhost:3000/api/users/3 \
  -H "Content-Type: application/json" \
  -d '{"department": "AI & Data Engineering"}'
```

### 6. Kullanıcı Silme (DELETE):
```bash
curl -X DELETE http://localhost:3000/api/users/3
```
*HTTP Yanıtı:* `204 No Content`

---

## 📁 Proje Dosya Yapısı

```
alumni/
├── app/
│   ├── __init__.py
│   ├── main.py          # Controller: FastAPI route'ları ve iş mantığı
│   ├── models.py        # Model: Pydantic veri modelleri ve doğrulama
│   └── static/          # View: Web sunum katmanı
│       ├── index.html   # Modern HTML5 arayüz sayfası
│       ├── style.css    # Özel CSS tasarım sistemi (Dark/Glassmorphism)
│       └── app.js       # Dinamik JS istemcisi ve canlı log konsolu
├── Dockerfile           # Python 3.11 tabanlı Dockerfile
├── docker-compose.yml   # Servis konteyner yapılandırması
├── .dockerignore        # Gereksiz dosyaların imaja eklenmesini önler
├── requirements.txt     # Python paket bağımlılıkları
├── main.py              # Yerel çalıştırma giriş noktası
├── test_api.py          # 12 uç noktanın otomatik test paketi
└── README.md            # Proje dokümantasyonu (MVC, Key Features, Endpoints)
```

---

## 👤 Hazırlayan
- **Öğrenci:** Osman Parlak
- **Ders:** YBSB3001 - Web Programlama
- **Kurum:** İstanbul Üniversitesi
