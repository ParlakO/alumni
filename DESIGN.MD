# 📐 AlumniTrack Design System Specification (DESIGN.MD)

> **Inspiration & Sources:** [`styles.refero.design`](https://refero.design) & [`VoltAgent/awesome-design-md`](https://github.com/VoltAgent/awesome-design-md)  
> **Project:** Istanbul University — Alumni Tracking System (AlumniTrack)  
> **Version:** 1.0.0  
> **Design Archetype:** Developer-First Modern Portal / Sleek Dark Glassmorphism  

---

## 📑 Table of Contents
- [1. Design Philosophy & Principles](#1-design-philosophy--principles)
- [2. Color System & Design Tokens](#2-color-system--design-tokens)
- [3. Typography System & Hierarchy](#3-typography-system--hierarchy)
- [4. Layout, Spacing & Elevation Grid](#4-layout-spacing--elevation-grid)
- [5. Component Specifications](#5-component-specifications)
  - [5.1. Navigation Bar (Navbar)](#51-navigation-bar-navbar)
  - [5.2. Hero Showcase Section](#52-hero-showcase-section)
  - [5.3. Metric & Stat Cards](#53-metric--stat-cards)
  - [5.4. Multi-Entity Tabs Navigation](#54-multi-entity-tabs-navigation)
  - [5.5. Data Tables & Grid Cards](#55-data-tables--grid-cards)
  - [5.6. Form Controls & Inputs](#56-form-controls--inputs)
  - [5.7. Modals & Dialog Windows](#57-modals--dialog-windows)
  - [5.8. Badges, Status Indicators & Toast Notifications](#58-badges-status-indicators--toast-notifications)
- [6. Micro-Interactions & Transitions](#6-micro-interactions--transitions)
- [7. Responsive Breakpoints](#7-responsive-breakpoints)
- [8. Accessibility Standards (WCAG 2.1 AA)](#8-accessibility-standards-wcag-21-aa)

---

## 1. Design Philosophy & Principles

Curated from high-performance developer tools on `styles.refero.design` and `VoltAgent/awesome-design-md`, AlumniTrack adheres to four foundational principles:

1. **Information Density with Breathing Room:**  
   Organizes relational data entities (`users`, `job_postings`, `applications`) without visual crowding by utilizing generous spacing and clear typographical hierarchy.
2. **Layered Depth & Glassmorphism:**  
   Uses semi-transparent surfaces (`backdrop-filter: blur(12px)`), hairline borders (`border: 1px solid rgba(255,255,255,0.08)`), and soft radial ambient gradients.
3. **Developer-Centric Technical Clarity:**  
   Displays HTTP status codes (`200 OK`, `201 Created`, `404 Not Found`, `409 Conflict`, `500 Server Error`), Alembic revision identifiers, and integrity constraints (`RESTRICT`, `UNIQUE`) prominently with monospace badges.
4. **Instant Action & Feedback Loop:**  
   Triggers real-time event logging in the interactive API console drawer and delivers animated toast feedback for all user mutations.

---

## 2. Color System & Design Tokens

Mapped directly to CSS Custom Properties in `app/static/style.css`:

```css
:root {
  /* Surfaces & Canvas */
  --bg-main: #090d16;                   /* Deep midnight canvas */
  --bg-card: rgba(17, 24, 39, 0.85);    /* Frosted glass card */
  --bg-card-hover: rgba(26, 36, 56, 0.95);
  --bg-surface: #131c2e;                /* Solid panel & modal base */
  --bg-input: #0c121e;                  /* Deep input field background */

  /* Hairline Borders */
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-focus: #6366f1;
  --border-hover: rgba(255, 255, 255, 0.16);

  /* Typographic Hierarchy */
  --text-main: #f8fafc;                 /* Primary high-contrast text */
  --text-muted: #94a3b8;                /* Secondary subtext */
  --text-dim: #64748b;                  /* Tertiary metadata / footnotes */

  /* Brand Accents */
  --primary: #4f46e5;                   /* Royal Indigo */
  --primary-hover: #4338ca;
  --primary-glow: rgba(79, 70, 229, 0.35);

  /* Functional & Semantic Tokens */
  --color-blue: #3b82f6;                /* GET endpoints, alumni entity */
  --color-purple: #8b5cf6;              /* Job postings (1:N) */
  --color-emerald: #10b981;             /* Applications (N:M), 201 Created */
  --color-amber: #f59e0b;               /* Warnings, PATCH, RESTRICT badge */
  --color-rose: #ef4444;                /* DELETE, 404, 409 Conflict, 500 */
  --color-cyan: #06b6d4;                /* Swagger UI / Documentation links */
}
```

---

## 3. Typography System & Hierarchy

| Token / Element | Font Family | Size | Weight | Line Height | Letter Spacing |
|:---|:---|:---|:---|:---|:---|
| **Hero Display** | Plus Jakarta Sans | `2.25rem (36px)` | 800 | 1.2 | `-0.03em` |
| **Section Title (H2)**| Plus Jakarta Sans | `1.5rem (24px)` | 700 | 1.3 | `-0.02em` |
| **Card Title (H3)** | Plus Jakarta Sans | `1.15rem (18px)` | 600 | 1.4 | `-0.01em` |
| **Body (Default)** | Plus Jakarta Sans | `0.92rem (14.7px)`| 400 | 1.6 | `0` |
| **Labels & Buttons** | Plus Jakarta Sans | `0.85rem (13.6px)`| 600 | 1.4 | `0` |
| **Monospace / Code**| JetBrains Mono | `0.78rem (12.5px)`| 500 / 700 | 1.4 | `0` |
| **Badges & Tags** | JetBrains Mono | `0.72rem (11.5px)`| 700 | 1.0 | `0.02em` |

---

## 4. Layout, Spacing & Elevation Grid

### 4.1. Spacing Scale (4px / 8px Grid)
- **4px (`0.25rem`):** Icon-to-text gap
- **8px (`0.5rem`):** Badge padding, button spacing
- **12px (`0.75rem`):** Table cells, compact inputs
- **16px (`1.0rem`):** Standard card padding
- **24px (`1.5rem`):** Grid column gap
- **32px (`2.0rem`):** Major section vertical spacing

### 4.2. Border Radius Tokens
- `--radius-sm: 8px` ➔ Buttons, inputs, inline badges
- `--radius-md: 12px` ➔ Table containers, dropdowns
- `--radius-lg: 16px` ➔ Stat cards, modal bodies
- `--radius-xl: 20px` ➔ Hero showcase container
- `Full (9999px)` ➔ Status pills and indicators

### 4.3. Shadows & Depth
```css
--shadow-card: 0 10px 30px -10px rgba(0, 0, 0, 0.5), 0 0 1px 1px rgba(255, 255, 255, 0.05);
--shadow-modal: 0 25px 50px -12px rgba(0, 0, 0, 0.75);
--primary-glow: 0 4px 14px rgba(79, 70, 229, 0.35);
```

---

## 5. Component Specifications

### 5.1. Navigation Bar (Navbar)
- **Positioning:** Sticky top (`position: sticky; top: 0; z-index: 50;`)
- **Aesthetic:** `background: rgba(9, 13, 22, 0.8)` with `backdrop-filter: blur(16px)`
- **Elements:** Brand logo, live health dot (`.pulse-dot`), Swagger `/docs` shortcut, Seed All (`🌱`), and quick action buttons.

### 5.2. Hero Showcase Section
- **Background:** Angled gradient (`135deg`) with subtle purple/indigo ambient glow.
- **Content:** Institutional accreditation tag, gradient headline, architectural pills (MVC, SQLite, Alembic, RESTRICT), and interactive shortcut cards.

### 5.3. Metric & Stat Cards
- 4-Column responsive grid: Registered Alumni (Blue), Active Postings (Purple), Submitted Applications (Emerald), Architecture (Amber).
- **Hover Micro-interaction:** `transform: translateY(-3px); border-color: rgba(99, 102, 241, 0.3);`

### 5.4. Multi-Entity Tabs Navigation
- Tabs: `🎓 Alumni`, `💼 Job Postings`, `📋 Applications`.
- Active State: Background `rgba(79, 70, 229, 0.2)`, border `#6366f1`, counter pill `#818cf8`.

### 5.5. Data Tables & Grid Cards
- **Table:** Alternating subtle hover states (`rgba(99, 102, 241, 0.06)`), monospace ID badges, and right-aligned actions.
- **View Toggle:** Seamless client-side switching between tabular and grid card representations.

### 5.6. Form Controls & Inputs
- **Base:** Deep background `--bg-input: #0c121e`, subtle border.
- **Focus:** `border-color: #6366f1; outline: none; box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25);`

### 5.7. Modals & Dialog Windows
- **Backdrop:** `background: rgba(0, 0, 0, 0.7)` with `backdrop-filter: blur(8px)`.
- **Slide Transition:** Animated smoothly on open (`@keyframes modalSlideIn`).

### 5.8. Badges, Status Indicators & Toast Notifications
- `POST` / `201`: Emerald green (`#34d399`)
- `GET` / `200`: Sky blue (`#60a5fa`)
- `PUT` / `PATCH`: Amber (`#fbbf24`) / Purple (`#c084fc`)
- `DELETE` / `404` / `409` / `500`: Coral red (`#f87171`)
- **Toasts:** Fixed bottom-right sliding notification cards with automatic 3s timeout.

---

## 6. Micro-Interactions & Transitions

```css
@keyframes pulseAnimation {
  0% { transform: scale(0.95); opacity: 0.7; }
  50% { transform: scale(1.3); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.7; }
}

@keyframes slideToast {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

@keyframes modalSlideIn {
  from { opacity: 0; transform: translateY(-20px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
```

---

## 7. Responsive Breakpoints

- **Mobile (`< 640px`):** Single-column stacked navbar, horizontal scroll on tables (`overflow-x: auto`), compact modal sizing.
- **Tablet (`640px - 1024px`):** 2x2 stat grid layout, adaptive modal width.
- **Desktop (`> 1024px`):** Max width `1300px`, 4-column metrics grid, side-by-side control filters.

---

## 8. Accessibility Standards (WCAG 2.1 AA)

- **Color Contrast:** All interface typography maintains at least a 4.5:1 contrast ratio against dark backgrounds.
- **Keyboard Navigation:** Explicit `focus-visible` rings for all interactive elements.
- **Semantic Structure:** Native semantic HTML5 landmarks (`header`, `nav`, `main`, `section`, `footer`).

---
*Compliant with styles.refero.design & VoltAgent/awesome-design-md standards.*
