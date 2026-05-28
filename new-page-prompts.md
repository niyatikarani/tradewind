# TradeWind — Claude Design Prompts for New Pages

These prompts are self-contained. Each one gives Claude everything it needs to produce a pixel-accurate HTML mockup using the TradeWind design system. Paste each prompt directly into Claude.

---

## How to use these prompts

Each prompt below is a standalone block. Paste it into Claude (web or API). Claude will return a single HTML file using Tailwind CDN + Tabler Icons CDN — no build step needed, opens in any browser.

---

---

# PROMPT 1 — Order Intake / AI Chat Interface

```
You are building a static HTML mockup for a B2B export operations SaaS called TradeWind.
This is the AI Order Intake page — the primary chatbot-first interface where a manager or clerk
drops in an order from any source (WhatsApp forward, PDF, typed message) and the AI structures it.

## Design system (use exactly these values)
- Font: Inter from Google Fonts (weights 400/500/600/700)
- Icons: Tabler Icons webfont CDN
- Page bg: #f1f5f9 (slate-100)
- Card bg: #ffffff, border: #e2e8f0, border-radius: 10px, shadow: 0 1px 3px rgba(0,0,0,0.05)
- Accent: #10b981 (emerald-500), Accent dark: #059669, Accent bg: #ecfdf5, Accent text: #065f46
- Text primary: #0f172a, Text secondary: #64748b, Text muted: #94a3b8
- Warning bg: #fef3c7, Warning text: #d97706
- Error bg: #fee2e2, Error text: #dc2626
- Success bg: #dcfce7, Success text: #16a34a

## Page layout
Full app shell: fixed left sidebar (220px wide) + topbar + main content area.

Sidebar nav items (use ti-* Tabler icon class):
- Dashboard (ti-layout-dashboard) — inactive
- Orders (ti-file-invoice) — inactive  
- AI Intake (ti-brain) — ACTIVE (bg: #ecfdf5, text: #10b981, left border 3px #10b981)
- Quotes (ti-file-text) — inactive
- Tasks (ti-checklist) — inactive
- Analytics (ti-chart-bar) — inactive
- Rule Engine (ti-settings) — inactive

Topbar: "AI Order Intake" title on left. Right side: badge showing "3 pending review" in amber.

## Main content — split layout (left 55% chat, right 45% extracted data panel)

### LEFT — Chat / Intake Stream
Header: "New Intake" with a small dropdown showing "Paste text / image URL / forward"

Show a conversation thread with these messages in order:

1. [SYSTEM bubble — slate bg] "Drop an order here. Paste a WhatsApp message, type it out, or paste an image URL. I'll extract the details."

2. [USER bubble — right aligned, emerald bg, white text] 
"Al Barakah wants 500kg cinnamon sticks, kosher, delivery by 14th Jan, FOB Mundra. Also 200kg cardamom bold. Payment 30 days LC."

3. [AI bubble — white card with emerald left border, sparkles icon]
"Got it. Extracted 2 line items from this message. Review the details on the right — I've flagged one thing for your attention."
Below the bubble, show 3 small chips: ✓ SKUs matched  ✓ Buyer found  ⚠ Delivery date needs confirm

4. [USER bubble — right aligned]
"The cardamom is actually Green Cardamom Bold 7mm, not standard. And delivery is 14th Jan CIF not FOB."

5. [AI bubble — white card with emerald left border]
"Updated. Changed cardamom SKU to CARD-BOLD-7MM and Incoterm to CIF Mundra. CIF affects the quote — freight and insurance will be your cost. Shall I flag this for Rahul to review before confirming?"
Below: two buttons — [Confirm & Create SO] (emerald filled) and [Assign to Rahul] (outline)

Below the chat, a fixed input bar at bottom of left panel:
- Text input placeholder: "Paste order text, describe an order, or ask anything..."
- Right side of input: paperclip icon button + send button (emerald)
- Small note below: "Supports WhatsApp text, voice note transcripts, email forwards, PDF text"

### RIGHT — Extracted Order Panel (live updating)

Header: "Extracted Order" + badge "Draft — pending confirm"

Section 1 — Buyer
Show a small card: "Al Barakah Trading · UAE · LC 30 days" with a green "Known buyer" badge and note "Last order: Nov 2024 · 3 orders total"

Section 2 — Line Items table
Columns: SKU | Description | Qty | Incoterm | Cert | Confidence
Row 1: CINN-STICKS-001 | Cinnamon Sticks | 500 kg | CIF | Kosher | green badge "96%"
Row 2: CARD-BOLD-7MM | Green Cardamom Bold 7mm | 200 kg | CIF | — | amber badge "81% — review"

Below table: small amber alert banner:
"⚠ CARD-BOLD-7MM has 3 similar SKUs — confirm this is the right one before creating SO."
With a small [Pick SKU] button.

Section 3 — Order Meta (key-value rows)
Delivery: 14 Jan 2025 · 22 days away
Port: Mundra (CIF)
Payment: LC 30 days
Container: Est. 20ft FCL (62% util. at current qty)

Section 4 — Actions
Two buttons stacked:
- [Create Sales Order] — emerald filled, full width
- [Save as Draft] — outline, full width

Below: small muted text "AI extracted from 2 messages · 3 fields confirmed by user · 1 pending"

## Confidence scoring visual rule
- 90%+ = green badge
- 70–89% = amber badge  
- Below 70% = red badge + field highlighted with dashed red border

Render as a complete single HTML file. Use inline Tailwind (CDN), Tabler Icons CDN, Inter font. No JS frameworks. Make it look like a real, polished SaaS product. Dark sidebar, light main area.
```

---

---

# PROMPT 2 — Order Task Board (Floor Execution View)

```
You are building a static HTML mockup for TradeWind, a B2B export ops SaaS for Indian food exporters.
This is the Task Board page — where the manager sees all active orders as task checklists, and
floor clerks mark steps done. Think Trello but auto-generated from Sales Orders.

## Design system
- Font: Inter (Google Fonts, 400/500/600/700)
- Icons: Tabler Icons webfont CDN
- Page bg: #f1f5f9
- Card: bg #fff, border #e2e8f0, radius 10px, shadow 0 1px 3px rgba(0,0,0,0.05)
- Accent: #10b981, Accent bg: #ecfdf5, Accent text: #065f46
- Text primary: #0f172a, secondary: #64748b, muted: #94a3b8
- Warn: bg #fef3c7, text #d97706 | Error: bg #fee2e2, text #dc2626 | Success: bg #dcfce7, text #16a34a

## App shell
Same sidebar as before. Active nav item: Tasks (ti-checklist icon).
Topbar: "Task Board" on left. Right: filter pills — [All] [My Tasks] [Overdue] [This Week] — "Overdue" pill in red.

## Main content

### Top KPI strip (3 cards in a row)
1. "Active Orders" — value: 4, sub: "3 on track · 1 at risk"
2. "Tasks Due Today" — value: 7, sub: "3 completed · 4 remaining", value in amber
3. "Blocked Tasks" — value: 2, sub: "Waiting on external docs", value in red

### Order Task Cards (vertical list, each order is one card)

---
CARD 1 — SO-089 · Al Barakah Trading
Top row: "SO-089" monospace + "Al Barakah Trading · UAE" + badge "On Track" (green) + "Container: Jan 14 · 8 days" on far right
Progress bar below: 6/9 tasks done — show a green progress bar at ~67%

Task checklist (use checkboxes, checked ones have strikethrough text, green check icon):
✅ Order received & structured (Jan 3 · auto)
✅ Quote sent to buyer (Jan 4 · Rahul)
✅ Quote accepted — SO raised (Jan 6 · auto)
✅ Vendor PO sent — Ramesh Agro (Jan 7 · Priya)
✅ Packaging material ordered (Jan 7 · Priya)
✅ Kosher cert attached to order (Jan 8 · Priya)
☐ Packing floor briefed — IN PROGRESS (amber, assigned: Suresh) — due Jan 10
☐ Packing complete & weighed — due Jan 12
☐ Container loaded & sealed — due Jan 14

Below checklist, small row: [+ Add Task] link (muted) | "SOP: Kosher Export" link (emerald, ti-book icon)

---
CARD 2 — SO-090 · Euro Spices GmbH (AT RISK — show amber left border on entire card)
Top row: "SO-090" + "Euro Spices GmbH · Germany" + badge "At Risk" (amber) + "Container: Jan 20 · 14 days"
Progress bar: 3/8 tasks done (~37%) — amber fill

Alert banner inside card (amber): "⚠ Sourcing is 2.4× slower than usual for this order. At current pace, packing won't start until Jan 16 — only 4 days before container."

Tasks:
✅ Order received (Jan 5 · auto)
✅ Quote accepted — SO raised (Jan 7 · auto)
✅ Vendor PO sent (Jan 8 · Priya)
☐ Raw material received — OVERDUE (red, was due Jan 10) — assigned: Suresh
☐ Packaging material received — due Jan 12
☐ Packing floor briefed — due Jan 14
☐ Packing complete — due Jan 17
☐ Container loaded — due Jan 20

---
CARD 3 — SO-091 · Saffron House UK (EARLY STAGE)
Top row: "SO-091" + "Saffron House UK · United Kingdom" + badge "Quote Sent" (slate/neutral) + "Container: Jan 28 · 22 days"
Progress bar: 2/8 tasks done (25%) — slate fill

Tasks:
✅ Order received & structured (Jan 6 · auto)
✅ Quote sent (Jan 7 · Rahul)
☐ Awaiting buyer confirmation — due Jan 10
☐ [remaining tasks greyed out — will unlock on SO creation]

---

### SOP Library panel (collapsible right panel, 260px wide, shown open)
Header: "SOP Library" with ti-book icon

Show 4 SOP cards (compact):
1. "Kosher Export Protocol" — 7 steps — badge "Active on SO-089"
2. "EU Labelling Requirements" — 5 steps — badge "Active on SO-091"
3. "Halal Certification Workflow" — 6 steps — muted
4. "FSSAI Documentation" — 4 steps — muted

Below: [+ Create SOP] button (outline)

## Key UX details
- Checked tasks: line-through on text, green check icon, muted text color
- Overdue unchecked tasks: red text, red clock icon, red bg chip
- In-progress tasks: amber bg chip, person's name shown
- Each task row has a tiny avatar/initial badge for assigned person

Render as complete single HTML file. Tailwind CDN, Tabler Icons CDN, Inter font. No JS. Make it look polished and real.
```

---

---

# PROMPT 3 — Sales Order Detail Page (with Timeline + Warnings)

```
You are building a static HTML mockup for TradeWind, a B2B export ops SaaS for Indian spice exporters.
This is the Sales Order Detail page — the single most important page in the system.
The manager opens this to get a complete picture of one order: status, timeline, tasks, packaging, documents.

## Design system
- Font: Inter (Google Fonts, 400/500/600/700)
- Icons: Tabler Icons webfont CDN  
- Page bg: #f1f5f9, Card: #fff border #e2e8f0 radius 10px shadow 0 1px 3px rgba(0,0,0,0.05)
- Accent: #10b981 | Warn: #d97706 bg #fef3c7 | Error: #dc2626 bg #fee2e2 | Success: #16a34a bg #dcfce7
- Override orange: #fd7e14

## App shell
Sidebar same as other pages. Active nav: Orders.
Topbar: breadcrumb "Orders / SO-2024-089" on left. Right side: [Edit] outline button + [Print Packing List] outline + [Download PDF] emerald button.

## Page content (full width, sections stacked)

### Section 1 — Order Header Card (full width)
Left side:
- "SO-2024-089" in large monospace (20px bold)
- "Al Barakah Trading · UAE" in slate-600
- Row of badges: green "Confirmed" + amber "Packing in Progress" + "Kosher" (emerald) + "CIF Mundra"

Right side (4 KPI mini-cards in a row):
- Total Value: ₹14,82,000
- Margin: 12.4% (emerald)
- Container: 20ft FCL · 67% full (amber — below threshold)
- Deadline: Jan 14 · 8 days (green)

---
### Section 2 — ALERT BANNERS (shown when there are active warnings)
Show two banners stacked:

Banner 1 (amber): "⚠ Container utilisation is 67% — below your 85% threshold. 58 more cartons fit. Consider adding volume or switching to a 10ft container."
With [Contact Buyer] and [Switch Container] buttons.

Banner 2 (amber): "⚠ Packing stage is running 1.8× longer than the average for this buyer. Container loading is Jan 14 — 8 days away."

---
### Section 3 — Two column layout (left 60% main, right 40% timeline)

LEFT COLUMN:

#### Line Items Table
Header: "Order Items" + small badge "2 SKUs"
Table columns: SKU | Description | Qty | Unit Price | Pack Format | Cert | Line Total
Row 1: CINN-STICKS-001 | Cinnamon Sticks | 500 kg | ₹296/kg | 100g kraft · 24/ctn | Kosher badge | ₹1,48,000
Row 2: CARD-BOLD-7MM | Green Cardamom Bold 7mm | 200 kg | ₹542/kg | 50g pouch · 48/ctn | — | ₹1,08,400
Footer row: Total — ₹14,82,000 (bold, right-aligned)
Note below: "Prices include packaging cost · FX locked at ₹83.4/$ on Jan 3 11:30 IST · RBI FBIL"

#### Packaging Summary Card
"Packaging Config" header
Key-value rows:
Container: 20ft FCL
Total cartons: 480
CBM utilisation: show an amber progress bar at 67% with "16.8 / 25.0 m³" label
Weight: 1,152 kg / 22,000 kg max

Processing constraints (3 chips):
✅ Kosher: no chemical treatment
🔒 Blocked: steam pasteurisation restricted
⚠ Required: COA attached before shipment

#### Documents Card
Header: "Required Documents" + "4/6 ready" badge
List:
✅ Commercial Invoice (auto-generated)
✅ Packing List (auto-generated)  
✅ Kosher Certificate — attached Jan 8
✅ FSSAI Lab Report — attached Jan 9
⚠ Certificate of Origin — pending (amber)
⚠ Phytosanitary Certificate — pending (amber)
[+ Upload Document] button at bottom

RIGHT COLUMN:

#### Order Timeline (vertical milestone list)
Header: "Order Timeline"

Events (top = newest):
🟡 Packing in progress — Jan 9, 2:30 PM · Suresh (current stage — amber)
✅ FSSAI cert attached — Jan 9, 10:45 AM · Priya
⚠ Packing delayed 2 days — Jan 9, 10:45 AM · [system] — dashed amber line + amber icon
   "FSSAI certificate arrived late. Packing restarted immediately."
✅ Packaging PO sent — Jan 7, 3:00 PM · Priya
✅ Raw material PO sent — Jan 7, 2:45 PM · Priya
✅ SO created — Jan 6, 11:20 AM · [auto on quote accept]
✅ Quote accepted by buyer — Jan 6, 11:18 AM
✅ Quote sent — Jan 4, 4:30 PM · Rahul
✅ Order structured by AI — Jan 3, 9:16 AM · [2 min from intake]
✅ Order received (WhatsApp) — Jan 3, 9:14 AM · Al Barakah

Below timeline:
AI Summary card (emerald left border):
"Received Jan 3 via WhatsApp. Quoted Jan 4, accepted Jan 6. Packing delayed 2 days on Jan 9 — FSSAI certificate arrived late. Resumed immediately. On track for Jan 14 container loading. No compliance issues."

NL Query input:
"Ask anything about this order..." with a send button
Below show a past query result:
Q: "Why was packing delayed?"
A: → "FSSAI lab report was received on Jan 9 instead of Jan 7. Priya uploaded it immediately and packing resumed the same day."

Render as complete single HTML file. Tailwind CDN, Tabler Icons CDN, Inter font. No JS. Dense, information-rich, but visually clean. Use the exact colors from the design system.
```

---

---

# PROMPT 4 — Dashboard (Manager's Control Room)

```
You are building a static HTML mockup for TradeWind, a B2B export ops SaaS for Indian food exporters.
This is the main Dashboard — the first page the manager sees. It should feel like a control room:
every active order's health, key metrics, upcoming deadlines, and alerts — at a glance.

## Design system
- Font: Inter (Google Fonts, 400/500/600/700), Icons: Tabler Icons webfont CDN
- Page bg: #f1f5f9, Card: #fff border #e2e8f0 radius 10px shadow 0 1px 3px rgba(0,0,0,0.05)
- Accent: #10b981 | Warn: #d97706 bg #fef3c7 | Error: #dc2626 bg #fee2e2 | Success: #16a34a bg #dcfce7

## App shell
Left sidebar 220px. Active: Dashboard (ti-layout-dashboard icon, emerald).
Top right corner of topbar: "Good morning, Rahul · S&G Exports" + notification bell with red dot showing "2".

## Page content

### Row 1 — KPI strip (5 cards)
1. Orders This Month: 14 · ↑ 3 vs last month (accent value)
2. Open Quotes: ₹42L · 3 awaiting buyer reply (accent)
3. Avg. Margin: 12.4% · ↑ 1.2pp vs last quarter
4. Container Utilisation: 87% · across active FCLs (green)
5. Overdue Tasks: 2 · needs attention (red value, red left border on card)

### Row 2 — Two alerts (full width, stacked)
Alert 1 (red): "🚨 SO-090 — Raw material delivery is 2 days overdue. Container date Jan 20 is now at risk."
Right side of alert: [View Order] button
Alert 2 (amber): "⚠ SO-089 — Container utilisation 67%, below your 85% threshold. 58 cartons of space unused."
Right side: [Contact Buyer] + [Dismiss] buttons

### Row 3 — Main grid (left 65% + right 35%)

LEFT:
#### Active Orders Table
Header: "Active Orders" (5) + [+ New Order] emerald button on right

Table: Order | Buyer | Stage | Value | Margin | Deadline | Status
SO-089 | Al Barakah · UAE | Packing | ₹14.8L | 12.4% | Jan 14 ↑8d | On Track (green badge)
SO-090 | Euro Spices · DE | Sourcing | ₹8.2L | 11.8% | Jan 20 ↑14d | At Risk (amber badge)
SO-091 | Saffron House · UK | Quote Sent | ₹6.1L | — | Jan 28 ↑22d | Pending (slate badge)
SO-088 | Gulf Traders · KW | Shipped | ₹22.4L | 13.1% | Shipped ✓ | Shipped (green)
SO-087 | Herb Direct · NL | Completed | ₹11.0L | 14.2% | Done ✓ | Done (slate)

Deadline column: color code — green if >10 days, amber if 5-10 days, red if <5 days

#### Today's Task Summary
Header: "Tasks Due Today" + "4 remaining / 7 total" badge

Show 4 task rows (each a small card row):
1. [amber chip "In Progress"] Brief packing floor — SO-089 · Assigned: Suresh · Due: today
2. [red chip "Overdue"] Confirm raw material receipt — SO-090 · Assigned: Priya · Was due: Jan 10
3. [slate chip "Pending"] Upload COA document — SO-089 · Assigned: Priya · Due: today
4. [slate chip "Pending"] Send revised quote v2 — SO-091 · Assigned: Rahul · Due: today

RIGHT:
#### Upcoming Deadlines (next 14 days)
Mini calendar-style list:

Jan 10 (TODAY)
- Packing floor briefed — SO-089 (amber dot)
- Upload COA — SO-089 (amber dot)

Jan 12
- Packing complete & weighed — SO-089 (green dot)

Jan 14 ← CONTAINER DATE
- Container loaded — SO-089 (red dot — critical)

Jan 20 ← CONTAINER DATE  
- Container loaded — SO-090 (amber dot — at risk)

#### Quick AI Input
Small card at bottom right:
"Ask TradeWind anything"
Input with placeholder: "e.g. What's the margin on SO-089? / Which orders have stale prices?"
Below: 3 suggestion chips: "Show at-risk orders" | "Stale vendor prices" | "This week's deadlines"

Render as complete single HTML file. Tailwind CDN, Tabler Icons CDN, Inter font. No JS. This should look like the kind of dashboard that makes a manager feel in control the moment they open it.
```

---

---

# PROMPT 5 — Vendor Price Entry + Stale Price Warning Screen

```
You are building a static HTML mockup for TradeWind, a B2B export ops SaaS for Indian spice exporters.
This is the Vendor Price Entry page — where the team logs prices after calling vendors.
It also shows the stale price warning state and the full price history for a SKU.

## Design system
- Font: Inter (Google Fonts, 400/500/600/700), Icons: Tabler Icons webfont CDN
- Page bg: #f1f5f9, Card: #fff border #e2e8f0 radius 10px shadow 0 1px 3px rgba(0,0,0,0.05)
- Accent: #10b981 | Warn: #d97706 bg #fef3c7 | Error: #dc2626 bg #fee2e2
- Override: #fd7e14

## App shell
Active nav: Prices (ti-chart-bar icon).
Topbar: "Vendor Prices" title. Right: badge "5 stale prices" in red + [Bulk Update] outline button.

## Main content — two column (left 55%, right 45%)

### LEFT — Price Entry Form

#### Stale Price Alert Banner (top, full width red)
"⚠ 5 SKUs have prices older than 5 days. Quotes using these prices are flagged and cannot be sent until confirmed."
[View all stale] button.

#### Recent Price Entries Table
Header: "Recent Entries" + "Last 30 days"
Columns: SKU | Description | Price | Vendor | Source | Date | Status

CINN-STICKS-001 | Cinnamon Sticks | ₹280/kg | Ramesh Agro | Vendor call | Jan 8 | green "Fresh" badge
CARD-BOLD-7MM | Cardamom Bold 7mm | ₹1,240/kg | Kerala Spices Co. | WhatsApp msg | Jan 7 | green "Fresh" badge  
BLK-PEPPER-002 | Black Pepper | ₹540/kg | Malabar Exports | Vendor call | Jan 3 | red "Stale 7d" badge + warning icon
TURMERIC-PWD-003 | Turmeric Powder | ₹145/kg | Rajasthan Agro | Manual entry | Dec 29 | red "Stale 11d" badge — override orange left border on row
CUMIN-SEEDS-004 | Cumin Seeds | ₹420/kg | Unjha Traders | Vendor call | Dec 27 | red "Stale 13d" badge

Note: TURMERIC row has override orange (#fd7e14) left border and its price cell shows the orange override indicator.

#### New Price Entry Form (card below table)
Header: "Log New Price" + small note "Enter after speaking with vendor"

Form fields in 2-column grid:
- SKU (dropdown, searchable) | Vendor Name (text)
- Price per kg (₹) | Currency (dropdown: INR/USD)
- Source (dropdown: Vendor Call / WhatsApp / Email / Market Rate) | Date (auto-filled today)
- Notes (text, optional, full width)

[Save Price] emerald button | [Save & Enter Another] outline button

Below form: small note in muted: "Prices are locked into quotes at save time. Changing a price here does not retroactively change existing quotes."

### RIGHT — SKU Price History (shown when a row is selected)

Header: "CINN-STICKS-001 · Cinnamon Sticks" + "Ramesh Agro (primary vendor)"

#### Price Chart (bar chart mockup)
Show a simple bar chart using divs (no canvas, just CSS bars) representing weekly price for last 8 weeks:
Bars: ₹265, ₹268, ₹271, ₹275, ₹278, ₹280, ₹280, ₹280
Last 3 bars are the same = flat trend. Color bars emerald. X axis: week labels. Y axis: show ₹260-₹285 range.
Below chart: "Current: ₹280/kg · 30-day avg: ₹275/kg · Trend: +1.9%"

#### AI Price Insight card (amber left border)
sparkles icon + "AI: Cinnamon Sticks prices have been stable for 3 weeks. Market data suggests a seasonal uptick in Feb — consider locking in your Q1 quotes before then."

#### Price History List (last 6 entries)
Each row: date | price | vendor | source | who entered | freshness
Jan 8 | ₹280/kg | Ramesh Agro | Vendor call | Priya | Fresh (green)
Jan 1 | ₹280/kg | Ramesh Agro | Vendor call | Priya | —
Dec 24 | ₹278/kg | Ramesh Agro | Vendor call | Priya | —
Dec 16 | ₹275/kg | Ramesh Agro | WhatsApp | Priya | —
Dec 9 | ₹271/kg | Kerala Spices | Vendor call | Priya | —
Dec 2 | ₹268/kg | Kerala Spices | Market rate | System | —

Below: "Prices shown are per kg at source (EXW). Freight and packaging are added separately in the quote engine."

Render as complete single HTML file. Tailwind CDN, Tabler Icons CDN, Inter font. No JS. Dense and data-rich but clean.
```

---

---

# PROMPT 6 — Order Intake via Document Upload (AI Processing State)

```
You are building a static HTML mockup for TradeWind, a B2B export ops SaaS.
This is the document upload + AI processing state page — shown when a user uploads a PDF,
image, or Excel file and the system is extracting order details from it.

## Design system
- Font: Inter (Google Fonts), Icons: Tabler Icons webfont CDN
- Same colors as all TradeWind pages (accent #10b981, page bg #f1f5f9, etc.)

## App shell
Active nav: AI Intake. Topbar: "AI Order Intake — Document Upload"

## Page content

### Upload Zone (top of page, full width card)
Large dashed border upload zone:
- ti-cloud-upload icon (large, 48px, emerald)
- "Drop a file here or click to upload"
- Supported: "PDF · Excel · JPG · PNG · Forwarded email (.eml)"
- Max file size: 10MB

Below upload zone, show 3 small "recently processed" chips:
"Euro Spices order Jan 5.pdf" (green check) | "Al Barakah WA screenshot.jpg" (green check) | "Saffron House PO.xlsx" (green check)

---

### Processing State Card (shown while AI is working)
Show a card that appears to be actively processing. Use a pulsing/animated feel through CSS.

Header: "Processing — Saffron House UK Purchase Order.pdf · 2.4 MB"
Progress bar (emerald, ~65% complete, animated width using CSS)

Step list showing AI processing stages:
✅ File received & validated
✅ Document type detected: Purchase Order
✅ Buyer identified: Saffron House UK (matched from buyer database)
⏳ Extracting line items... (spinner icon, amber text — in progress)
⬜ Matching SKUs to product catalog
⬜ Checking compliance requirements
⬜ Flagging fields for review

Below: "Usually completes in 8–15 seconds for a standard PO"

---

### Extracted Result Card (shown after processing — this is the main section)
Header: "Extraction Complete — Review before confirming" + amber "3 fields need review" badge

#### Confidence Summary Strip (4 mini stats)
- Fields extracted: 14 total
- High confidence (>90%): 10 fields (green)
- Needs review (70-90%): 3 fields (amber)
- Could not extract: 1 field (red)

#### Extracted Data (two column form, pre-filled by AI, editable)

LEFT — Order Header:
Buyer: [Saffron House UK] — green "Matched" badge
PO Number: [SHK-2024-0891] — green
Order Date: [Jan 6, 2025] — green
Delivery Date: [Jan 28, 2025] — amber badge "Confirm — read from footer, may be incorrect"
Incoterm: [FOB] — green
Destination Port: [Felixstowe, UK] — green
Payment Terms: [field shows blank + red "Not found — enter manually"] — red dashed border

RIGHT — Line Items (table, editable cells):
Show table with amber highlighted cells for low-confidence fields:
SKU | Matched | Qty | Unit | Confidence

Row 1: 
- PO says "Saffron Threads Grade A" → matched to SAFF-THREADS-A1 — 92% (green)
- Qty: 50 | Unit: kg — green

Row 2:
- PO says "Organic Turmeric Finger" → matched to TURMERIC-FNG-ORG — 88% (amber, highlighted cell)
- Qty: 150 | Unit: kg — green

Row 3:
- PO says "Mixed Herbs Pack" → matched to [dropdown showing 3 options, amber] — 61% (red) "Ambiguous — pick one"
- Qty: 80 | Unit: [amber — "packs or kg?"  — needs clarification]

#### Review Required Panel (right side, amber card)
Header: "3 fields need your attention"
List:
1. Payment Terms — not found in document. Required before SO creation.
2. Mixed Herbs Pack SKU — 3 possible matches. Pick the correct one.
3. Delivery date — extracted from PO footer which may be a printing date. Confirm Jan 28 is correct.

#### Actions
[Confirm & Create Sales Order] — emerald, disabled until red fields resolved
[Save Draft] — outline
[Re-upload Different File] — muted link

Below: "Original file preserved. You can always view the source PDF."

Render as complete single HTML file. Tailwind CDN, Tabler Icons CDN, Inter font. No JS. Clean, polished, professional. The amber/red field highlighting is critical — show it clearly.
```

---

---

# USAGE NOTES

**Tech stack for all prompts:** Pure HTML + Tailwind CDN + Tabler Icons CDN. No React, no build step. Opens directly in browser. Paste into Claude.ai or API.

**What's already built** (don't rebuild these — existing quotation-builder app covers them):
- Quote creation wizard (step1_client, step2_items, step3_review, step4_confirm)
- Quote list view
- Price entry (prices/entry.html, prices/stale.html)
- Rule engine pages (rule_engine/*)
- Analytics dashboard (analytics/dashboard.html)
- Login page (auth/login.html)

**New pages these prompts cover:**
1. AI Chat / Order Intake interface
2. Task Board (floor execution + SOP library)
3. Sales Order Detail (timeline + warnings + documents)
4. Manager Dashboard (control room view)
5. Vendor Price Entry with stale warnings (enhanced version)
6. Document Upload + AI Processing state

**After getting HTML from Claude:** Review for design consistency, then hand off to a developer to wire up to the backend with real data.
