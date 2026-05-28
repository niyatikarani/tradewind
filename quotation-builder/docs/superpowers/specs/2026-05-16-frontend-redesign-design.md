# S&G Exports — Frontend Redesign: Design Spec
**Date:** 2026-05-16  
**Version:** 1.0

---

## 1. Goal

Replace Bootstrap 5 with an enterprise-grade design system. The result must look like a sellable B2B SaaS product — not a college project. No additional server or runtime beyond the existing FastAPI monolith.

---

## 2. Design Decisions

| Decision | Choice |
|---|---|
| Layout | Left sidebar (220px fixed) + sticky topbar |
| Default theme | Light (white sidebar, slate content area) |
| Dark mode | Available via 🌙/☀️ toggle in sidebar footer, persisted in localStorage |
| Accent color | Emerald — `#10b981` (primary), `#059669` (hover), `#ecfdf5` (tint) |
| Font | Inter (Google Fonts CDN) — 400, 500, 600, 700 weights |
| CSS framework | Tailwind CSS compiled via `npx tailwindcss` → `static/css/app.css` |
| JS interactivity | Alpine.js 3.x (CDN) — replaces Bootstrap JS for dropdowns, dark mode, modals |
| HTMX | Kept as-is for server-side partial updates |
| Chart.js | Kept as-is (CDN) |
| Icons | Heroicons (inline SVG) via Tailwind plugin or direct SVG snippets |

---

## 3. Color Palette

### Light Mode
| Token | Value | Usage |
|---|---|---|
| `bg-base` | `#f1f5f9` | Page background |
| `bg-sidebar` | `#ffffff` | Sidebar + cards |
| `bg-topbar` | `#ffffff` | Topbar |
| `border` | `#e2e8f0` | All borders |
| `text-primary` | `#0f172a` | Headings |
| `text-secondary` | `#64748b` | Labels, meta |
| `text-muted` | `#94a3b8` | Placeholders |
| `accent` | `#10b981` | Buttons, active states, links |
| `accent-hover` | `#059669` | Hover state |
| `accent-tint` | `#ecfdf5` | Active nav background |
| `accent-text` | `#065f46` | Active nav text |

### Dark Mode (toggled via `dark` class on `<html>`)
| Token | Value | Usage |
|---|---|---|
| `bg-base` | `#0f172a` | Page background |
| `bg-sidebar` | `#0f172a` | Sidebar |
| `bg-card` | `#1e293b` | Cards, topbar |
| `border` | `#334155` | All borders |
| `text-primary` | `#f1f5f9` | Headings |
| `text-secondary` | `#94a3b8` | Labels |
| `accent` | `#10b981` | Unchanged |
| `accent-tint` | `#10b98115` | Active nav bg |

---

## 4. Layout

```
┌──────────────────────────────────────────────────────┐
│  Sidebar (220px, fixed)  │  Topbar (sticky, full-w)  │
│  ┌──────────────────┐    │  Title   Search  [Btn]     │
│  │ Logo             │    ├────────────────────────────│
│  ├──────────────────│    │                            │
│  │ MAIN             │    │  KPI Cards (4-col grid)    │
│  │  📋 Quotes   ◉   │    │                            │
│  │  💰 Prices   ⚠7  │    │  Data Table / Form / Chart │
│  │  📊 Analytics    │    │                            │
│  ├──────────────────│    │                            │
│  │ CONFIG           │    │                            │
│  │  ⚙️ Rule Engine  │    │                            │
│  │  🗃️ Master Data  │    │                            │
│  │  👥 Users        │    │                            │
│  ├──────────────────│    │                            │
│  │ Avatar  Name  🌙 │    │                            │
│  └──────────────────┘    │                            │
└──────────────────────────────────────────────────────┘
```

---

## 5. Component Library

### Buttons
- **Primary:** `bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg px-4 py-2 text-sm font-semibold`
- **Outline:** `border border-slate-200 text-slate-600 hover:border-emerald-500 hover:text-emerald-600 rounded-lg px-3 py-2 text-sm`
- **Danger:** `bg-red-500 hover:bg-red-600 text-white rounded-lg px-4 py-2 text-sm font-semibold`

### Badges / Status Pills
- **Draft:** `bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400`
- **Confirmed:** `bg-emerald-100 text-emerald-700`
- **Cancelled:** `bg-red-100 text-red-600`
- **Stale Override:** `bg-amber-100 text-amber-700`
- **Stale Warning (inline):** `bg-red-100 text-red-600` with ⚠ icon

### Cards
- `bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-sm`

### Tables
- Header: `bg-slate-50 dark:bg-slate-800/50 text-xs font-semibold text-slate-500 uppercase tracking-wide`
- Row: `border-b border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30`
- Monospace quote numbers: `font-mono text-sm font-semibold text-slate-900`

### Form Inputs
- `bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none`

### KPI Cards
- 4-column grid on quotes/analytics pages
- Large stat number (24px, semibold, colored for status)
- Small label above (10px, uppercase, muted)
- Delta text below (10px, emerald for positive)

### Overridden Field Indicator
- `ring-2 ring-amber-400` on input + amber ✏ icon badge

---

## 6. Pages to Redesign (All 32 Templates)

| Module | Templates |
|---|---|
| Base | `base.html` — sidebar layout, dark mode toggle |
| Auth | `auth/login.html` — centered card, no sidebar |
| Quotes | `quotes/list.html`, `step1_client.html`, `step2_items.html`, `step3_review.html`, `step4_confirm.html`, `upload.html` |
| Prices | `prices/entry.html`, `bulk.html`, `stale.html`, `trends.html` |
| Rule Engine | `rule_engine/margin.html`, `factors.html`, `list_prices.html`, `countries.html`, `country_exceptions.html`, `clients.html`, `price_locks.html`, `cost_defaults.html`, `thresholds.html`, `currencies.html`, `containers.html`, `system.html`, `audit.html` |
| Analytics | `analytics/dashboard.html` |
| Admin | `admin/users.html`, `user_edit.html`, `master_data.html` |
| Components | `components/inline_price_form.html`, `upload_result.html` |
| Exports | `exports/quote_pdf.html` (print-optimized, no sidebar) |

---

## 7. Dark Mode Implementation

- Tailwind `darkMode: 'class'` config
- Alpine.js manages toggle: reads `localStorage.getItem('theme')` on load, sets `document.documentElement.classList.toggle('dark')`
- Toggle button in sidebar footer: 🌙 in light mode, ☀️ in dark mode
- All `dark:` variants defined in Tailwind classes

---

## 8. Build

```
# One-time setup (Node.js required for build only, NOT for runtime)
npm init -y
npm install -D tailwindcss

# Build (run before deploying or when changing templates)
npx tailwindcss -i static/css/input.css -o static/css/app.css --minify
```

- `static/css/input.css` — Tailwind directives + any custom CSS
- `static/css/app.css` — compiled output, committed to repo, served by FastAPI
- `tailwind.config.js` — content scan: `app/templates/**/*.html`
- Output size: ~15–25KB minified
- Node.js is NOT needed at runtime — only `app.css` is served

---

## 9. File Changes

| Action | File |
|---|---|
| Create | `tailwind.config.js` |
| Create | `static/css/input.css` |
| Replace | `static/css/app.css` (compiled output replaces `custom.css`) |
| Rewrite | `app/templates/base.html` |
| Rewrite | All 32 templates (new Tailwind classes, sidebar layout) |
| Update | `app/templates_cfg.py` — no change needed |
| Update | `static/css/custom.css` — replaced by `app.css` |
| Update | References to `custom.css` → `app.css` in `base.html` |

---

## 10. Non-Goals

- No React, Vue, or SPA — stays server-rendered Jinja2
- No separate frontend deployment
- No webpack, vite, or complex build pipeline
- No changes to routes, services, or database
- PDF export template (`quote_pdf.html`) keeps inline CSS for WeasyPrint compatibility
