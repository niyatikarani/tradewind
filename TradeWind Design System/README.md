# TradeWind — Design System

TradeWind is a **B2B export-operations SaaS** built for **Indian food & spice exporters**. It replaces the WhatsApp-forwards-and-spreadsheets workflow of a small export house with a single, AI-assisted operations hub: orders arrive in any format, an AI structures them, and every downstream step — quoting, sourcing, packing, documentation, container loading — becomes a tracked task with deadlines, warnings, and an audit trail.

The product voice is calm, operational, and trustworthy. It speaks to a busy manager ("Rahul at S&G Exports") and floor clerks ("Priya", "Suresh") who need to feel **in control at a glance**. The interface is information-dense but visually clean: a near-white slate UI, a single emerald accent, and a disciplined amber/red/green status language for order health.

---

## What this product does (surfaces)

TradeWind is **one web application** with several core surfaces:

1. **Dashboard** — the manager's "control room": KPI strip, active-order health, alerts, today's tasks, upcoming container deadlines, and a quick AI query box.
2. **AI Order Intake** — a chatbot-first interface where a manager/clerk drops in an order from any source (WhatsApp forward, typed message, PDF, image, voice-note transcript) and the AI extracts structured line items with confidence scores.
3. **Document Upload + AI Processing** — the file-upload variant of intake, showing the live extraction/processing state and a review screen with per-field confidence.
4. **Sales Order Detail** — the single most important page: full picture of one order (header KPIs, alert banners, line items, packaging config, documents, and a vertical timeline with an AI summary + natural-language query).
5. **Task Board** — Trello-like board auto-generated from Sales Orders; each order is a checklist card with progress, assignees, overdue/in-progress states, plus a collapsible SOP library.
6. **Vendor Price Entry** — log vendor prices after calls; stale-price warnings, price history, and a CSS bar chart of price trend.

**Already built elsewhere** (per the source brief — not rebuilt in this system): quote creation wizard, quote list, rule-engine pages, analytics dashboard, login. This design system documents the foundations so those and the new surfaces stay consistent.

---

## Sources

This design system was built from a **detailed written specification** (a set of "Claude design prompts" for TradeWind pages). There was **no codebase, Figma file, or design file attached** — the spec itself enumerated exact tokens (colors, font, icons, radii, shadows) and screen layouts, so the foundations below are transcribed from that spec rather than reverse-engineered from code.

- **No GitHub repo provided.**
- **No Figma URL provided.**
- **No brand logo provided** — the logo in `assets/` is an original placeholder wordmark (see Caveats). Replace with the real mark when available.

Because there's no source UI to diff against, the UI kit recreates the six specified screens faithfully to the written spec.

---

## Index — what's in this folder

| File / folder | What it is |
|---|---|
| `README.md` | This file — context, content & visual foundations, iconography, manifest. |
| `colors_and_type.css` | All color + type + spacing + radius + shadow tokens as CSS vars. The source of truth for foundations. |
| `assets/` | Logo (`logo.svg`), logomark (`logomark.svg`). |
| `preview/` | Small HTML cards that populate the Design System tab (colors, type, spacing, components). |
| `ui_kits/app/` | The TradeWind app UI kit — JSX components + an interactive `index.html` click-through prototype. |
| `SKILL.md` | Agent Skill manifest so this system can be used as a downloadable skill. |

UI kits:
- `ui_kits/app/` — the single TradeWind web application (Dashboard, AI Intake, Sales Order Detail, Task Board).

---

## CONTENT FUNDAMENTALS

**Voice:** operational, plain, and reassuring. The product is a colleague that has already done the work and is reporting back — not a marketing surface and not a chirpy assistant.

**Person:** The AI speaks in **first person** about what it did ("Got it. Extracted 2 line items.", "Updated. Changed cardamom SKU to CARD-BOLD-7MM."). It addresses the user implicitly ("Review the details on the right", "Shall I flag this for Rahul?"). Greetings are warm and named: "Good morning, Rahul · S&G Exports".

**Casing:** **Sentence case everywhere** — buttons ("Create Sales Order", "Save as Draft"), headers ("Extracted Order", "Order Timeline"), nav ("AI Intake", "Rule Engine"). Title Case is reserved for proper nouns (buyer names, SKUs, SOP titles like "Kosher Export Protocol"). **No ALL-CAPS in prose** — uppercase appears only as small eyebrow/label styling (KPI labels), never as written copy.

**Numbers & units:** Indian-format currency with lakh shorthand on dense surfaces — `₹14,82,000` in full, `₹14.8L` / `₹42L` in tables and KPIs. Quantities always carry units (`500 kg`, `200 kg`). Percentages for margin and utilisation (`12.4%`, `67%`). Confidence as a bare percent on a colored badge (`96%`, `81% — review`). Deadlines as **date + relative** ("Jan 14 · 8 days", "Jan 20 · 14 days").

**Status phrasing:** short, declarative, color-coded. "On Track", "At Risk", "Quote Sent", "Shipped", "Done". Warnings lead with the fact, then the consequence, then the suggested action: *"Container utilisation is 67% — below your 85% threshold. 58 more cartons fit. Consider adding volume or switching to a 10ft container."*

**AI explanations** are causal and concrete, never vague: *"FSSAI lab report was received on Jan 9 instead of Jan 7. Priya uploaded it immediately and packing resumed the same day."* The AI cites who/when and quantifies anomalies ("Sourcing is 2.4× slower than usual for this order").

**AI-native interaction patterns.** TradeWind is AI-first — the AI doesn't just answer, it *acts*. Three component patterns express this and recur across the product:
1. **Conversation / chat window** — the primary intake surface; user messages (emerald, right-aligned) and AI replies (logomark avatar, left-aligned) in a framed window with a live "Working" status.
2. **Action log ("executed on your behalf")** — an agentic run block listing the steps the AI took, each with a status: ✓ done (with a result like a SKU count or `PO-441`), ⟳ running (spinner), 🔒 blocked (red, with a Resolve affordance). Destructive/created actions expose **Undo**. This is how the AI is accountable for what it did.
3. **Clarifying question** — when the AI needs input before acting, it asks inline with an amber-bordered block: either selectable option rows (e.g. pick the right SKU, with a "Best match" recommendation) or a binary confirm (Yes/No buttons). The AI never silently guesses on low-confidence fields — it asks.

**Microcopy** is helpful and bounded: input placeholders describe scope ("Paste order text, describe an order, or ask anything…"), footnotes set expectations ("Usually completes in 8–15 seconds for a standard PO", "Changing a price here does not retroactively change existing quotes").

**Emoji:** **not used in product chrome.** The spec uses ✓/⚠/🚨/🔒 as shorthand, but in the rendered UI these are **Tabler icons**, not emoji. Status is communicated by icon + color + a text label, never by an emoji alone. Unicode arrows (↑ ↓) appear inline in metrics ("↑ 3 vs last month").

**Vibe:** a quietly competent operations tool. Dense but never cluttered; every number earns its place. No hype, no exclamation marks in system copy, no filler.

---

## VISUAL FOUNDATIONS

**Overall feel:** a light, calm, enterprise operations console. Reads as *crisp* — thin borders, generous-but-efficient spacing, one accent color. It is the opposite of a colorful consumer app: color is used almost entirely for **status meaning**, not decoration.

**Color:**
- **Neutrals do the work.** The whole UI is built from the slate ramp — page background `#f1f5f9` (slate-100), white surfaces, `#e2e8f0` borders, slate-900 text, slate-500 secondary, slate-400 muted.
- **Emerald is the only brand color** (`#10b981`, dark `#059669`). Used for: primary buttons, active nav (tinted bg `#ecfdf5` + 3px left border), links, progress bars on healthy orders, focus rings, the AI's left-border accent on its messages.
- **Status palette is strict and consistent across every surface:** green (`bg #dcfce7` / `text #16a34a`) = success/fresh/on-track; amber (`bg #fef3c7` / `text #d97706`) = warning/at-risk/needs-review; red (`bg #fee2e2` / `text #dc2626`) = error/overdue/critical/stale. A separate **override orange** (`#fd7e14`) marks manually-overridden values (e.g. a forced price) — it appears as a left border on a row + an indicator on the value.
- **No gradients.** Backgrounds are flat. No purple, no glassmorphism.

**Typography:** **Inter** throughout (400/500/600/700). Headings are tight (`-0.01em`), 16–20px. Body is 14px, dense tables drop to 13px. **SKUs and order numbers are monospace** (`CINN-STICKS-001`, `SO-2024-089`) — a deliberate signal that these are system identifiers. KPI/eyebrow labels are 12px uppercase with wide tracking. Big KPI numbers are 24–28px/700.

**Spacing & layout:** 4px base scale. Fixed **220px left sidebar** + **~60px topbar**, both persistent (fixed) chrome; main area scrolls. Pages are built from stacked sections and 2-column splits (e.g. 55/45 chat vs extracted-data, 60/40 order-detail vs timeline, 65/35 dashboard grid). KPI strips are equal-width card rows (3–5 across). Tables are full-width with a slate-50 header row.

**Cards:** the signature container — white bg, `1px #e2e8f0` border, **`10px` radius**, and a single soft shadow `0 1px 3px rgba(0,0,0,0.05)`. Cards rarely stack shadows; depth comes from the border. Alert/at-risk cards add a **colored left border** (amber/red, 3–4px) and a tinted background. AI messages use an **emerald left border** on a white card.

**Borders & dividers:** 1px slate-200 is the default seam — between table rows, around cards, under section headers. Stronger slate-300 only on hover/focus or inputs. Dashed borders signal *missing/needs-input* (red dashed on a not-found field; dashed amber line on a delayed timeline event; dashed border on an upload dropzone).

**Radii:** 6px (chips/badges), 8px (buttons/inputs), **10px (cards — the signature)**, 14px (large dropzones), full (pills, avatars, status dots).

**Shadows / elevation:** minimal. Card `0 1px 3px rgba(0,0,0,0.05)`; raised menus/popovers `0 4px 12px rgba(15,23,42,0.08)`; modals `0 20px 48px rgba(15,23,42,0.18)`. Focus uses an **emerald ring** `0 0 0 3px rgba(16,185,129,0.25)`, not a shadow.

**Badges & chips:** small, `6px` radius, tinted background + matching text color, 12–13px/500–600. Confidence badges follow a hard rule: **≥90% green, 70–89% amber, <70% red** (and a <70% field also gets a red dashed border). Status badges (On Track / At Risk / Pending / Shipped / Done) map to green / amber / slate / green / slate.

**Buttons:** primary = emerald fill, white text, 8px radius; secondary = white with slate-200 border + slate-700 text ("outline"); tertiary = muted text link. Disabled primaries dim (used for "Create Sales Order" until red fields resolve).

**Progress bars:** thin rounded track (slate-100) with a fill colored by health — emerald (on track), amber (at risk), slate (early/quote stage). Utilisation bars turn amber below threshold.

**Imagery & texture:** essentially none — this is a data tool. No hero photography, no illustrations, no patterns or grain. The only "imagery" is the logo, small avatar initials (colored circles with a letter), and CSS-drawn charts (bar charts built from divs, never canvas). Backgrounds are flat slate.

**Animation:** restrained and functional. Subtle fades/slide-ins on panels, a pulsing/animated progress bar during AI processing, hover transitions ~120–150ms. No bounces, no parallax, no decorative motion. Easing is standard ease / ease-out.

**Hover states:** surfaces lighten or pick up a slate-50 background; primary buttons darken to `#059669`; outline buttons gain a slate-300 border / slate-50 fill; nav rows tint toward emerald-50; links darken. **Press states:** subtle — a slightly darker fill, no scale-down on dense UI controls.

**Transparency / blur:** used sparingly — modal scrims and the occasional sticky-header backdrop. The product is opaque and solid by default; no frosted-glass aesthetic.

**Layout rules:** sidebar and topbar are fixed; content respects a max-width on very wide screens but is generally fluid. Alert banners are full-width at the top of their content region. The right rail (timeline, extracted-order panel, SOP library) is a fixed-proportion column, collapsible where noted.

---

## ICONOGRAPHY

**Icon system: [Tabler Icons](https://tabler.io/icons)** — used exclusively, via the **webfont CDN** (`ti ti-*` classes). Tabler is a 24×24, 2px-stroke, rounded-join outline set; its even stroke weight and friendly geometry match the calm, modern enterprise feel.

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3/dist/tabler-icons.min.css">
<i class="ti ti-brain"></i>
```

**Where icons appear & the canonical set:**
- **Sidebar nav:** `ti-layout-dashboard` (Dashboard), `ti-file-invoice` (Orders), `ti-brain` (AI Intake), `ti-file-text` (Quotes), `ti-checklist` (Tasks), `ti-chart-bar` (Analytics / Prices), `ti-settings` (Rule Engine).
- **AI / intake:** `ti-sparkles` (AI messages & insights), `ti-paperclip` (attach), `ti-send` (send), `ti-cloud-upload` (dropzone), `ti-loader-2` / spinner (processing).
- **Status:** `ti-circle-check` (done/success), `ti-alert-triangle` (warning), `ti-alert-circle` / `ti-exclamation-circle` (error/critical), `ti-lock` (blocked/restricted), `ti-clock` (overdue/time).
- **Content:** `ti-book` (SOP), `ti-bell` (notifications), `ti-plus` (add), `ti-chevron-down` (dropdowns), `ti-file-type-pdf` / `ti-photo` / `ti-file-spreadsheet` (file types), `ti-user` (avatar fallback).

**Stroke & sizing:** keep Tabler's native 2px stroke; size by font-size (16px inline, 18–20px nav, 48px in the upload dropzone). Color icons with the surrounding text color (`currentColor`) — status icons inherit their status text color (amber/red/green).

**Emoji:** **never** in product chrome. The spec's ✓/⚠/🚨/🔒 glyphs are realized as Tabler icons. **Unicode arrows** (↑ ↓) and the middot (·) separator are used in text metrics and meta rows — these are typographic, not iconographic.

**Avatars:** no photos — colored circles with a single initial (e.g. "P" for Priya, "S" for Suresh), `radius-full`, ~24px in task rows.

**Substitution note:** Tabler is loaded from CDN (no local copy was provided or required). If you need an offline build, install `@tabler/icons-webfont` and self-host the `dist/` fonts; class names are unchanged.

---

## Caveats

- **Placeholder logo.** No brand mark was provided; `assets/logo.svg` and `logomark.svg` are original placeholders (emerald rounded square + "trade route" strokes + Inter wordmark). Replace with the real logo.
- **Inter via CDN.** Loaded from Google Fonts (free/embeddable). No local font files were shipped; add `@tabler` + Inter to a local build if you need offline support.
- **Built from a written spec, not source code.** No Figma/codebase was available to diff against, so fidelity is to the documented spec.
