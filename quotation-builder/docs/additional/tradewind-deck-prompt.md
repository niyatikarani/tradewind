# TradeWind — HTML Pitch Deck Prompt

> Paste the prompt below into a new Claude session with the instruction: **"Write the complete HTML file as described."**
> Output: single `.html` file, dark theme, 15 slides, printable to PDF via Cmd/Ctrl+P.

---

## PROMPT

Create a single self-contained HTML file: a 15-slide pitch deck for
TradeWind, printable to PDF via browser print (Cmd/Ctrl+P).

Each slide is a 16:9 page. On screen: slides stack vertically with
a dark chrome wrapper. On print: each slide is exactly one page,
landscape A4/Letter, no margins, no chrome.

---

## TECHNICAL REQUIREMENTS

- Single .html file, no external dependencies except Google Fonts
- Google Fonts: Inter (weights 400, 500, 600, 700) via @import in `<style>`
- `@page { size: landscape; margin: 0; }`
- Each slide: `<section class="slide">` — fixed 1280×720px on screen
- `@media print`: `.slide { width:100vw; height:100vh; page-break-after:always; }`
- No scrollbars inside slides
- Browser print button works — no extra plugin needed
- A small floating "Print" button (top-right, screen only, `display:none` on print) that calls `window.print()`

---

## DARK THEME DESIGN SYSTEM (use these tokens exactly)

```css
/* Surfaces */
--bg-page:      #0f172a;   /* slate-900 — main background */
--bg-card:      #1e293b;   /* slate-800 — card/panel surface */
--bg-hover:     #0f172a;   /* table row hover */
--bg-input:     #1e293b;   /* input background */
--bg-active-nav:#10b98115; /* active nav item tint */

/* Borders */
--border:       #334155;   /* slate-700 — card borders */
--border-soft:  #1e293b;   /* slate-800 — subtle dividers */

/* Text */
--text-primary:  #f1f5f9;  /* slate-100 */
--text-secondary:#94a3b8;  /* slate-400 */
--text-muted:    #475569;  /* slate-600 */
--text-body:     #94a3b8;

/* Accent — Emerald */
--accent:        #10b981;
--accent-dark:   #059669;
--accent-glow:   rgba(16,185,129,0.15);

/* Status badges (dark-adjusted) */
--badge-confirmed-bg:  rgba(16,185,129,0.15);
--badge-confirmed-text:#10b981;
--badge-draft-bg:      #1e293b;
--badge-draft-text:    #64748b;
--badge-warning-bg:    rgba(245,158,11,0.15);
--badge-warning-text:  #fbbf24;
--badge-error-bg:      rgba(239,68,68,0.15);
--badge-error-text:    #f87171;
--badge-override:      #fd7e14;  /* field-overridden orange */

/* Logo mark */
/* gradient: linear-gradient(135deg, #10b981, #059669) */
/* border-radius: 8px, white letter inside */

/* Buttons */
--btn-primary-bg:   #10b981;
--btn-primary-text: #ffffff;
--btn-outline-bg:   #1e293b;
--btn-outline-text: #94a3b8;
--btn-outline-border:#334155;

/* Typography */
/* Font: Inter */
/* KPI value: 28-32px, weight 700, --text-primary */
/* KPI label: 10px, uppercase, letter-spacing 0.5px, --text-muted */
/* Card title: 13px, weight 600, --text-primary */
/* Body: 12px, weight 400, --text-body */
/* Badge: 10px, weight 600, border-radius 20px, padding 2px 8px */
/* Table header: 10px, uppercase, letter-spacing 0.5px, --text-muted */
/* Table cell: 12px, --text-body */
/* Monospace IDs: font-family monospace, weight 600, --text-primary */

/* Cards */
/* background: --bg-card */
/* border: 1px solid --border */
/* border-radius: 10px */
/* padding: 16px */
/* box-shadow: 0 1px 3px rgba(0,0,0,0.3) */

/* Slide layout */
/* background: --bg-page */
/* padding: 48px 56px */
/* display: flex; flex-direction: column */

/* Slide header area */
/* slide-label: 10px, uppercase, letter-spacing 1px, --accent */
/* slide-headline: 24-28px, weight 700, --text-primary, max-width 75% */
/* slide-subhead: 14px, --text-secondary, margin-top 8px */
```

---

## SLIDE CONTENT (15 slides)

Build each slide to look like a real app UI mockup where the content describes it.
Use actual HTML elements (divs, tables, badges, cards) inside each slide —
not placeholder boxes. Every slide should feel like a real screen from the TradeWind product.

---

### SLIDE 01 — COVER

Layout: Two columns, 45/55 split.

**Left col** (centered vertically):
- Logo mark: 48px square, emerald gradient, border-radius 10px, white "TW" initials, weight 700
- Product name: "TradeWind" — 42px, weight 700, `--text-primary`
- Tagline: "From WhatsApp Order to Shipped Container — All in One." — 16px, `--text-secondary`, margin-top 12px
- Three small pill badges row (margin-top 32px): `[AI-Native]` `[India-First]` `[SMB-Ready]` — `--badge-confirmed-*` colors

**Right col:**
Mini app mockup (dark, matching design system):
- Three KPI cards in a row:
  - "Orders This Week: 14" (`--accent` value)
  - "Open Quotes: ₹42L" (`--text-primary` value)
  - "Container: 87% full" (`--badge-warning-text` value)
- Below: a 2-row mini table (quote list style):
  - SGE-0047 | Al Barakah | `[Draft]` badge
  - SGE-0046 | Euro Spices | `[Confirmed]` badge
- Wrap in a `--bg-card` rounded card with `--border` border

---

### SLIDE 02 — THE PROBLEM

**Slide label:** PROBLEM
**Headline:** "Indian spice exporters run on WhatsApp and Excel. It's breaking them."

Three cards in a row. Each card: `--bg-card`, `--border`, 10px radius.
Left border on each card: 3px solid `--badge-error-text` (#f87171).

**Card 1:**
- Label (uppercase muted): ORDER INTAKE
- Title: "Handwritten photos. Typed messages. No structure."
- Body: "Every order is a re-entry job. WhatsApp images, forwarded Excel files, voice notes — all manual, all error-prone."
- Bottom stat: "~45 min" in `--badge-warning-text`, label "per order, manually"

**Card 2:**
- Label: PRICING
- Title: "Cloves moved 8% last week. The quote didn't."
- Body: "Prices shift daily. Quotations built on last month's rates go out, deals are signed, then margins disappear."
- Bottom stat: "₹2–8L" in `--badge-error-text`, label "lost per mispriced shipment"

**Card 3:**
- Label: OPERATIONS
- Title: "4 tools. No integration. No audit trail."
- Body: "Excel for pricing. Tally for accounts. WhatsApp for orders. A standalone CBM calculator. A notepad for the rest."
- Bottom stat: "88%" in `--badge-error-text`, label "SME exporters on manual tools"

---

### SLIDE 03 — THE MARKET

**Slide label:** MARKET OPPORTUNITY
**Headline:** "A ₹2.4 lakh crore market. Zero purpose-built tooling."

**Left half:** Three stat blocks stacked (large KPI style):

| Value | Label |
|---|---|
| ₹2.4L Cr (`--accent`) | India food & spice export market (FY24) |
| 88% (`--badge-error-text`) | SME exporters still on manual tools |
| $95–500 (`--badge-warning-text`) | per user/month — cost of existing enterprise ERPs |

Dividers between stats: 1px `--border-soft`

**Right half:** `--bg-card`, `--border`, 10px radius, padding 24px

Title: "The gap" (13px 600)

Body (12px, `--text-body`, line-height 1.7):
> "The tools that exist — VISCO, Blue Link ERP — are built for Western enterprise importers.
> They cost more per user per month than what an Indian SME exporter pays their accountant.
>
> Eximly (the closest Indian player) covers compliance but has no AI intake, no packaging engine, no commodity intelligence.
>
> The market is large, the pain is real, and the gap is unoccupied."

Bottom: three small badges: `[No AI intake in market]` `[No packaging engine]` `[No SMB price point]` — `--badge-error-*`

---

### SLIDE 04 — THE SOLUTION (FLOW)

**Slide label:** SOLUTION
**Headline:** "One platform. Entire export workflow."

Horizontal flow diagram — 6 nodes connected by arrows. Center vertically in slide.

**Node style:** `--bg-card`, `--border`, border-radius 10px, padding 14px 18px, text-align center, min-width 140px.
Icon area: 28px circle, `--accent` bg, `--bg-page` icon char, border-radius 50%, centered above label.
Label: 12px, 600, `--text-primary`. Sublabel: 10px, `--text-muted`.

| # | Icon | Label | Sub |
|---|---|---|---|
| 1 | 📱 | Order Arrives | WA / Photo / PDF |
| 2 | 🤖 | AI Structures | Extract + validate |
| 3 | 📋 | Quotation | Live prices + margin |
| 4 | 📦 | Packaging | CBM + certification |
| 5 | 🧾 | Purchase Order | Auto-generated |
| 6 | 🚢 | Compliance Docs | Ship-ready |

Arrows between nodes: `→` in `--accent` color, 24px, weight 300.

Below diagram (centered, `--text-muted`, 12px, italic):
> "Each step feeds the next. No re-entry. No lost context."

---

### SLIDE 05 — AI ORDER INTAKE

**Slide label:** MODULE 1
**Headline:** "Any format. Any device. Structured in seconds."

**Left half:** Mock "Incoming Orders" panel (`--bg-card`, `--border`, 10px radius)

Panel header: "Incoming Orders" (13px 600 `--text-primary`) + "3 new" badge (`--badge-warning-*`)

Three rows (each: padding 12px 16px, border-bottom `--border-soft`):

**Row 1:**
- Icon chip: "IMG" (`--accent` bg, 20px, 8px text)
- "Al Barakah Trading" (12px 600) / "Handwritten order photo · 2 min ago" (10px muted)
- Extracted: "Cinnamon 500kg, Cardamom 200kg, 30 day delivery" (10px `--text-secondary`)
- Right badge: "94% confident" (`--badge-confirmed-*`)

**Row 2:**
- Icon chip: "MSG" (`--badge-warning-bg`, amber text)
- "Euro Spices GmbH" / "WhatsApp message · 8 min ago"
- Extracted: "Turmeric powder 1MT, FSSAI cert required"
- Right badge: "89% confident" (`--badge-confirmed-*`)

**Row 3:**
- Icon chip: "PDF" (`--bg-card`, `--text-muted`)
- "Saffron House UK" / "Excel upload · 24 min ago"
- Extracted: "⚠ 3 fields need review — qty unclear on row 4" (`--badge-warning-text`)
- Right badge: "Review" (`--badge-warning-*`)

**Right half:** 4 feature rows with emerald checkmark:
- ✓ Accepts WhatsApp images, voice notes, PDFs, forwarded messages
- ✓ AI extracts SKUs, quantities, delivery dates, special requirements
- ✓ Confidence scoring — low-confidence fields flagged, not silently wrong
- ✓ Buyer memory — remembers prior orders, usual terms, pricing tiers

Callout box below (`--accent` border-left 3px, `--bg-active-nav` bg, padding 12px 16px, border-radius 6px):
> "~₹15–40 per order at current AI API rates. Absorbed in Growth and Scale plan tiers."

---

### SLIDE 06 — QUOTATION BUILDER

**Slide label:** MODULE 2
**Headline:** "Live prices. Auto-populated. Margin-aware."

Full-width mock of quotation review screen inside the slide.

**Mock topbar** (`--bg-card`, `--border-soft` bottom, padding 10px 16px):
- Left: "Quote SGE-0047" (13px 600) + "Draft" badge (`--badge-draft-*`)
- Right: `[Send Quote]` button (`--btn-primary-*` style, small)

**KPI row** (4 cards, `--bg-page` bg, `--border`, 8px radius, padding 12px):
- "Total FOB" / "₹14,82,000" (`--text-primary`)
- "Margin" / "12.4%" (`--accent`)
- "FX Rate" / "₹83.4 / $1" (`--text-primary`)
- "Container" / "20ft — 67% full" (`--badge-warning-text`)

**Alert banner** (`--badge-warning-bg`, `--badge-warning-text`, border-radius 6px, padding 8px 14px):
> ⚠ Cinnamon price updated 6 days ago — verify before sending
>
> `[Update Price]` small outline button (right side)

**Table** (`--bg-card`, `--border`, 8px radius):

Headers: SKU | QTY | UNIT COST | PACK COST | MARGIN | LINE TOTAL

| Row | Notes |
|---|---|
| Cinnamon Sticks · 500 kg · ₹847/kg · ₹42/kg · 11.2% · ₹4,44,750 | Normal |
| Cardamom Bold · 200 kg · ₹2,680/kg ⚠ · ₹38/kg · 9.8% · ₹5,43,600 | **OVERRIDDEN** — left border 3px `--badge-override` orange, bg `rgba(253,126,20,0.08)`. Note below: "Market: ₹2,847/kg — overridden manually" (9px `--badge-override`) |
| Turmeric Powder · 100 kg · ₹184/kg · ₹18/kg · 14.1% · ₹22,200 | Normal |

---

### SLIDE 07 — PACKAGING CONFIGURATOR

**Slide label:** MODULE 3
**Headline:** "Cinnamon sticks aren't cardamom powder. The system knows."

**Left half:** Configurator panel (`--bg-card`, `--border`, 10px radius, padding 20px)

Product header: "Cinnamon Sticks — 500 kg order" (13px 600) + badge "Solid · Irregular shape" (`--badge-draft-*`)

Config rows (label left, value right, border-bottom `--border-soft`, padding 10px 0):

| Field | Value |
|---|---|
| Packaging | 100g Kraft Packets |
| Jar option | Toggle: OFF (`--text-muted`) |
| Label | Both sides · HQ print |
| Certification | `[Kosher]` `[FSSAI]` (emerald badges) |
| Sanitization | "Steam only" 🔒 — "Chemical options locked by Kosher cert" (9px `--text-muted`) |
| Packets/Carton | 24 packets |
| Carton dims | 42 × 28 × 28 cm · 2.4 kg |

**CBM bar** (margin-top 16px):
- Label: "Container utilization (20ft)"
- Bar: full-width, height 8px, `--bg-page` bg, border-radius 4px
- Fill: 62% width, `--accent`, border-radius 4px
- Below: "18.4 CBM used of 29.6 CBM" (10px `--text-muted`)
- Alert: "⚠ 11.2 CBM available — consider upsell" (10px `--badge-warning-text`)

**Right half:** Feature rows:
- ✓ SKU-aware rules — powder, sticks, grains, liquids handled differently
- ✓ Certification constraints — Kosher locks chemical treatment options
- ✓ Container dashboard — CBM vs booked, flag waste before booking

Callout box (`--accent` left-border 3px, `--bg-active-nav`):
> "Visual carton layout preview — shows packet arrangement inside carton, helps warehouse team verify before packing."

---

### SLIDE 08 — CERTIFICATION & COMPLIANCE ENGINE

**Slide label:** MODULE 4
**Headline:** "Kosher means steam only. The system enforces it automatically."

**Left half:** Processing steps panel (`--bg-card`, `--border`, 10px radius, padding 20px)

Header: "Active certifications on this order"
Badge row: `[Kosher]` `[FSSAI]` (both `--badge-confirmed-*`)

Steps list (icon + label + status chip):

| Step | Status |
|---|---|
| ✓ Cleaning | `[Allowed]` (`--badge-confirmed-*`) |
| ✓ Steam sanitization | `[Required · Kosher]` (`--accent` text, `--bg-active-nav` bg) |
| ✗ ~~Chemical fumigation~~ | `[Blocked]` (`--badge-error-*`) — "Prohibited under Kosher" (9px muted) |
| ✗ ~~Methyl bromide treatment~~ | `[Blocked]` (`--badge-error-*`) |
| ! Phytosanitary certificate | `[Required]` (`--badge-warning-*`) |
| ! COA lab test | `[Required · FSSAI]` (`--badge-warning-*`) |

**Right half:** Compliance table (`--bg-card`, `--border`, 8px radius):

| CERT | RESTRICTS | REQUIRES | AUTO-DOC |
|---|---|---|---|
| Kosher | Chemical treat | Steam, COA | ✓ |
| Halal | Alcohol contact | Halal cert | ✓ |
| Organic | Syn. fumigation | Organic cert | ✓ |
| FSSAI | — | Lab report | ✓ |
| APEDA | — | EIC reg | — |
| FDA | — | Prior notice | — |

Below table (11px `--text-muted`, italic):
> "Destination label rules — EU / GCC / US / UK — auto-applied based on shipping country on the order."

---

### SLIDE 09 — INVENTORY + COMMODITY INTELLIGENCE

**Slide label:** MODULE 5
**Headline:** "Stop calling dealers. Let the feed tell you."

**Left half:** Inventory card (`--bg-card`, `--border`, 10px radius, padding 20px)

Product header: "Cardamom Bold" (14px 700) + `[MCX LIVE]` chip (8px, `--accent` bg, white text)

Stock row: "840 kg on hand" · "Godown 2 · Kochi" (10px muted)

Price row (padding 14px 0, border-top/bottom `--border-soft`):
- Left: "Spot Price" (10px uppercase muted) / "₹2,847 / kg" (22px 700 `--text-primary`)
- Right: "↑ 6.2% this week" (12px 600 `--badge-error-text`) / "vs ₹2,680 last week" (10px muted)

Alert box (`--badge-error-bg`, `--badge-error-text` border-left 3px, padding 10px 14px, border-radius 6px, margin-top 12px):
> "3 open quotes priced below current market
> Potential margin loss: ~₹2.4L across quotes
> `[Review Quotes →]`" (`--accent` text, weight 600)

**Right half:** Features:
- ✓ Live MCX/NCDEX feed — price alerts before quotes go stale
- ✓ Lot/batch tracking — FIFO/FEFO, full traceability per shipment
- ✓ Predictive reorder — factors lead time, consumption, price volatility
- ✓ Multi-godown support with GST e-way bill generation

Reorder card (`--bg-card`, `--border`, 8px radius, padding 14px):
> "Reorder suggestion · Cardamom
> Current: 840 kg · Safety stock: 600 kg
> Suggested PO: 400 kg from Ramesh Agro, Coimbatore
> Trigger: Lead time 12 days, price trending up"

---

### SLIDE 10 — PURCHASE ORDERS

**Slide label:** MODULE 6
**Headline:** "Confirmed sale. Purchase list ready in 30 seconds."

**Top:** Sales Order trigger card (`--bg-card`, `--border`, 8px radius, border-left 3px `--accent`):
- "SO-2024-089" (monospace 12px 600) · "Al Barakah Trading" (`--text-secondary`) · `[Confirmed]` badge
- "500 kg Cinnamon Sticks · Kosher · 20 Jan delivery" (11px muted)

Arrow: "→ Auto-generated" (`--accent`, 12px, centered, margin 12px 0)

**Three output cards** in a row (`--bg-card`, `--border`, 10px radius, padding 16px):

**Card 1 — Raw Material PO:**
- Chip: "Raw Material PO" (10px uppercase muted)
- "Cinnamon Sticks — 520 kg" (13px 600) / "(incl. 4% wastage buffer)"
- Supplier: Ramesh Agro, Coimbatore
- Rate: ₹847/kg (MCX market) · Total: ₹4,40,440
- `[Auto-generated]` chip (`--badge-confirmed-*` small)

**Card 2 — Packaging PO:**
- Chip: "Packaging PO"
- 100g kraft packets × 5,200
- HQ labels × 5,200 (both sides)
- Outer cartons × 217 · Supplier: Annapurna Packaging · Total: ₹38,600

**Card 3 — Labour Estimate:**
- Chip: "Labour Estimate"
- Estimated: 3.2 working days · 8 workers required
- Lead time: 14 days — no rush surcharge
- "Packaging team notified ✓" (`--accent`, 11px)

---

### SLIDE 11 — COMPETITIVE LANDSCAPE

**Slide label:** MARKET POSITION
**Headline:** "The only AI-native player built for Indian food export."

Full-slide 2×2 matrix (centered, ~600×440px, `--bg-card`, `--border`, 12px radius, padding 32px):

**Axes:**
- X: "Generic" ←———→ "Food/Spice Export Domain" (`--text-muted`, 11px)
- Y: "Enterprise / Expensive" ↑ / ↓ "SMB-Friendly" (`--text-muted`, 11px, rotated -90deg)

Quadrant lines: 1px dashed `--border`

**Competitor dots** (18px circles, `--badge-draft-bg` fill, label below 10px):
- Top-left: VISCO / Blue Link
- Center: IncoDocs
- Bottom-left: Gallabox
- Bottom-right (near): Eximly

**TradeWind dot** (far bottom-right, 28px, `--accent` fill):
- `box-shadow: 0 0 16px rgba(16,185,129,0.4)`
- Label: "TradeWind" (12px 700 `--accent`)
- Sub: "AI-Native" (10px `--text-muted`)

Below matrix (11px `--text-muted`, italic):
> "Closest competitor (Eximly): compliance-strong, but no AI intake, no packaging engine, no commodity feeds."

---

### SLIDE 12 — WHY NOW

**Slide label:** TIMING
**Headline:** "Three forces converged. The window is open."

Three rows, full width, each: `--bg-card`, `--border`, 10px radius, padding 18px 24px, border-left 3px `--accent`.

**Row 1:**
- Left stat: "₹15/order" (28px 700 `--accent`) / "AI COST TODAY" (9px uppercase muted)
- Divider: 1px `--border` vertical, height 40px
- Body: "GPT-4o and Claude multimodal reduced handwriting extraction cost to ~₹15 per order. Two years ago this was technically impossible at SMB price points."

**Row 2:**
- Left stat: "77%" (28px 700 `--accent`) / "WHATSAPP ADOPTION"
- Body: "77% of Indian tier-2/3 business buyers use WhatsApp as their primary ordering channel. The intake channel already exists — we meet them where they already are."

**Row 3:**
- Left stat: "$24B" (28px 700 `--accent`) / "APEDA EXPORT TARGET"
- Body: "India's food export target. SME exporters carry the majority of volume. They have zero modern tooling to scale to this demand — TradeWind is that tooling."

---

### SLIDE 13 — PRICING

**Slide label:** BUSINESS MODEL
**Headline:** "10× cheaper than the alternative. Purpose-built, not retrofitted."

Three pricing cards horizontal, vertically centered. Base: `--bg-card`, `--border`, 12px radius, padding 24px.

**Card 1 — Starter:**
- Tier: "STARTER" (10px uppercase muted)
- Price: "₹9,999" (32px 700 `--text-primary`) + "/month"
- Features: Up to 30 orders/month · WhatsApp + image intake · Quotation builder · Basic packaging config · 1 user

**Card 2 — Growth (FEATURED):**
- Border: 1px solid `--accent`
- Shadow: `0 0 24px rgba(16,185,129,0.2)`
- Top badge: "MOST POPULAR" (`--accent` bg, white text, centered)
- Price: "₹24,999" (36px 700 `--accent`) + "/month"
- Features: Unlimited orders · Full packaging engine · PO + Purchase List automation · Commodity price alerts · 3 users + roles · Email support

**Card 3 — Scale:**
- Tier: "SCALE"
- Price: "₹49,999" (32px 700 `--text-primary`) + "/month"
- Features: MCX/NCDEX live feed · Full compliance suite · Unlimited users · API access · Priority support · Custom onboarding

**Comparison strip** below cards (`--bg-page`, padding 14px 24px, border-radius 8px, flex row, justify-between):
- Left: "VISCO Software: $95–125/user/month (~₹48,000 for 5 users)" + `[5× more expensive]` (`--badge-error-*`)
- Right: "TradeWind Growth: ₹24,999 flat for team" + `[India-first · AI-native]` (`--badge-confirmed-*`)

---

### SLIDE 14 — ROADMAP

**Slide label:** ROADMAP
**Headline:** "Shipping the core. Building the moat."

Horizontal timeline, 4 phases. Timeline bar: thin line connecting phases, `--border`. Phase nodes: circles above line.

**Phase 1 — NOW**
- Node: filled `--accent` circle
- Card border-top: 3px `--accent`
- Label: "PHASE 1 · NOW" (`--accent`)
- Title: "Core Platform"
- Items: AI order intake (WA, image, PDF) · Quotation builder + FX + margin · Basic packaging config · Sales order generation

**Phase 2 — Q3 2025**
- Node: `--badge-warning-bg` circle, `--badge-warning-text` border
- Card border-top: 3px `--badge-warning-text`
- Label: "PHASE 2 · Q3 2025" (`--badge-warning-text`)
- Title: "Full Platform"
- Items: Packaging configurator · PO + Purchase List · Inventory + lot tracking · Multi-user + notifications

**Phase 3 — Q4 2025**
- Node: `--border` circle
- Label: "PHASE 3 · Q4 2025" (`--text-muted`)
- Title: "Intelligence Layer"
- Items: MCX/NCDEX commodity feed · Compliance rules engine · ICEGATE/DGFT integration · Certification auto-docs

**Phase 4 — 2026**
- Node: `--border` dashed circle
- Label: "PHASE 4 · 2026" (`--text-muted`)
- Title: "Scale"
- Items: Demand forecasting · Supplier marketplace · Container optimization AI · API ecosystem

---

### SLIDE 15 — CLOSE

Layout: Full centered, generous whitespace. Center column max-width 600px, margin auto.

- Logo mark: 56px, emerald gradient, border-radius 12px, "TW" white 700, centered
- "TradeWind" (48px 700 `--text-primary`, centered, margin-top 20px)
- "The OS for Indian Food Export." (18px `--text-secondary`, centered, margin-top 8px)
- 40px vertical spacer
- CTA line (14px `--text-secondary`, centered) — customize for audience:
  - Option A (investor): "Seed round open. [ your contact ]"
  - Option B (pilot): "Join our pilot cohort — 3 months free."
  - Option C (co-founder): "[your pitch]"
- Bottom strip (absolute, bottom 40px, centered row, gap 12px):
  - `[88% SMEs on manual tools]` `[₹2.4L Cr market]` `[No AI-native competitor]`
  - Style: `--badge-confirmed-*` pills

---

## PRINT / SCREEN INSTRUCTIONS

**Screen:**
- Body bg: `#0a0f1e` (darker than slide bg for contrast)
- Slides centered, max-width 1280px, margin 40px auto
- Gap between slides: 32px
- Each slide: 1280×720px fixed, overflow hidden

**Print** (`@media print`):
- Body bg: none
- `.slide`: `width: 100vw; height: 100vh; page-break-after: always; margin: 0; padding: 40px 48px;`
- Hide: `.print-btn`
- `@page`: `{ size: A4 landscape; margin: 0; }`

**Print button** (screen only):
- Fixed top-right: 16px 16px
- `--btn-primary-*` style
- Label: "Print / Export PDF"
- `onclick="window.print()"`
- `z-index: 999`

---

## FINAL NOTES

- All content inside slides must be real HTML — not placeholder boxes or lorem ipsum
- Badges, tables, KPI cards, and alerts must use the exact tokens listed above
- Monospace font for IDs (SGE-0047, LOT-2024-112, SO-2024-089 etc.)
- No external images — use CSS shapes, gradients, and emoji icons only
- The HTML file should be standalone: save and open in any browser, Cmd+P to print to PDF
