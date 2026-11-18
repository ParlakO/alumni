# 🎓 AlumniTrack — Brand Identity Guidelines (brand.md)

This document defines the brand identity, core mission, vision, tone of voice, visual design standards, and brand governance rules for the **Istanbul University Alumni Tracking System (AlumniTrack)**.

---

## 📑 Table of Contents
- [1. Brand Overview & Strategy](#1-brand-overview--strategy)
- [2. Tone of Voice & Communication](#2-tone-of-voice--communication)
- [3. Logo & Symbol Guidelines](#3-logo--symbol-guidelines)
- [4. Color Palette & Design Tokens](#4-color-palette--design-tokens)
- [5. Typography Standards](#5-typography-standards)
- [6. Iconography & Visual Language](#6-iconography--visual-language)
- [7. Design Rules (Do's and Don'ts)](#7-design-rules-dos-and-donts)

---

## 1. Brand Overview & Strategy

### 1.1. Brand Name & Positioning
- **Official Name:** İstanbul Üniversitesi Mezun Takip Sistemi
- **Digital Brand:** `AlumniTrack`
- **Tagline:** *"Mezun Bilgi & Kariyer Ekosistemi — Connecting Graduates, Opportunities, and Academia"*

### 1.2. Mission
To bridge university graduates, academic departments, and the industry through a transparent, high-performance, and verifiable digital networking and career ecosystem.

### 1.3. Vision
To empower Istanbul University graduates worldwide with modern web technologies, relational data models (1:N & N:M), and open standards.

### 1.4. Core Values
1. **Academic Excellence & Trust:** Reflecting the historic prestige of Istanbul University in a modern digital platform.
2. **Relational Integrity:** Clean RESTful architecture, strict data integrity (`RESTRICT`), and validated inputs.
3. **Modern Elegance:** Frosted glass depth (glassmorphism), responsive layout, and instant feedback.
4. **Community & Growth:** Mentorship and career opportunities connecting alumni and active students.

---

## 2. Tone of Voice & Communication

| Characteristic | Description | Example |
|:---|:---|:---|
| **Authoritative & Professional** | Clear, concise, and academic. No fluff. | *"Graduate profile successfully registered in the database."* |
| **Supportive & Guiding** | Constructive error guidance without blaming the user. | *"You have already applied to this posting (409 Conflict). You can review your status under Applications."* |
| **Technical & Modern** | Blends academic dignity with modern software architecture. | *"Relational Model: 1:N Job Postings and N:M Applications"* |

---

## 3. Logo & Symbol Guidelines

### 3.1. Symbol Metaphor
AlumniTrack's logo icon unites two visual metaphors:
1. **Mortarboard (Graduation Cap):** Symbolizes academic achievement, graduation pride, and education.
2. **Network Nodes (Interconnection):** Symbolizes relational database integrity, career bonds, and community interaction.

```
          ┌─────────/\─────────┐
          │        /  \        │  <-- Graduation Cap
          │       /____\       │
          └─────────┬──────────┘
                    │
             ●──────┴──────●      <-- Network Connections (1:N & N:M)
```

### 3.2. Clear Space
Maintain a minimum clear space of `0.25H` around the logo mark, where `H` is the height of the icon.

---

## 4. Color Palette & Design Tokens

| Token Role | CSS Variable | Hex Code | Purpose |
|:---|:---|:---|:---|
| **Primary Indigo** | `--primary` | `#4F46E5` | Primary buttons, active tabs, main brand accents |
| **Primary Hover** | `--primary-hover` | `#4338CA` | Hover and active states for primary actions |
| **Emerald Growth** | `--color-emerald` | `#10B981` | Success states, seeder (seed data), active applications |
| **Electric Purple** | `--color-purple` | `#8B5CF6` | Job postings entity (1:N), career tags |
| **Cyber Cyan** | `--color-cyan` | `#06B6D4` | Information badges, Swagger /docs links |
| **Amber Warning** | `--color-amber` | `#F59E0B` | Warnings, PATCH operations, RESTRICT indicators |
| **Crimson Red** | `--color-rose` | `#EF4444` | Deletion (DELETE), 404, 409 Conflict, 5xx Guardian |
| **Canvas Background** | `--bg-main` | `#090D16` | Deep midnight canvas background |
| **Card Surface** | `--bg-card` | `rgba(17, 24, 39, 0.85)` | Glassmorphic cards with backdrop blur |

---

## 5. Typography Standards

- **Primary Interface Font:** `Plus Jakarta Sans` (Geometric, friendly, accessible)
- **Technical & Monospace Font:** `JetBrains Mono` (IDs, HTTP methods, endpoints, database fields)

### Type Hierarchy
- **Hero Title:** `2.25rem (36px)` / Weight: `800` / Line-height: `1.2`
- **Page Title (H2):** `1.5rem (24px)` / Weight: `700` / Line-height: `1.3`
- **Card Title (H3):** `1.15rem (18px)` / Weight: `600` / Line-height: `1.4`
- **Body Regular:** `0.92rem (14.7px)` / Weight: `400` / Line-height: `1.6`
- **Badges & Tags:** `0.75rem (12px)` / Weight: `700` (Monospace)

---

## 6. Iconography & Visual Language

- Stroke width: `2px`, line-cap: `round`, line-join: `round` (Lucide/Feather standard)
- Semantic Icons:
  - 🎓 `Graduation Cap` ➔ Alumni Entity
  - 💼 `Briefcase` ➔ Job Postings (1:N)
  - 📋 `Clipboard` ➔ Applications (N:M Join Table)
  - ⚡ `Zap` ➔ Swagger API & Utilities
  - 🛡️ `Shield` ➔ 404 & 5xx Guardians
  - 🔗 `Link` ➔ Relational Architecture

---

## 7. Design Rules (Do's and Don'ts)

### ✅ Do's
- Use frosted glass (`backdrop-filter: blur(12px)`) on card containers.
- Maintain WCAG 2.1 AA compliant color contrast (at least 4.5:1).
- Represent technical metadata (IDs, status codes, routes) with monospace badges.
- Include smooth micro-interactions (`transform: translateY(-2px)`) on interactive cards.

### ❌ Don'ts
- Do not use oversaturated neon colors on primary buttons.
- Do not expose raw exception stack traces in the UI; route them to `logs/error.logs` via 5xx Guardian.
- Do not distort or rotate brand icons without preserving aspect ratios.

---
*AlumniTrack Brand Identity Guidelines — Istanbul University YBSB3001 Standards.*
