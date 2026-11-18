# 📐 AlumniTrack Tasarım Sistemi Spesifikasyonu (DESIGN.MD)

> **Kaynak & İlham:** [`styles.refero.design`](https://refero.design) & [`VoltAgent/awesome-design-md`](https://github.com/VoltAgent/awesome-design-md)  
> **Proje:** İstanbul Üniversitesi — Mezun Takip Sistemi (Alumni Tracking System / AlumniTrack)  
> **Sürüm:** 1.0.0  
> **Tasarım Arketipi:** Modern Developer-First Enterprise Portal / Sleek Dark Glassmorphism  

---

## 📑 İçindekiler
- [1. Tasarım Felsefesi ve İlkeleri](#1-tasarım-felsefesi-ve-ilkeleri)
- [2. Renk Sistemi ve Tasarım Belirteçleri (Color Tokens)](#2-renk-sistemi-ve-tasarım-belirteçleri-color-tokens)
- [3. Tipografi Sistemi (Typography Scale)](#3-tipografi-sistemi-typography-scale)
- [4. Yerleşim, Boşluk ve Derinlik (Layout, Spacing & Elevation)](#4-yerleşim-boşluk-ve-derinlik-layout-spacing--elevation)
- [5. Bileşen Standartları (Component Specifications)](#5-bileşen-standartları-component-specifications)
  - [5.1. Gezinme Çubuğu (Navbar)](#51-gezinme-çubuğu-navbar)
  - [5.2. Hero Vitrin Bölümü (Hero Showcase)](#52-hero-vitrin-bölümü-hero-showcase)
  - [5.3. Metrik ve İstatistik Kartları (Stat Cards)](#53-metrik-ve-istatistik-kartları-stat-cards)
  - [5.4. Çoklu Varlık Sekme Yöneticisi (Tabs Navigation)](#54-çoklu-varlık-sekme-yöneticisi-tabs-navigation)
  - [5.5. Veri Tabloları ve Kart Izgaraları (Tables & Grid Cards)](#55-veri-tabloları-ve-kart-ızgaraları-tables--grid-cards)
  - [5.6. Form Elemanları ve Kontroller (Inputs & Forms)](#56-form-elemanları-ve-kontroller-inputs--forms)
  - [5.7. Modallar ve İletişim Pencereleri (Modals)](#57-modallar-ve-iletişim-pencereleri-modals)
  - [5.8. Rozetler, Durum Göstergeleri ve Toast Bildirimleri (Badges & Toasts)](#58-rozetler-durum-göstergeleri-ve-toast-bildirimleri-badges--toasts)
- [6. Mikro Etkileşimler ve Animasyonlar (Micro-Interactions)](#6-mikro-etkileşimler-ve-animasyonlar-micro-interactions)
- [7. Duyarlılık ve Kırılma Noktaları (Responsive Breakpoints)](#7-duyarlılık-ve-kırılma-noktaları-responsive-breakpoints)
- [8. Erişilebilirlik Standartları (WCAG 2.1 AA)](#8-erişilebilirlik-standartları-wcag-21-aa)

---

## 1. Tasarım Felsefesi ve İlkeleri

`styles.refero.design` kürasyonundaki modern B2B SaaS ve akademik/geliştirici platformlarından türetilen bu sistem, aşağıdaki 4 temel ilkeye dayanır:

1. **Yoğun Bilgi & Görsel Nefes Alanı (Information Density & Breathing Room):**  
   Mezunlar, iş ilanları (1:N) ve başvurular (N:M) gibi çok boyutlu ilişkisel veriler tablo ve kartlarla organize edilir; ancak her bir eleman net padding ve hiyerarşi ile ferah bir algı sunar.
2. **Katmanlı Derinlik & Buzlu Cam (Layered Depth & Glassmorphism):**  
   Yarı saydam yüzeyler (`backdrop-filter: blur(12px)`), ince kenarlıklar (`border: 1px solid rgba(255,255,255,0.08)`) ve yumuşak radyal degradeler kullanılarak modern bir arayüz derinliği sağlanır.
3. **Teknik Netlik (Developer-Centric Clarity):**  
   REST API yanıtları, HTTP durum kodları (`200`, `201`, `409`, `404`, `500`), Alembic migrasyon sürümleri ve veri kısıtlamaları (`RESTRICT`, `UNIQUE`) monospaced tipografi ve renkli rozetlerle daima görünür kılınır.
4. **Hızlı ve Geri Bildirim Odaklı Etkileşim (Instant Feedback):**  
   Her kullanıcı aksiyonunda (yeni mezun ekleme, başvuru yapma, tohumlama) canlı API konsol günlüğü ve toast bildirimleri tetiklenir.

---

## 2. Renk Sistemi ve Tasarım Belirteçleri (Color Tokens)

Sistem, `app/static/style.css` içindeki CSS özel değişkenleri (CSS Custom Properties) ile doğrudan eşlenir:

```css
:root {
  /* Zemin ve Yüzeyler */
  --bg-main: #090d16;                   /* Koyu ana tuval zemini */
  --bg-card: rgba(17, 24, 39, 0.85);    /* Yarı saydam kart gövdesi */
  --bg-card-hover: rgba(26, 36, 56, 0.95);
  --bg-surface: #131c2e;                /* Katı panel/modal zemini */
  --bg-input: #0c121e;                  /* Girdi alanları zemini */

  /* Kenarlıklar */
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-focus: #6366f1;
  --border-hover: rgba(255, 255, 255, 0.16);

  /* Metin Renkleri */
  --text-main: #f8fafc;                 /* 1. Derece metin (yüksek kontrast) */
  --text-muted: #94a3b8;                /* 2. Derece ikincil metin */
  --text-dim: #64748b;                  /* 3. Derece pasif / dipnot metin */

  /* Marka ve Vurgu */
  --primary: #4f46e5;                   /* Royal Indigo */
  --primary-hover: #4338ca;
  --primary-glow: rgba(79, 70, 229, 0.35);

  /* Fonksiyonel & Durum Renkleri */
  --color-blue: #3b82f6;                /* GET istekleri, mezun kimliği */
  --color-purple: #8b5cf6;              /* İş ilanları (1:N) */
  --color-emerald: #10b981;             /* Başvurular (N:M), 201 Created */
  --color-amber: #f59e0b;               /* PATCH güncellemeleri, uyarı */
  --color-rose: #ef4444;                /* DELETE, 404, 409 Conflict, 500 */
  --color-cyan: #06b6d4;                /* Swagger / API bağlantıları */
}
```

---

## 3. Tipografi Sistemi (Typography Scale)

| Token / Eleman | Yazı Tipi | Boyut | Ağırlık | Satır Yüksekliği | Harf Aralığı |
|:---|:---|:---|:---|:---|:---|
| **Hero Display** | Plus Jakarta Sans | `2.25rem (36px)` | 800 | 1.2 | `-0.03em` |
| **Section Title (H2)**| Plus Jakarta Sans | `1.5rem (24px)` | 700 | 1.3 | `-0.02em` |
| **Card Heading (H3)** | Plus Jakarta Sans | `1.15rem (18px)` | 600 | 1.4 | `-0.01em` |
| **Body (Default)** | Plus Jakarta Sans | `0.92rem (14.7px)`| 400 | 1.6 | `0` |
| **Label / Button** | Plus Jakarta Sans | `0.85rem (13.6px)`| 600 | 1.4 | `0` |
| **Monospace / Code**| JetBrains Mono | `0.78rem (12.5px)`| 500 / 700 | 1.4 | `0` |
| **Badge / Tag** | JetBrains Mono | `0.72rem (11.5px)`| 700 | 1.0 | `0.02em` |

---

## 4. Yerleşim, Boşluk ve Derinlik (Layout, Spacing & Elevation)

### 4.1. Boşluk Skalası (Spacing Grid)
- **4px (`0.25rem`):** İkon-metin arası mikro boşluk
- **8px (`0.5rem`):** Rozet içi padding, buton yatay aralığı
- **12px (`0.75rem`):** Tablo hücreleri, kompakt form elemanları
- **16px (`1.0rem`):** Standart kart içi kenar boşluğu
- **24px (`1.5rem`):** Grid kartları arasındaki sütun aralığı
- **32px (`2.0rem`):** Sayfa bölümleri (section) arasındaki boşluk

### 4.2. Köşe Yuvarlama (Border Radius)
- `--radius-sm: 8px` ➔ Butonlar, etiketler, form girdileri
- `--radius-md: 12px` ➔ Tablo konteyneri, açılır menüler
- `--radius-lg: 16px` ➔ İstatistik kartları, modal gövdeleri
- `--radius-xl: 20px` ➔ Hero paneli
- `Full (9999px)` ➔ Rozet hapları (pills), durum indikatörleri

### 4.3. Gölgeler ve Derinlik (Elevation & Shadows)
```css
--shadow-card: 0 10px 30px -10px rgba(0, 0, 0, 0.5), 0 0 1px 1px rgba(255, 255, 255, 0.05);
--shadow-modal: 0 25px 50px -12px rgba(0, 0, 0, 0.75);
--primary-glow: 0 4px 14px rgba(79, 70, 229, 0.35);
```

---

## 5. Bileşen Standartları (Component Specifications)

### 5.1. Gezinme Çubuğu (Navbar)
- **Konum:** Sayfa üstünde sabit (`position: sticky; top: 0; z-index: 50;`)
- **Görsel:** Yarı saydam `rgba(9, 13, 22, 0.8)` + `backdrop-filter: blur(16px)`
- **İçerik:** AlumniTrack marka logosu, canlı API sağlık nabzı (`.pulse-dot`), Swagger `/docs` kısayolu, Tohumlama (`🌱 Seed All`) ve Hızlı Ekleme butonları.

### 5.2. Hero Vitrin Bölümü (Hero Showcase)
- **Arka Plan:** `linear-gradient(135deg, rgba(17, 24, 39, 0.95), rgba(30, 27, 75, 0.75), rgba(15, 23, 42, 0.95))`
- **Öğeler:** Üniversite kurumsal rozeti, degrade başlık (`gradient-text`), mimari etiket hapları (MVC, SQLite, Alembic, RESTRICT) ve Swagger/MVC hızlı eylem kartları.

### 5.3. Metrik ve İstatistik Kartları (Stat Cards)
- 4 Sütunlu Grid: Kayıtlı Mezunlar (Mavi), Aktif İlanlar (Mor), Yapılan Başvurular (Zümrüt), Sistem Mimarisi (Kehribar).
- **Hover Etkisi:** `transform: translateY(-3px); border-color: rgba(99, 102, 241, 0.3);`

### 5.4. Çoklu Varlık Sekme Yöneticisi (Tabs Navigation)
- `🎓 Mezunlar (Alumni)`, `💼 İş İlanları (Job Postings)`, `📋 Başvurular (Applications)`.
- Aktif sekme: Zemin `rgba(79, 70, 229, 0.2)`, kenarlık `#6366f1`, sayaç hapı `#818cf8`.

### 5.5. Veri Tabloları ve Kart Izgaraları (Tables & Grid Cards)
- **Tablo:** Zebra şeritleme yerine saydam `rgba(255, 255, 255, 0.02)` arka plan ve `border-bottom: 1px solid var(--border-subtle)`.
- **Satır Hover:** `background: rgba(99, 102, 241, 0.05)`.
- **Görünüm Değiştirici:** Tablo görünümü ile Kart ızgara görünümü arasında anlık dinamik geçiş.

### 5.6. Form Elemanları ve Kontroller (Inputs & Forms)
- **Zemin:** Derin siyah `--bg-input: #0c121e`, kenarlık `--border-subtle`.
- **Focus:** `border-color: #6366f1; outline: none; box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);`
- **Method Toggle:** `PUT` (sarı rozet) ve `PATCH` (mor rozet) seçenekleri radyo kartları şeklinde.

### 5.7. Modallar ve İletişim Pencereleri (Modals)
- **Perde (Backdrop):** `background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(8px);`
- **Modal Kart:** Yumuşak kayma animasyonu (`@keyframes modalSlideIn`).

### 5.8. Rozetler, Durum Göstergeleri ve Toast Bildirimleri (Badges & Toasts)
- `POST` / `201`: Zümrüt yeşili (`#34d399`)
- `GET` / `200`: Gökyüzü mavisi (`#60a5fa`)
- `PUT` / `PATCH`: Kehribar sarısı (`#fbbf24`) / Menekşe moru (`#c084fc`)
- `DELETE` / `404` / `409` / `500`: Parlak mercan kırmızısı (`#f87171`)
- **Toast:** Sağ alttan `slideToast` animasyonuyla gelen 3 saniyelik otomatik kapanan kartlar.

---

## 6. Mikro Etkileşimler ve Animasyonlar (Micro-Interactions)

```css
/* Canlı Nabız Göstergesi */
@keyframes pulseAnimation {
  0% { transform: scale(0.95); opacity: 0.7; }
  50% { transform: scale(1.3); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.7; }
}

/* Toast Giriş */
@keyframes slideToast {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

/* Modal Açılış */
@keyframes modalSlideIn {
  from { opacity: 0; transform: translateY(-20px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
```

---

## 7. Duyarlılık ve Kırılma Noktaları (Responsive Breakpoints)

- **Mobil (`< 640px`):** Navbar tek sütuna iner, butonlar ikon ağırlıklı olur, tablo yatay kaydırılabilir (`overflow-x: auto`).
- **Tablet (`640px - 1024px`):** 4 sütunlu istatistik gridi 2x2 matrise geçer, modal genişliği %90'a oturur.
- **Masaüstü (`> 1024px`):** Maksimum genişlik `1300px`, 4 sütunlu tam grid, yan yana kontroller.

---

## 8. Erişilebilirlik Standartları (WCAG 2.1 AA)

- **Kontrast:** Koyu zemin üzerindeki tüm metinler en az 4.5:1 kontrast oranını sağlar (`#f8fafc` ve `#cbd5e1`).
- **Klavye Odaklanması:** Tüm buton ve girdi elemanlarında belirgin `focus-visible` halkası mevcuttur.
- **Semantik HTML:** Yapısal etiketler (`<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`, `<dialog>/<modal>`) standartlara uygun hiyerarşiyle kullanılır.

---
*Referans: styles.refero.design & VoltAgent/awesome-design-md spesifikasyonlarına tam uyumludur.*
