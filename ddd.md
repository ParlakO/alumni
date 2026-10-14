# 📊 Veri Tasarımı Dokümantasyonu (Data Design Documentation - DDD)

Bu doküman, **Üniversite Mezun Takip Sistemi (Alumni Tracking System)** uygulamasının veri modellerini, veri akışını, kısıtlamalarını ve yaşam döngüsünü detaylandıran resmi veri tasarım dokümantasyonudur (Data Design Document - DDD).

---

## 📑 İçindekiler
- [1. Veri Mimarisi Özeti](#1-veri-mimarisi-özeti)
- [2. Varlık ve Alan Tanımları (Entity Schema)](#2-varlık-ve-alan-tanımları-entity-schema)
- [3. Pydantic Şemaları ve Veri Transfer Nesneleri (DTO)](#3-pydantic-şemaları-ve-veri-transfer-nesneleri-dto)
- [4. Bellek İçi Veri Depolama (In-Memory Storage)](#4-bellek-içi-veri-depolama-in-memory-storage)
- [5. CRUD İş Kuralları ve Veri Doğrulama](#5-crud-iş-kuralları-ve-veri-doğrulama)
- [6. Konteyner Yaşam Döngüsü ve "Forgetting Test" (Statelessness)](#6-konteyner-yaşam-döngüsü-ve-forgetting-test-statelessness)
- [7. Gelecek Veritabanı Geçiş Yol Haritası (Database Roadmap)](#7-gelecek-veritabanı-geçiş-yol-haritası-database-roadmap)

---

## 1. Veri Mimarisi Özeti

Proje, **MVC (Model-View-Controller)** mimarisinin Model katmanını harici bir SQL/NoSQL veritabanı sürücüsü kullanmadan, saf Python nesneleri ve **Pydantic v2** ile bellek üzerinde (In-Memory) yönetecek şekilde tasarlanmıştır.

- **Kaynak Dosya:** [`app/models.py`](app/models.py)
- **Veri Saklama Biçimi:** Python Sözlük Listesi (`List[dict]`)
- **Veri Bütünlüğü & Validasyon:** Pydantic `BaseModel` ve `Field` kısıtlamaları
- **Erişim Modeli:** Singleton `user_model = UserModel()` örneği üzerinden merkezi CRUD yönetimi

```
                  ┌──────────────────────────────────────────────┐
                  │                 HTTP Request                 │
                  └───────────────────────┬──────────────────────┘
                                          │
                                          ▼
                  ┌──────────────────────────────────────────────┐
                  │        Pydantic DTO (Validation Layer)       │
                  │   UserCreate / UserUpdate / UserPatch        │
                  └───────────────────────┬──────────────────────┘
                                          │ Validated Data
                                          ▼
                  ┌──────────────────────────────────────────────┐
                  │          UserModel (Business Layer)          │
                  │  - ID Çakışma Denetimi                       │
                  │  - Otomatik ID Üretimi                       │
                  │  - Arama, Filtreleme, Sıralama               │
                  └───────────────────────┬──────────────────────┘
                                          │
                                          ▼
                  ┌──────────────────────────────────────────────┐
                  │    In-Memory Storage: self._users (List)     │
                  └──────────────────────────────────────────────┘
```

---

## 2. Varlık ve Alan Tanımları (Entity Schema)

Sistemdeki temel varlık **`User` (Mezun)** varlığıdır:

| Alan Adı (Field) | Veri Tipi | Zorunlu mu? | Min / Max Uzunluk | Örnek Değer | Açıklama |
|:---|:---|:---:|:---:|:---|:---|
| **`id`** | `Integer` | Evet (Otomatik/Opsiyonel) | Pozitif tam sayı | `1` | Kullanıcının benzersiz kimlik numarası (Primary Key niteliğinde). |
| **`name`** | `String` | Evet | 2 - 100 karakter | `"Osman Parlak"` | Mezunun ad ve soyadı. |
| **`email`** | `String` | Evet | 5 - 120 karakter | `"osman@example.com"` | Mezunun iletişim e-posta adresi. |
| **`department`** | `String` | Evet | 2 - 100 karakter | `"MIS"` | Mezun olunan üniversite bölümü. |

---

## 3. Pydantic Şemaları ve Veri Transfer Nesneleri (DTO)

Farklı HTTP operasyonlarının gereksinimlerine göre özelleştirilmiş 5 adet veri şeması bulunmaktadır:

### 3.1. `UserBase`
Ortak alanları barındıran temel şema:
```python
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="Osman Parlak")
    email: str = Field(..., min_length=5, max_length=120, example="osman@example.com")
    department: str = Field(..., min_length=2, max_length=100, example="MIS")
```

### 3.2. `UserCreate` (POST İstekleri)
Yeni kayıt oluşturma şeması. `id` alanı opsiyoneldir; kullanıcı dilerse manuel ID belirtebilir:
```python
class UserCreate(BaseModel):
    id: Optional[int] = Field(None, description="Opsiyonel ID. Belirtilmezse otomatik siradaki ID verilir.")
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=120)
    department: str = Field(..., min_length=2, max_length=100)
```

### 3.3. `UserUpdate` (PUT İstekleri)
Kaydın tüm alanlarının eksiksiz yeniden yazılması (Full Replacement) kuralını zorunlu kılar:
```python
class UserUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=120)
    department: str = Field(..., min_length=2, max_length=100)
```

### 3.4. `UserPatch` (PATCH İstekleri)
Kısmi güncelleme şeması. Tüm alanlar opsiyoneldir; sadece gönderilen alanlar güncellenir:
```python
class UserPatch(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = Field(None, min_length=5, max_length=120)
    department: Optional[str] = Field(None, min_length=2, max_length=100)
```

### 3.5. `User` (Response Modeli)
İstemciye dönülen veriyi garanti altına alır; `id` kesinlikle zorunludur:
```python
class User(UserBase):
    id: int
```

---

## 4. Bellek İçi Veri Depolama (In-Memory Storage)

Sistem ayağa kalktığında `UserModel` sınıfı örneklenir ve varsayılan başlangıç tohum verileri (seed data) ile yüklenir:

```python
self._users: List[dict] = [
    {"id": 1, "name": "Osman Parlak", "email": "osman@example.com", "department": "MIS"},
    {"id": 2, "name": "Ahmet Yilmaz", "email": "ahmet@example.com", "department": "Computer Engineering"}
]
```

Bu liste, uygulama çalıştığı sürece işlem belleğinde (RAM) canlı tutulur.

---

## 5. CRUD İş Kuralları ve Veri Doğrulama

[`UserModel`](app/models.py) katmanında uygulanan iş kuralları:

1. **Listeleme ve Sıralama (`get_all`):**
   - Sonuçlar varsayılan olarak ID'ye göre küçükten büyüğe sıralı (`results.sort(key=lambda u: u["id"])`) döner.
   - `department` ve `search` parametreleri ile büyük/küçük harf duyarsız (case-insensitive) arama ve filtreleme yapılır.
2. **Kimlik Çakışma Denetimi (`exists_by_id`):**
   - POST işleminde manuel bir `id` verilmişse `exists_by_id(user_data.id)` çağrılır. Çakışma varsa `ValueError("User ID already exists")` fırlatılır ve istemciye `400 Bad Request` yanıtı iletilir.
3. **Otomatik Sıralı ID Üretimi:**
   - Manuel ID verilmezse `max([u["id"] for u in self._users], default=0) + 1` formülüyle bir sonraki sıralı ID üretilir.
4. **Tam Güncelleme (`PUT`):**
   - Kayıt bulunamazsa `None` döner (`404 Not Found`). Kayıt varsa ID korunarak tüm diğer alanlar ezilir.
5. **Kısmi Güncelleme (`PATCH`):**
   - Yalnızca `None` olmayan alanlar güncellenir; diğer alanlar eski değerini korur.
6. **Silme (`DELETE`):**
   - Kayıt listeden `pop` edilerek çıkarılır ve `204 No Content` durumu üretilir.

---

## 6. Konteyner Yaşam Döngüsü ve "Forgetting Test" (Statelessness)

Bu mimarinin en temel pedagojik özelliklerinden biri **durumsuzluk (statelessness)** ve **ephemeral container** kavramlarının test edilebilmesidir:

- **RAM Bağımlılığı:** Veriler fiziksel bir diskte veya harici bir veritabanında tutulmadığı için sadece konteynerin yaşam döngüsü boyunca mevcuttur.
- **Forgetting Test Senaryosu:**
  1. `docker compose up -d` ile uygulama başlatılır (2 başlangıç kaydı vardır).
  2. `POST /api/users` ile yeni bir kayıt (örn. ID: 3) eklenir.
  3. `docker compose down` komutuyla konteyner kapatılır (RAM sıfırlanır).
  4. `docker compose up -d` ile yeniden başlatıldığında 3. kaydın **unutulduğu**, sistemin ilk 2 kayda geri döndüğü gözlemlenir.

Bu test, mikroservis ve bulut mimarilerinde veritabanı ve Docker Volume gereksiniminin önemini somut olarak kanıtlar.

---

## 7. Veritabanı Göçü ve Alembic Entegrasyonu (Week 5 - Database Migration)

Uygulama, bellek içi (In-Memory) yapıdan kalıcı **SQLite** veritabanına ve endüstri standardı **Alembic** migrasyon aracına başarıyla geçirilmiştir:

### 7.1. SQLAlchemy ORM Modeli ([`app/database.py`](app/database.py))
```python
class UserRecord(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    department = Column(String(100), nullable=False)
```

### 7.2. Alembic Migrasyon Süreci
1. **Başlatma:** `python -m alembic init alembic`
2. **İlk Revizyon (Autogenerate):** `alembic/versions/*_create_users_table.py` oluşturuldu.
3. **Şema Yükseltme (Upgrade):** `python -m alembic upgrade head` komutu ile `users` tablosu ve `alembic_version` takip tablosu oluşturuldu.

### 7.3. Mimari Şeffaflık (Repository Pattern)
`UserModel` arayüzü (`get_all`, `get_by_id`, `create`, `update`, `patch`, `delete`) SQL sorguları çalıştıracak şekilde dönüştürülmüştür. Bu sayede hem `UserController` (`/users`) hem de `ApiUserController` (`/api/users`) kontrolcülerinde tek bir satır kod bile değiştirmeden kalıcı veritabanı desteğine geçilmiştir.

---

## 8. Veri Üretim Fabrikası ve Tohumlama (Factory & Seeder Pattern)

Geliştirme, yük testleri ve veri görselleştirmesi için Factory ve Seeder desenleri uygulanmıştır:

- **Factory Deseni ([`app/factory.py`](app/factory.py)):**
  - [`UserFactory`](app/factory.py): Gerçekçi Türkçe isimler, soyisimler, geçerli e-posta adresleri ve üniversite bölümleri kullanarak tekil veya toplu (`create_batch(count=50)`) sentetik veri üretir.
- **Veritabanı Tohumlayıcı ([`seed.py`](seed.py)):**
  - Komut satırından doğrudan çalıştırılabilir: `python seed.py --count 50`
  - Var olan kayıtları silip yeniden tohumlama desteği: `python seed.py --reset`
- **Web ve API Tetikleme:**
  - `POST /api/seed?count=50` uç noktası ve arayüzdeki "🌱 50 Mezun Ekle" butonu ile tek tıkla veritabanına 50 mezun tohumlanabilir.


