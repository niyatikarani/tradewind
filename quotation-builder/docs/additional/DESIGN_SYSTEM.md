# TradeWind / S&G Exports — Design System Reference

> Source-of-truth export for migrating to React + Vite + Tailwind (shadcn/ui).  
> Derived from: `quotation-builder` app (Tailwind) and `ppt.html` pitch deck (CSS vars).  
> Last updated: 2026-05-23

---

## 1. Design Tokens

### 1.1 Color Palette

| Token name | Hex | Tailwind equivalent | Usage |
|---|---|---|---|
| `--accent` | `#10b981` | `emerald-500` | Primary action, active nav, chart bars, progress fills |
| `--accent-dark` | `#059669` | `emerald-600` | Hover state for accent |
| `--accent-bg` | `#ecfdf5` | `emerald-50` | Badge bg, icon bg, active nav bg |
| `--accent-text` | `#065f46` | `emerald-900` | Text on accent-bg |
| `--bg-page` | `#f1f5f9` | `slate-100` | Page / app background |
| `--bg-surface` | `#ffffff` | `white` | Card, panel, input background |
| `--border` | `#e2e8f0` | `slate-200` | Card borders, table dividers |
| `--divider` | `#f1f5f9` | `slate-100` | Table row separators |
| `--text-primary` | `#0f172a` | `slate-900` | Headings, data values, labels |
| `--text-secondary` | `#64748b` | `slate-500` | Body text, descriptions |
| `--text-muted` | `#94a3b8` | `slate-400` | Eyebrows, sub-labels, timestamps |
| `--warn-bg` | `#fef3c7` | `amber-100` | Warning alert bg, pending badge bg |
| `--warn-text` | `#d97706` | `amber-600` | Warning text |
| `--error-bg` | `#fee2e2` | `red-100` | Error alert bg, stale badge bg |
| `--error-text` | `#dc2626` | `red-600` | Error text |
| `--success-bg` | `#dcfce7` | `green-100` | Success badge bg |
| `--success-text` | `#16a34a` | `green-600` | Success text |
| `--override` | `#fd7e14` | `orange-500`* | Manually overridden field highlight |

> **\* Override orange:** Tailwind `orange-500` is `#f97316` — close but not identical. Add to `tailwind.config.js`:
> ```js
> extend: { colors: { override: '#fd7e14' } }
> ```

### 1.2 Dark Mode Tokens

| Light | Dark Tailwind class |
|---|---|
| `bg-white` (card) | `dark:bg-slate-800` |
| `bg-slate-100` (page) | `dark:bg-slate-900` |
| `border-slate-200` | `dark:border-slate-700` |
| `text-slate-900` | `dark:text-slate-100` |
| `text-slate-500` | `dark:text-slate-400` |
| `text-slate-400` | `dark:text-slate-500` |
| `bg-emerald-50` | `dark:bg-emerald-950/30` |
| `text-emerald-700` (badge) | `dark:text-emerald-400` |
| `bg-red-50` | `dark:bg-red-950/30` |
| `bg-amber-100` | `dark:bg-amber-950/50` |
| `bg-slate-50` (table header) | `dark:bg-slate-800/50` |

Dark mode is toggled via `class="dark"` on `<html>`. Toggle stored in `localStorage` key `theme`.

```tsx
// ThemeToggle.tsx
const toggle = () => {
  const isDark = document.documentElement.classList.toggle('dark')
  localStorage.setItem('theme', isDark ? 'dark' : 'light')
}
// On mount: 
if (localStorage.getItem('theme') === 'dark') document.documentElement.classList.add('dark')
```

### 1.3 Typography

| Style | Tailwind | Notes |
|---|---|---|
| Font family | `font-['Inter']` | Google Fonts, weights 400/500/600/700 |
| Eyebrow | `text-[10px] font-medium uppercase tracking-[1px] text-slate-400` | Section labels above headings |
| Page heading | `text-lg font-semibold text-slate-900 dark:text-slate-100` | Topbar title |
| Slide headline | `text-[22px] font-bold text-slate-900 leading-[1.3]` | Deck slide headings |
| Card title | `text-sm font-semibold text-slate-900 dark:text-slate-100` | Inside cards |
| Body | `text-sm text-slate-600 dark:text-slate-300` | Descriptions |
| Small body | `text-xs text-slate-500 dark:text-slate-400` | Sub-descriptions |
| Table header | `text-xs font-semibold text-slate-500 uppercase tracking-wide` | `table-header` class |
| Mono / data | `font-mono font-semibold text-slate-900` | SKU codes, prices |
| Tabular nums | `tabular-nums` | **Always apply to number columns** |
| Section group label | `text-xs font-semibold text-slate-400 uppercase tracking-widest` | Rule engine section dividers |

### 1.4 Spacing & Sizing

| Element | Value |
|---|---|
| Page padding | `p-6` (24px) |
| Card padding (standard) | `p-5` (20px) |
| Card padding (compact) | `p-4` / `p-3` |
| Gap between cards | `gap-4` or `gap-5` |
| Table cell padding | `px-4 py-3` |
| Compact table cell | `px-2 py-1.5` |
| Input padding | `px-3 py-2` or `px-3 py-2.5` |
| Icon container size | `w-10 h-10` (rule engine), `w-8 h-8` (nav), `w-5 h-5` (icon inside) |

### 1.5 Border Radius

| Element | Tailwind |
|---|---|
| Cards | `rounded-xl` |
| Buttons | `rounded-lg` |
| Inputs | `rounded-lg` |
| Badges | `rounded-full` |
| Small chips / tags | `rounded-md` |
| Logo / icon containers | `rounded-lg` or `rounded-2xl` (login) |
| Avatar / dot | `rounded-full` |

### 1.6 Shadows

| Element | Tailwind |
|---|---|
| Card | `shadow-sm` |
| Card hover (rule engine) | `hover:shadow-md` |
| Login card | `shadow-xl shadow-emerald-100/50` |
| Logo | `shadow-lg shadow-emerald-200` |
| Deck viewport | `box-shadow: 0 24px 64px rgba(0,0,0,0.4)` — custom CSS, not Tailwind |

---

## 2. Layout System

### 2.1 App Shell

```
<html class="h-full dark">
  <body class="h-full bg-slate-100 dark:bg-slate-900 text-slate-900 dark:text-slate-100 font-['Inter']">
    <div class="flex h-full min-h-screen">
      <Sidebar />              {/* w-64, hidden on mobile */}
      <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Topbar />             {/* h-auto, border-b */}
        <main class="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  </body>
</html>
```

### 2.2 Sidebar

```tsx
// Fixed width w-64, hidden below lg breakpoint
// Logo area: px-6 py-5 border-b
// Nav: flex-1 px-3 py-4 space-y-1 overflow-y-auto
// Footer: px-3 py-4 border-t (user avatar + name + dark toggle + sign out)

// Nav item pattern:
<a href="/quotes" className={cn(
  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
  isActive
    ? "bg-emerald-50 dark:bg-emerald-950/20 text-emerald-700 dark:text-emerald-400"
    : "text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-100"
)}>
  <Icon className="w-4 h-4 shrink-0" />
  Quotes
</a>
```

Active nav uses `bg-emerald-50` bg — NOT emerald-500. Text becomes `text-emerald-700 dark:text-emerald-400`.

### 2.3 Topbar

```tsx
<header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700 px-6 py-4 flex items-center justify-between shrink-0">
  <h1 className="text-lg font-semibold text-slate-900 dark:text-slate-100">{pageTitle}</h1>
  <div className="flex items-center gap-2">
    {/* topbar actions slot */}
  </div>
</header>
```

### 2.4 Common Grid Layouts

```tsx
// KPI row (3 cards)
<div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6" />

// Chart 2/3 + table 1/3
<div className="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-5">
  <div className="lg:col-span-2" />
  <div />
</div>

// Rule engine grid (up to 3 columns)
<div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4" />

// Two-column (50/50)
<div className="grid grid-cols-2 gap-4 items-start" />

// Two-column with left-heavy (detail + list)
<div className="grid grid-cols-[1fr_1fr] gap-4" />
```

---

## 3. Component Catalog

### 3.1 Button

**Three variants used throughout:**

```tsx
// Primary — emerald filled
<button className="bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg px-4 py-2 text-sm font-semibold transition-colors cursor-pointer">
  + New Quote
</button>

// Outline — border with hover emerald
<button className="border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:border-emerald-500 hover:text-emerald-600 rounded-lg px-3 py-2 text-sm transition-colors cursor-pointer">
  View
</button>

// Danger — red filled
<button className="bg-red-500 hover:bg-red-600 text-white rounded-lg px-4 py-2 text-sm font-semibold transition-colors cursor-pointer">
  Override & Confirm
</button>

// Compact variants (add to className)
// Small: text-xs py-1 px-3
// Full width: w-full flex justify-center
```

**shadcn mapping:**
- Primary → `<Button>` (default variant, customize `bg-emerald-500` in `button.tsx` variants)
- Outline → `<Button variant="outline">`
- Danger → `<Button variant="destructive">`

---

### 3.2 Card

```tsx
// Standard card
<div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-sm p-5">
  {children}
</div>

// Card with accent top border
<div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-sm border-t-2 border-t-emerald-500 p-5" />

// Card with accent left border
<div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-[0_10px_10px_0] shadow-sm border-l-[3px] border-l-emerald-500 p-4" />

// Override card (left border orange)
<div className="border-l-[3px] border-l-orange-[#fd7e14] ..." />

// Rule engine nav card (interactive)
<a href="..." className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-sm p-5 hover:border-emerald-300 dark:hover:border-emerald-700 hover:shadow-md transition-all group">
  <div className="flex items-start gap-4">
    <div className="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center shrink-0 group-hover:bg-emerald-100 transition-colors">
      <Icon className="w-5 h-5 text-emerald-600" />
    </div>
    <div>
      <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 group-hover:text-emerald-600 transition-colors">Title</h3>
      <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Description</p>
    </div>
  </div>
</a>
```

**shadcn mapping:** `<Card>`, `<CardHeader>`, `<CardContent>`. The accent-border variants need custom `className` overrides since shadcn Card doesn't expose border-color props.

---

### 3.3 Badge

Five variants. All use `inline-flex items-center rounded-full text-xs font-medium`.

```tsx
// Confirmed — emerald
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400">
  Confirmed
</span>

// Draft — slate/neutral
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400">
  Draft
</span>

// Pending — amber
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-400">
  Pending
</span>

// Stale / Error — red
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-600 dark:bg-red-950/50 dark:text-red-400">
  Stale
</span>

// Cancelled — red (same as stale)
// Auto-generated — accent (emerald bg, emerald text)
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-400">
  Auto-generated
</span>
```

**shadcn mapping:** `<Badge>`. Add custom variants in `badge.tsx`:
```ts
variants: {
  variant: {
    confirmed: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400",
    pending: "bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-400",
    stale: "bg-red-100 text-red-600 dark:bg-red-950/50 dark:text-red-400",
    draft: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
    accent: "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-400",
  }
}
```

---

### 3.4 Form Input

```tsx
// Text input
<input className="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-shadow" />

// Label
<label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1">
  Email
</label>

// Field group
<div>
  <label className="form-label">Field Name</label>
  <input className="form-input" />
</div>

// Override state — field that was manually edited
<input className="border-2 border-[#fd7e14] focus:ring-orange-400" />
// Or with data attribute:
// data-overridden="true" → CSS: [data-overridden=true]:border-[#fd7e14]
```

**shadcn mapping:** `<Input>` and `<Label>`. Customize focus ring to `ring-emerald-500` in `input.tsx`.

---

### 3.5 Table

```tsx
<div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-sm overflow-hidden">
  <table className="w-full text-sm">
    <thead>
      <tr>
        <th className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide bg-slate-50 dark:bg-slate-800/50 px-4 py-3 text-left">
          Column
        </th>
        <th className="... text-right">Number Col</th>
      </tr>
    </thead>
    <tbody>
      <tr className="border-b border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors">
        <td className="px-4 py-3 text-slate-900 dark:text-slate-100">Value</td>
        <td className="px-4 py-3 text-right tabular-nums font-medium">42.00</td>
      </tr>
    </tbody>
  </table>
</div>

// Empty state row
<tr>
  <td colSpan={7} className="px-4 py-8 text-center text-slate-500 dark:text-slate-400">
    No quotes yet. Create your first quote to get started.
  </td>
</tr>

// Overridden cell (manual edit)
<td className="px-4 py-3 text-right tabular-nums text-amber-600 dark:text-amber-400 font-medium border-l-[3px] border-l-[#fd7e14]">
  ₹145/kg ✎
</td>
```

**shadcn mapping:** `<Table>`, `<TableHeader>`, `<TableBody>`, `<TableRow>`, `<TableHead>`, `<TableCell>`. The hover row effect needs `className` on `<TableRow>`.

---

### 3.6 KPI Card

```tsx
<div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-sm p-4">
  <p className="text-[9px] uppercase tracking-[0.5px] text-slate-400 font-medium mb-1">
    Avg Margin
  </p>
  <p className="text-[22px] font-bold text-slate-900 dark:text-slate-100">
    11.8%
  </p>
  <p className="text-[10px] text-slate-400 mt-0.5">
    vs 10.2% last quarter
  </p>
</div>

// Accent value variant
<p className="text-[22px] font-bold text-emerald-500">₹42L</p>

// Error value variant (cost/problem)
<p className="text-[22px] font-bold text-red-600">45–90 min</p>

// Large format (analytics page)
<p className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-1">14</p>
<p className="text-sm text-slate-500 dark:text-slate-400">Confirmed Quotes</p>
```

No direct shadcn equivalent — compose from `<Card>` + custom children.

---

### 3.7 Alert Banner

```tsx
// Warning (amber) — stale price, MCX alert
<div className="rounded-lg bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 px-4 py-3 text-sm text-amber-700 dark:text-amber-400 mb-4">
  ⚠ Cinnamon Sticks price entry is 5 days old — confirm with your vendor before sending.
</div>

// Error (red) — stale override required
<div className="rounded-lg bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 px-4 py-3 text-sm text-red-700 dark:text-red-400 mb-4">
  Stale Prices Detected — some SKUs have outdated prices.
</div>

// AI suggestion (green-accent, left border)
<div className="rounded-lg bg-emerald-50 dark:bg-emerald-950/20 border-l-[3px] border-l-emerald-500 px-4 py-3 text-sm text-slate-700 dark:text-slate-300">
  <span className="text-emerald-600 font-semibold">AI:</span> Suggested price $4.72
</div>
```

**shadcn mapping:** `<Alert>` with `variant="destructive"` for red. Amber needs a custom variant.

---

### 3.8 Process Step (Packaging Constraints)

Three states: allowed, blocked, required.

```tsx
// Allowed / OK — emerald
<div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-50 text-emerald-800 text-xs font-medium mb-1.5">
  <CheckIcon className="w-3 h-3" />
  Allowed methods — set by certification rules
</div>

// Blocked — red with strikethrough
<div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-red-50 text-red-700 text-xs font-medium mb-1.5 line-through">
  <LockClosedIcon className="w-3 h-3" />
  Blocked methods — auto-restricted by cert
</div>

// Required — amber warning
<div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-amber-50 text-amber-700 text-xs font-medium mb-1.5">
  <ExclamationTriangleIcon className="w-3 h-3" />
  Required steps — flagged for compliance
</div>
```

---

### 3.9 Feature List Item

Used on module slides — icon + title + body description.

```tsx
<ul className="flex flex-col gap-3">
  <li className="flex gap-2.5 items-start">
    <div className="w-[22px] h-[22px] bg-emerald-50 rounded-[5px] flex items-center justify-center shrink-0 mt-0.5">
      <SparklesIcon className="w-[13px] h-[13px] text-emerald-500" />
    </div>
    <div>
      <p className="text-xs font-semibold text-slate-900 dark:text-slate-100 mb-0.5">AI field extraction</p>
      <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-[1.5]">
        SKUs, quantities, delivery dates, special requirements extracted automatically.
      </p>
    </div>
  </li>
</ul>
```

---

### 3.10 Flow Stepper (Horizontal Workflow)

Used on the Solution overview slide — horizontal nodes with arrows.

```tsx
<div className="flex items-stretch gap-0">
  {steps.map((step, i) => (
    <React.Fragment key={step.id}>
      <div className="bg-white border border-slate-200 rounded-[10px] p-3.5 flex-1 text-center flex flex-col items-center gap-1.5 shadow-sm">
        <div className="w-[30px] h-[30px] bg-emerald-50 rounded-[7px] flex items-center justify-center">
          <step.Icon className="w-[15px] h-[15px] text-emerald-500" />
        </div>
        <p className="text-[10px] font-semibold text-slate-900 leading-[1.3]">{step.label}</p>
        <p className="text-[9px] text-slate-500">{step.sub}</p>
      </div>
      {i < steps.length - 1 && (
        <div className="text-emerald-500 text-base font-bold flex items-center px-1 shrink-0">→</div>
      )}
    </React.Fragment>
  ))}
</div>
<p className="text-xs text-slate-500 text-center mt-4">Each step feeds the next. No re-entry. No lost context.</p>
```

No shadcn equivalent — custom component.

---

### 3.11 Order Timeline (Milestone Vertical)

Used on the traceability slide and order detail views.

```tsx
type TimelineEvent = {
  status: 'done' | 'warning' | 'pending'
  title: string
  subtitle: string
}

// done — green circle with check
<div className="flex gap-2.5 items-start pb-2.5">
  <div className="w-[18px] h-[18px] bg-green-100 rounded-full flex items-center justify-center shrink-0 mt-0.5">
    <CheckIcon className="w-[10px] h-[10px] text-green-600" />
  </div>
  <div className="border-l border-slate-200 pl-2.5 pb-2.5 flex-1">
    <p className="text-[11px] font-semibold text-slate-900">Order received</p>
    <p className="text-[10px] text-slate-500">Jan 3, 9:14 AM · WhatsApp · Al Barakah</p>
  </div>
</div>

// warning — amber circle with triangle, dashed border
<div className="flex gap-2.5 items-start pb-2.5">
  <div className="w-[18px] h-[18px] bg-amber-100 rounded-full flex items-center justify-center shrink-0 mt-0.5">
    <ExclamationTriangleIcon className="w-[10px] h-[10px] text-amber-600" />
  </div>
  <div className="border-l border-dashed border-amber-300 pl-2.5 pb-2.5 flex-1">
    <p className="text-[11px] font-semibold text-amber-600">Packing delayed 2 days</p>
    <p className="text-[10px] text-slate-500">Jan 9, 10:45 AM · FSSAI certificate arrived late</p>
  </div>
</div>

// pending — grey circle with clock, no border
<div className="flex gap-2.5 items-start">
  <div className="w-[18px] h-[18px] bg-slate-100 rounded-full flex items-center justify-center shrink-0 mt-0.5">
    <ClockIcon className="w-[10px] h-[10px] text-slate-400" />
  </div>
  <div className="pl-2.5 flex-1">
    <p className="text-[11px] font-semibold text-slate-400">Container loading</p>
    <p className="text-[10px] text-slate-400">Jan 14 · 5 days away</p>
  </div>
</div>
```

---

### 3.12 Price Waterfall Table

Core to the Quotation Builder. Named calculation steps with alternating subtotal rows.

```tsx
<div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
  {/* Header */}
  <div className="bg-slate-50 px-3.5 py-2.5 border-b border-slate-200 text-[9px] font-semibold uppercase tracking-[0.4px] text-slate-500">
    Price Breakdown — CINN-STICKS-001 · per kg
  </div>
  <table className="w-full text-[11px]">
    <tbody>
      {/* Regular row */}
      <tr className="border-b border-slate-50">
        <td className="px-3.5 py-2 text-slate-500">Base commodity price</td>
        <td className="px-3.5 py-2 text-right font-mono font-semibold text-slate-900">₹ 280.00</td>
        <td className="px-3.5 py-2 text-[9px] text-slate-400">Ramesh Agro, vendor call</td>
      </tr>
      {/* Subtotal row — highlighted */}
      <tr className="bg-slate-50 border-b border-slate-200">
        <td className="px-3.5 py-2 font-semibold text-slate-900">= EXW Cost</td>
        <td className="px-3.5 py-2 text-right font-mono font-bold text-slate-900">₹ 312.90</td>
        <td />
      </tr>
      {/* Final row — emerald highlight */}
      <tr className="bg-emerald-50">
        <td className="px-3.5 py-2 font-bold text-emerald-900">= Quoted price / kg</td>
        <td className="px-3.5 py-2 text-right font-mono font-bold text-emerald-500">$ 4.61</td>
        <td className="px-3.5 py-2 text-[9px] text-emerald-600">× 500 kg = $2,305</td>
      </tr>
    </tbody>
  </table>
  {/* AI coach footer */}
  <div className="px-3.5 py-2 bg-amber-50 border-t border-amber-200 text-[10px] text-amber-800 flex items-center gap-1.5">
    <SparklesIcon className="w-3 h-3 text-amber-600" />
    AI: This margin (16%) is 2.3% below your Japan average. Suggested price: $4.72.
  </div>
</div>
```

---

### 3.13 Progress Bar (CBM Utilisation)

```tsx
// Green — good utilisation
<div>
  <div className="flex justify-between text-[10px] mb-1">
    <span className="text-slate-400">CBM Utilisation</span>
    <span className="text-emerald-500 font-semibold">18.4 / 25.0 m³ — 73.6%</span>
  </div>
  <div className="bg-slate-100 rounded h-2">
    <div className="bg-emerald-500 rounded h-2" style={{ width: '73.6%' }} />
  </div>
</div>

// Amber — below threshold warning
// Change text-emerald-500 → text-amber-600
// Change bg-emerald-500 → bg-amber-500
// Add warning below:
<p className="text-[9px] text-amber-600 mt-1">⚠ Below 85% — 58 more cartons fit.</p>
```

---

### 3.14 Rule Engine Section Group Header

```tsx
// Section divider within a grid — spans full width
<div className="col-span-full mt-2">
  <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-3">
    Pricing Rules
  </h2>
</div>
```

---

### 3.15 Slide Eyebrow + Headline

Pattern used on every module slide in the deck. Maps to page section headers in the app.

```tsx
<>
  <p className="text-[10px] uppercase tracking-[1px] text-slate-400 font-medium mb-2">
    Module 2 — Quotation Builder
  </p>
  <h2 className="text-[22px] font-bold text-slate-900 dark:text-slate-100 leading-[1.3] mb-6">
    Your vendor prices, packaging costs, FX, and margin — one screen, one send.
  </h2>
</>
```

---

### 3.16 Login Page

Specific to the auth screen. Not part of the main shell.

```tsx
// Page: full-height wave gradient bg
<div className="min-h-screen flex flex-col items-center justify-center p-6"
  style={{
    background: 'linear-gradient(160deg, #ecfdf5 0%, #d1fae5 40%, #a7f3d0 70%, #6ee7b7 100%)'
  }}>
  
  {/* Logo mark */}
  <div className="inline-flex items-center justify-center w-14 h-14 bg-emerald-500 rounded-2xl shadow-lg shadow-emerald-200 mb-3">
    <SunIcon className="w-8 h-8 text-white" strokeWidth={1.8} />
  </div>
  <h1 className="text-xl font-bold text-slate-800">S&G Exports</h1>
  <p className="text-sm text-emerald-700 font-medium">Quotation Builder</p>

  {/* Card */}
  <div className="w-full max-w-sm bg-white/90 backdrop-blur-sm border border-emerald-100 rounded-2xl shadow-xl shadow-emerald-100/50 p-8 mt-6">
    {/* form fields */}
  </div>
  
  <p className="text-xs text-emerald-700/60 mt-4">Mumbai, India · Est. 1998</p>
</div>
```

---

### 3.17 Chart (Analytics)

```tsx
// Chart.js config — always use these colors
const chartConfig = {
  type: 'bar',
  data: {
    labels: [...],
    datasets: [{
      label: 'Confirmed Quotes',
      data: [...],
      backgroundColor: '#10b981',  // emerald-500 — hardcode this
    }]
  },
  options: {
    responsive: true,
    plugins: { legend: { display: false } }
  }
}

// With Recharts (React preferred):
<BarChart data={data}>
  <Bar dataKey="value" fill="#10b981" radius={[4, 4, 0, 0]} />
  <XAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
  <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} />
  <Tooltip 
    contentStyle={{ 
      background: '#fff', border: '1px solid #e2e8f0', 
      borderRadius: '8px', fontSize: '12px' 
    }} 
  />
</BarChart>
```

---

### 3.18 Container Plan / Pack Config Row List

Key-value pairs in a panel — used in packaging configurator.

```tsx
<div className="bg-white border border-slate-200 rounded-[10px] p-4 shadow-sm">
  <p className="text-[10px] font-semibold uppercase tracking-[0.4px] text-slate-400 mb-2.5">
    Packaging Config — SO-089
  </p>
  {rows.map(({ key, value }) => (
    <div key={key} className="flex justify-between items-center py-1.5 border-b border-slate-50 last:border-0">
      <span className="text-[11px] text-slate-400">{key}</span>
      <span className="text-[12px] text-slate-900 font-medium">{value}</span>
    </div>
  ))}
</div>
```

---

### 3.19 Rule Hierarchy Display

Three-tier hierarchy: certification → country → client.

```tsx
const tiers = [
  {
    icon: <CertificateIcon />,
    label: 'Certification level',
    detail: 'e.g. Kosher, Halal, Organic',
    bg: 'bg-emerald-50 dark:bg-emerald-950/20',
    text: 'text-emerald-800 dark:text-emerald-300',
    iconColor: 'text-emerald-500',
  },
  {
    icon: <GlobeIcon />,
    label: 'Country level',
    detail: 'e.g. EU labelling, US FDA, GCC',
    bg: 'bg-sky-50 dark:bg-sky-950/20',
    text: 'text-sky-800 dark:text-sky-300',
    iconColor: 'text-sky-500',
  },
  {
    icon: <UserIcon />,
    label: 'Client level',
    detail: 'Buyer-specific preferences and requirements',
    bg: 'bg-purple-50 dark:bg-purple-950/20',
    text: 'text-purple-800 dark:text-purple-300',
    iconColor: 'text-purple-500',
  },
]

{tiers.map(tier => (
  <div key={tier.label} className={`flex items-center gap-2 px-3 py-2 rounded-[7px] text-[11px] font-semibold mb-1.5 ${tier.bg} ${tier.text}`}>
    <tier.icon className={`w-3.5 h-3.5 ${tier.iconColor}`} />
    {tier.label}
    <span className="text-[10px] font-normal opacity-70">{tier.detail}</span>
  </div>
))}

{/* Override callout */}
<div className="flex items-center gap-2 px-3 py-2 rounded-[7px] bg-amber-50 border border-amber-200 text-[11px] text-amber-800 mt-2">
  <PencilIcon className="w-3.5 h-3.5" />
  Any rule can be manually overridden per order — full flexibility when you need it.
</div>
```

---

### 3.20 NL Query Input (Analytics)

```tsx
<div className="bg-white border border-slate-200 rounded-xl p-3 shadow-sm">
  <p className="text-[10px] font-semibold uppercase tracking-[0.4px] text-slate-400 mb-2">
    Ask anything about your orders
  </p>
  <div className="bg-slate-50 border border-slate-200 rounded-[7px] px-3 py-2 text-[11px] text-slate-700 italic">
    "Show orders where packing took more than 3 days"
  </div>
  <p className="text-[10px] text-slate-500 mt-1.5 pl-0.5">→ 3 orders found: SO-089, SO-087, SO-083</p>
</div>
```

---

## 4. Special States

### 4.1 Override State

When a field has been manually overridden from its rule-engine default.

```tsx
// Table cell override — amber/orange left border
<td className={cn(
  "px-4 py-3 text-right tabular-nums",
  isOverridden && "border-l-2 border-l-[#fd7e14] bg-orange-50/50 text-[#fd7e14] font-semibold"
)}>
  {value} {isOverridden && <span className="text-[10px]">✎</span>}
</td>

// Input override — orange border
<input className={cn(
  "form-input",
  isOverridden && "border-2 border-[#fd7e14] focus:ring-[#fd7e14]/30"
)} />

// Footer note on tables with overridden rows
<p className="text-[10px] text-slate-400 mt-2">
  <span className="text-[#fd7e14] font-semibold">■</span> Orange = manually overridden ·
  Prices entered by your team from vendor quotes.
</p>
```

### 4.2 Stale State

Price not updated within the threshold (default 5 days).

```tsx
// Badge
<span className="badge-stale">Stale (7d)</span>

// Alert banner shown above quote table
<div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700 mb-4">
  ⚠ Cinnamon Sticks price entry is 5 days old — confirm with your vendor before sending.
</div>

// In table cell — red text
<td className="text-red-600 dark:text-red-400 font-semibold tabular-nums">Stale</td>
```

### 4.3 AI Suggestion State

AI-generated callout, advisory — not a system state.

```tsx
<div className="flex items-start gap-2 px-3 py-2 rounded-[7px] bg-amber-50 border-l-2 border-l-amber-400 text-[10px] text-amber-800">
  <SparklesIcon className="w-3 h-3 text-amber-600 mt-0.5 shrink-0" />
  <span>AI: This margin (16%) is 2.3% below your Japan average. Suggested: $4.72.</span>
</div>
```

---

## 5. Tailwind Config Additions Needed

```js
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        override: '#fd7e14',   // manual override orange — not in Tailwind default
      },
      fontSize: {
        '2xs': ['10px', { lineHeight: '1.4' }],  // eyebrow text
        '3xs': ['9px', { lineHeight: '1.3' }],   // table headers, timestamps
      },
      boxShadow: {
        'deck': '0 24px 64px rgba(0,0,0,0.4)',   // pitch deck outer shadow
      },
    },
  },
}
```

---

## 6. shadcn/ui Component Mapping

| Custom component | shadcn component | Notes |
|---|---|---|
| `btn-primary` | `<Button>` | Change default from blue to `bg-emerald-500` in `button.tsx` |
| `btn-outline` | `<Button variant="outline">` | Add `hover:border-emerald-500 hover:text-emerald-600` |
| `btn-danger` | `<Button variant="destructive">` | Works as-is |
| `card` | `<Card>` | Remove default padding, apply manually (`p-4` / `p-5`) |
| `form-input` | `<Input>` | Change focus ring to `focus-visible:ring-emerald-500` |
| `form-label` | `<Label>` | Add `uppercase tracking-wide text-xs` |
| `badge-*` | `<Badge>` | Add 5 custom variants (see §3.3) |
| `alert-warn` | `<Alert>` | Add amber variant; default shadcn has only default + destructive |
| `alert-stale` | `<Alert variant="destructive">` | Works as-is |
| Data table | `<Table>` family | Add `hover:bg-slate-50 dark:hover:bg-slate-700/30` to `<TableRow>` |
| Sidebar nav | `<NavigationMenu>` or custom | Custom is simpler; shadcn NavigationMenu is for top nav |
| Rule engine card | `<Card>` with `asChild` | Use Radix `asChild` to make Card a link |
| KPI card | `<Card>` + custom children | No shadcn KPI component |
| Flow stepper | Custom | No shadcn equivalent |
| Timeline | Custom | No shadcn equivalent |
| Price waterfall | Custom table | No shadcn equivalent |
| Progress bar | `<Progress>` | Change indicator color to `bg-emerald-500` or `bg-amber-500` |
| NL query input | `<Input>` | Add italic placeholder styling |
| Chart | Recharts (included via shadcn) | Use `<BarChart>` with `fill="#10b981"` |

---

## 7. Migration Gotchas (Why Last Migration Failed)

These are the non-obvious patterns that are easy to miss:

1. **`tabular-nums` is mandatory on number columns.** Without it, numbers jump around as values change. Apply `tabular-nums` to every `<td>` containing prices, percentages, or counts.

2. **The override orange `#fd7e14` is not Tailwind `orange-500`.** Tailwind's `orange-500` is `#f97316`. Add the custom token (see §5) or use `text-[#fd7e14]`/`border-[#fd7e14]` arbitrary values.

3. **Dark mode uses `class` strategy, not `media`.** Toggle on `<html>` element, not `:root`. `next-themes` handles this automatically if configured with `attribute="class"`.

4. **Active sidebar nav uses `emerald-50` bg, NOT `emerald-500`.** The nav item background is the light emerald tint. Text becomes `text-emerald-700`. Common mistake: using a filled emerald background.

5. **Card `rounded-xl` not `rounded-lg`.** The app uses `rounded-xl` (12px) for cards and `rounded-lg` (8px) for buttons/inputs.

6. **Table header background is `bg-slate-50`, not `bg-white`.** It creates a subtle distinction between the header and rows. Easy to lose in migration.

7. **The `proc-step step-block` has `line-through` decoration.** The blocked certification methods are shown with strikethrough — this is intentional and carries meaning. Don't lose this styling.

8. **Rule hierarchy colors are a specific 3-color set:** emerald (cert), sky-blue (country), purple (client). These three should never be swapped or generalized.

9. **`backdrop-blur-sm` on the login card** requires the parent to have a semi-transparent background (`bg-white/90`). If the parent is fully opaque, the blur has no effect.

10. **Price waterfall subtotal rows use `bg-slate-50`, final row uses `bg-emerald-50`.** This is not just decoration — users read the hierarchy from this. Don't use a single alternating-rows pattern.

11. **Chart color is hardcoded `#10b981`**, not a CSS variable. Recharts/Chart.js doesn't read CSS variables in `fill`. Pass the hex directly.

12. **Anomaly alerts show 2 decimal places for ratios:** "2.4× longer". Format as `(value).toFixed(1)×`.

13. **The stale price banner appears ABOVE the table, not inline.** Inline stale badges on rows are a second layer — the top banner is the primary warning users act on.

14. **FX rate display format:** `₹83.4/$ · Source: RBI FBIL · 23 May 2026 11:30 IST`. Always show source and timestamp — never just the number.

---

## 8. Icon System

Source: **Tabler Icons** (CDN in ppt.html) and **Heroicons** (inline SVGs in app templates).

Migrate to: `@tabler/icons-react` for consistency. Install:
```bash
npm install @tabler/icons-react
```

Key icons used:
| Context | Icon |
|---|---|
| Logo / brand mark | `IconSun` (rays + circle) |
| Quotes nav | `IconFileInvoice` |
| Prices nav | `IconChartBar` |
| Rule Engine nav | `IconSettings` |
| Analytics nav | `IconChartBarOff` → `IconChartLine` |
| Admin nav | `IconAdjustments` |
| WhatsApp intake | `IconBrandWhatsapp` |
| AI / sparkles | `IconSparkles` |
| Override / edit | `IconEdit` |
| Stale / warning | `IconAlertTriangle` |
| Confirmed / check | `IconCheck` |
| Locked | `IconLock` |
| Certificate | `IconCertificate` |
| Globe / country | `IconGlobe` |
| Client | `IconUser` |
| Container / shipping | `IconShip` |
| Packaging box | `IconBox` |
| Trend | `IconTrendingUp` |
| Clock | `IconClock` |
| Camera | `IconCamera` |
| Sign out | `IconLogout` |
| Dark mode (moon) | `IconMoon` |
| Light mode (sun) | `IconSun` |

---

## 9. Component File Structure (Suggested)

```
src/
├── components/
│   ├── ui/                    # shadcn generated (don't edit manually)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── badge.tsx
│   │   ├── input.tsx
│   │   ├── label.tsx
│   │   ├── table.tsx
│   │   ├── alert.tsx
│   │   └── progress.tsx
│   ├── layout/
│   │   ├── AppShell.tsx       # sidebar + topbar + main wrapper
│   │   ├── Sidebar.tsx        # nav items, user footer, dark toggle
│   │   └── Topbar.tsx         # page title + topbar-actions slot
│   ├── data-display/
│   │   ├── KpiCard.tsx        # label + big number + sub
│   │   ├── DataTable.tsx      # wrapper with card + table + empty state
│   │   ├── Badge.tsx          # re-exports shadcn Badge with custom variants
│   │   ├── PriceWaterfall.tsx # named-step calculation table
│   │   ├── OrderTimeline.tsx  # milestone vertical timeline
│   │   ├── FlowStepper.tsx    # horizontal workflow nodes + arrows
│   │   ├── UtilisationBar.tsx # CBM/weight progress bar with label
│   │   └── RuleHierarchy.tsx  # cert/country/client 3-tier display
│   ├── form/
│   │   ├── FormField.tsx      # label + input + error wrapper
│   │   └── OverrideInput.tsx  # input with orange border when overridden
│   ├── feedback/
│   │   ├── AlertBanner.tsx    # warn/error/ai-suggestion variants
│   │   ├── ProcessStep.tsx    # ok/blocked/required step chips
│   │   └── AiCoach.tsx        # sparkles + amber suggestion callout
│   └── packaging/
│       ├── PackConfigPanel.tsx  # key-value row list
│       └── ContainerPlan.tsx    # pack summary + constraint checks
├── lib/
│   ├── tokens.ts              # color constants for Chart.js / inline styles
│   └── cn.ts                  # clsx + tailwind-merge utility
└── styles/
    └── globals.css            # @tailwind directives + dark mode setup
```

### `tokens.ts` — hardcoded values that CSS vars can't reach

```ts
export const COLORS = {
  accent: '#10b981',        // emerald-500
  accentDark: '#059669',    // emerald-600
  accentBg: '#ecfdf5',      // emerald-50
  override: '#fd7e14',      // custom orange
  warn: '#d97706',          // amber-600
  error: '#dc2626',         // red-600
  success: '#16a34a',       // green-600
  textMuted: '#94a3b8',     // slate-400
  border: '#e2e8f0',        // slate-200
} as const
```

---

## 10. Quick Reference — Tailwind Class Snippets

```
Page bg:        bg-slate-100 dark:bg-slate-900
Card:           bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-sm
Card padding:   p-5
Input:          bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none
Label:          text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1
Table header:   text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide bg-slate-50 dark:bg-slate-800/50 px-4 py-3
Table row:      border-b border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors
Table cell:     px-4 py-3 tabular-nums
Primary btn:    bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg px-4 py-2 text-sm font-semibold transition-colors
Outline btn:    border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:border-emerald-500 hover:text-emerald-600 rounded-lg px-3 py-2 text-sm transition-colors
Nav active:     bg-emerald-50 dark:bg-emerald-950/20 text-emerald-700 dark:text-emerald-400
Nav inactive:   text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-100
Icon container: w-10 h-10 rounded-lg bg-emerald-50 dark:bg-emerald-950/30 flex items-center justify-center
Eyebrow:        text-[10px] uppercase tracking-[1px] text-slate-400 font-medium mb-2
Section label:  text-xs font-semibold text-slate-400 uppercase tracking-widest mb-3
Warn alert:     rounded-lg bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 px-4 py-3 text-sm text-amber-700 dark:text-amber-400
Error alert:    rounded-lg bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 px-4 py-3 text-sm text-red-700 dark:text-red-400
Override border: border-l-2 border-l-[#fd7e14]
Override text:   text-[#fd7e14] font-semibold
```
