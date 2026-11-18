# 🎓 AlumniTrack — Marka Kimliği Kılavuzu (brand.md)

Bu doküman, **İstanbul Üniversitesi Mezun Takip Sistemi (Alumni Tracking System / AlumniTrack)** projesinin kurumsal marka kimliğini, misyonunu, vizyonunu, iletişim tonunu, görsel tasarım standartlarını ve marka kullanım kurallarını tanımlar.

---

## 📑 İçindekiler
- [1. Marka Özeti ve Stratejisi](#1-marka-özeti-ve-stratejisi)
- [2. Marka Sesi ve İletişim Tonu (Tone of Voice)](#2-marka-sesi-ve-iletişim-tonu-tone-of-voice)
- [3. Logo ve Sembol Kılavuzu](#3-logo-ve-sembol-kılavuzu)
- [4. Kurumsal Renk Paleti (Color Tokens)](#4-kurumsal-renk-paleti-color-tokens)
- [5. Tipografi Standartları (Typography)](#5-tipografi-standartları-typography)
- [6. İkonografi ve Görsel Dil](#6-ikonografi-ve-görsel-dil)
- [7. Tasarım ve Kullanım Kuralları (Do's and Don'ts)](#7-tasarım-ve-kullanım-kuralları-dos-and-donts)

---

## 1. Marka Özeti ve Stratejisi

### 1.1. Marka Adı ve Pozisyonlama
- **Resmi Adı:** İstanbul Üniversitesi Mezun Takip Sistemi
- **Kısa Adı & Dijital Marka:** `AlumniTrack`
- **Slogan (Tagline):** *"Mezun Bilgi & Kariyer Ekosistemi — Akademi ile Sektör Arasındaki Güvenilir Köprü"*

### 1.2. Misyon (Mission)
İstanbul Üniversitesi mezunlarını tek bir çatı altında toplayarak; mezunlar, akademisyenler ve iş dünyası arasında şeffaf, güvenilir, modern ve doğrulanabilir bir iletişim ve istihdam ağı kurmak.

### 1.3. Vizyon (Vision)
Türkiye’nin en köklü üniversitesinin mezun gücünü çağdaş web teknolojileri, ilişkisel veri mimarisi ve açık standartlarla geleceğe taşıyan; uluslararası düzeyde referans kabul edilen bir mezun takip ekosistemi sunmak.

### 1.4. Temel Değerler (Core Values)
1. **Akademik Ciddiyet & Saygınlık:** Tarihsel mirasın getirdiği güveni dijital platforma yansıtmak.
2. **Şeffaflık ve Veri Güvenliği:** RESTful standartlar, güvenilir doğrulamalar ve ilişkisel bütünlük (`RESTRICT` ilkeleri).
3. **Çağdaşlık ve İnovasyon:** Modern kullanıcı deneyimi, cam morfolojisi (glassmorphism), hızlı yanıt süreleri.
4. **İş Birliği ve Topluluk:** Mezun-öğrenci mentörlüğü ve iş ilanı/başvuru köprüleri (1:N ve N:M ilişkileri).

---

## 2. Marka Sesi ve İletişim Tonu (Tone of Voice)

| Özellik | Açıklama | Örnek İfade |
|:---|:---|:---|
| **Profesyonel & Güven Verici** | Boş laftan uzak, net ve tutarlı bir dil kullanılır. | *"Mezun kaydınız başarıyla veritabanına işlendi."* |
| **Rehber & Destekleyici** | Kullanıcıyı hata anlarında suçlamaz; çözüm odaklı yol gösterir. | *"Aynı ilana daha önce başvurdunuz (409 Conflict). Başvurularım sekmesinden durumu inceleyebilirsiniz."* |
| **Akademik & Çağdaş** | Kurumsal saygınlık modern yazılım terminolojisi ile harmanlanır. | *"İlişkisel Veri Modeli: 1:N İş İlanları ve N:M Başvuru Eşleşmeleri"* |

### Tercih Edilen vs. Kaçınılan Terminoloji
- ✅ **Kullan:** *Mezun Portalı, Kariyer Ağı, İş İlanı, Aday Profili, Doğrulama, İlişkisel Kayıt*
- ❌ **Kaçın:** *Sıradan Kullanıcı, Eleman Arayanlar, Data Listesi, Çöp/Geçersiz Veri*

---

## 3. Logo ve Sembol Kılavuzu

### 3.1. Sembol Mimarisi
AlumniTrack logosu iki temel görsel metaforun kesişiminden oluşur:
1. **Mezuniyet Kepi (Mortarboard):** Akademik başarıyı, mezuniyet gururunu ve eğitimi simgeler.
2. **Ağ / Düğüm Bağlantıları (Network Node):** Mezunlar arasındaki kariyer bağını, ilişkisel veri tabanını ve topluluk etkileşimini temsil eder.

```
          ┌─────────/\─────────┐
          │        /  \        │  <-- Akademik Kep Metaforu
          │       /____\       │
          └─────────┬──────────┘
                    │ (Kariyer Bağı)
             ●──────┴──────●      <-- Mezun Ağları (1:N & N:M)
```

### 3.2. Koruma Alanı (Clear Space)
Logo çevresinde en az logo yüksekliğinin %25'i (`0.25H`) kadar boşluk bırakılmalıdır. Bu alana hiçbir metin veya grafik öğe giremez.

---

## 4. Kurumsal Renk Paleti (Color Tokens)

AlumniTrack, modern koyu tema (dark mode) odaklı, odaklanmayı artıran ve gözü yormayan premium bir renk paletine sahiptir.

### 4.1. Birincil ve Vurgu Renkleri
| Renk Rolü | Token Adı | HEX Kodu | RGB / HSL | Anlam & Kullanım |
|:---|:---|:---|:---|:---|
| **Primary Indigo** | `--primary` | `#4F46E5` | `rgb(79, 70, 229)` | Ana marka rengi, butonlar, birincil aksiyonlar |
| **Primary Hover** | `--primary-hover` | `#4338CA` | `rgb(67, 56, 202)` | Buton hover ve aktif durumları |
| **Emerald Growth** | `--color-emerald` | `#10B981` | `rgb(16, 185, 129)` | Başarı, tohumlama (seed), aktif başvuru |
| **Electric Purple** | `--color-purple` | `#8B5CF6` | `rgb(139, 92, 246)` | İş ilanları (1:N), kariyer özellikleri |
| **Cyber Cyan** | `--color-cyan` | `#06B6D4` | `rgb(6, 182, 212)` | Bilgi etiketleri, Swagger bağlantıları |
| **Amber Warning** | `--color-amber` | `#F59E0B` | `rgb(245, 158, 11)` | Uyarılar, PATCH işlemleri, RESTRICT kuralı |
| **Crimson Red** | `--color-rose` | `#EF4444` | `rgb(239, 68, 68)` | Hata, silme (DELETE), 5xx Guardian |

### 4.2. Yüzey ve Zemin Renkleri (Surface & Backgrounds)
| Yüzey | Token Adı | Değer | Açıklama |
|:---|:---|:---|:---|
| **Ana Arka Plan** | `--bg-main` | `#090D16` | Derin gece mavisi taban |
| **Kart Zemin** | `--bg-card` | `rgba(17, 24, 39, 0.85)` | Cam morfolojili yarı saydam kart |
| **Yüzey Katmanı** | `--bg-surface` | `#131C2E` | Modallar, tablolar, açılır menüler |
| **Girdi Kutusu** | `--bg-input` | `#0C121E` | Form inputları ve filtre alanları |

---

## 5. Tipografi Standartları (Typography)

Markanın tipografi hiyerarşisi netlik, modernlik ve okunabilirlik üzerine kurulmuştur.

### 5.1. Yazı Tipleri
- **Birincil Arayüz Fontu (Display & Body):** `Plus Jakarta Sans`  
  *Yedekler:* `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- **Kod ve Monospace Fontu (Code & Technical):** `JetBrains Mono`  
  *Kullanım:* ID'ler, HTTP metotları (`GET`, `POST`), REST rotaları, SQL sorguları.

### 5.2. Tipografi Ölçeği
- **Hero Title:** `2.25rem (36px)` / Weight: `800` / Line-height: `1.2`
- **Page Headings (H2):** `1.5rem (24px)` / Weight: `700` / Line-height: `1.3`
- **Card Headings (H3):** `1.15rem (18px)` / Weight: `600` / Line-height: `1.4`
- **Body Regular:** `0.92rem (14.7px)` / Weight: `400` / Line-height: `1.6`
- **Captions & Meta:** `0.78rem (12.5px)` / Weight: `500` / Line-height: `1.5`
- **Code & Badges:** `0.75rem (12px)` / Weight: `700` / Font: `JetBrains Mono`

---

## 6. İkonografi ve Görsel Dil

- **Çizgi Kalınlığı:** `stroke-width="2"` (Lucide / Feather standartları)
- **Köşe Bitimleri:** `stroke-linecap="round" stroke-linejoin="round"`
- **İkon Eşleşmeleri:**
  - 🎓 `Graduation Cap` ➔ Mezunlar (Alumni Entity)
  - 💼 `Briefcase` ➔ İş İlanları (Job Postings Entity)
  - 📋 `Clipboard` ➔ Başvurular (Applications Join Table)
  - ⚡ `Zap / Code` ➔ Swagger API & RESTful Endpoints
  - 🛡️ `Shield` ➔ 404 & 5xx Guardians
  - 🔗 `Link` ➔ 1:N & N:M İlişkisel Modeller

---

## 7. Tasarım ve Kullanım Kuralları (Do's and Don'ts)

### ✅ Yapılması Gerekenler (Do's)
- Arka plan ve kartlarda cam morfolojisi (backdrop-filter: blur) kullanarak modern derinlik hissini koruyun.
- Metin kontrastını WCAG 2.1 AA erişilebilirlik standartlarına uygun tutun (en az 4.5:1 kontrast oranı).
- Teknik veri parçalarını (ID, HTTP Status, JSON alanları) daima monospace font (`JetBrains Mono`) ve renkli badge ile gösterin.
- Butonlarda ve etkileşimli kartlarda hafif `translateY(-2px)` mikro animasyonu uygulayın.

### ❌ Kaçınılması Gerekenler (Don'ts)
- Birincil butonlarda aşırı doygun veya göz yoran neon renkler kullanmayın.
- Logoyu orantısız biçimde esnetmeyin, döndürmeyin veya düşük kontrastlı zeminlerde kullanmayın.
- Bildirim mesajlarında teknik yığın izini (stack trace) doğrudan son kullanıcı arayüzünde çıplak biçimde göstermeyin; 5xx Guardian üzerinden `logs/error.logs` dosyasına yönlendirin.

---
*AlumniTrack Marka Kimliği Kılavuzu — İstanbul Üniversitesi YBSB3001 Standartları.*
