# Quotation Builder — Math & Formula Reference

---

## 1. End-to-End Flow

```
Vendor Price (INR/kg)
        |
        v
+------------------+
|  PACKAGE PLANNING |  <-- How many packets? How many cartons?
+------------------+
        |
        v
+------------------+
|   COST ENGINE    |  <-- 9-component cost stack per line item
+------------------+
        |  cost_per_kg_inr
        v
+------------------+
|  MARGIN ENGINE   |  <-- Base margin + 7 adaptive factors
+------------------+
        |  selling_price_per_kg_inr
        v
+------------------+
|   FX CONVERSION  |  <-- INR → USD/EUR/etc with buffer
+------------------+
        |  selling_price_fx
        v
+------------------+
|  CBM / CONTAINER |  <-- Volume check: 20ft or 40ft?
+------------------+
        |
        v
   FINAL QUOTE LINE ITEM
```

---

## 2. Package Planning

Before any cost can be calculated, the system must figure out how many **packets** and **cartons** the order requires.

### Inputs

| Variable | Source | Example |
|---|---|---|
| `quantity_kg` | User input | 250 kg |
| `weight_grams` | `package_sizes.weight_grams` | 500 g per packet |
| `pkts_per_carton` | `packaging_materials.pkts_per_carton` | 50 packets/carton |

### Formulas

```
num_pkts    = ceil( quantity_kg × 1000 / weight_grams )

num_cartons = ceil( num_pkts / pkts_per_carton )
```

### Example

```
quantity_kg    = 250 kg
weight_grams   = 500 g   (i.e. 0.5 kg packets)
pkts_per_carton = 50

num_pkts    = ceil(250 × 1000 / 500) = ceil(500)   = 500 packets
num_cartons = ceil(500 / 50)          = ceil(10)    = 10 cartons
```

### Why ceil()?

You can never pack a partial packet or a partial carton.
If 501 packets are needed, you need 11 cartons — not 10.1.

---

## 3. Cost Engine (9 Components)

Every line item's cost is built up from 9 stacked components.

### Component Stack

```
+------------------------------------------+
|  1. Raw Material        vendor_price × qty|
+------------------------------------------+
|  2. Labour              packing + sticker |
+------------------------------------------+
|  3. Packaging           cartons + pouches |
+------------------------------------------+
|  4. Sanitization        per-kg rate × qty |
+------------------------------------------+
|  5. Certifications      per-kg rate × qty |
+------------------------------------------+
|  6. Loading             per-kg rate × qty |
+------------------------------------------+
|  7. Transport           per-kg rate × qty |
+------------------------------------------+
|  8. CHA (Customs Agent) flat, allocated   |
+------------------------------------------+
|  9. Customs Duty        flat, allocated   |
+------------------------------------------+
              |
              v
         SUBTOTAL (INR)
              |
       ÷ quantity_kg
              |
         COST PER KG (INR)
```

### Formulas

**Component 1 — Raw Material**
```
raw_material_inr = vendor_price_per_kg × quantity_kg
```

**Component 2 — Labour**
```
sticker_cost = sticker_1side   (if label_sides == 1)
             = sticker_2side   (if label_sides == 2)

labour_inr = (packing_cost + sticker_cost) × num_pkts
```

> Labour scales with packets, not kg.
> Packing 500 small packets costs more than packing 10 large sacks of the same total weight.

**Component 3 — Packaging Materials**
```
packaging_inr = (carton_rate + pouch_price × pkts_per_carton) × num_cartons
              + sticker_rate × num_pkts
```

Breaking it down:
```
per_carton_cost = carton_rate              (cost of the cardboard box)
                + pouch_price × 50        (cost of 50 pouches that go inside)

packaging_inr   = per_carton_cost × num_cartons
                + sticker_rate   × num_pkts    (sticker per packet)
```

**Component 4 — Sanitization**
```
sanitization_inr = san_cost_per_kg × quantity_kg
```

| Type | Typical rate |
|---|---|
| Steam | ₹100/kg |
| Chemical (ETO/Gamma) | ₹150/kg |
| None | ₹0/kg |

**Component 5 — Certifications**
```
cert_inr = sum( cert[i].cost_per_kg × quantity_kg  for each cert )
```

Each certification (FDA, Halal, ISO, etc.) adds a per-kg charge.

**Component 6 — Loading**
```
loading_inr = loading_per_kg × quantity_kg
```

Default: ₹0.80/kg (from `system_settings`)

**Component 7 — Transport (Domestic)**
```
transport_inr = transport_per_kg × quantity_kg
```

Default: ₹1.50/kg (from `system_settings`)

**Component 8 & 9 — CHA + Customs (Allocated)**
```
cha_allocated_inr     = flat CHA fee ÷ total line items in shipment
customs_allocated_inr = flat customs fee ÷ total line items in shipment
```

Defaults: CHA = ₹25,000 flat, Customs = ₹15,000 flat (from `system_settings`)

**Final Assembly**
```
subtotal_inr = raw_material_inr
             + labour_inr
             + packaging_inr
             + sanitization_inr
             + cert_inr
             + loading_inr
             + transport_inr
             + cha_allocated_inr
             + customs_allocated_inr

cost_per_kg_inr = subtotal_inr / quantity_kg
```

### Full Worked Example

```
Product:         Turmeric Powder A Grade
Quantity:        250 kg
Package size:    500g packets
Label sides:     1
Sanitization:    Steam
Certifications:  FDA

--- Inputs from DB ---
vendor_price_per_kg = ₹450
weight_grams        = 500
pkts_per_carton     = 50
packing_cost        = ₹10/pkt
sticker_1side       = ₹2/pkt
carton_rate         = ₹25/carton
pouch_price         = ₹2/pkt
sticker_rate        = ₹0.50/pkt
san_cost_per_kg     = ₹100 (steam)
fda_cost_per_kg     = ₹250
transport_per_kg    = ₹1.50
loading_per_kg      = ₹0.80
cha_allocated       = ₹0 (not yet allocated)
customs_allocated   = ₹0

--- Package Planning ---
num_pkts    = ceil(250,000 / 500)  = 500 packets
num_cartons = ceil(500 / 50)       = 10 cartons

--- Cost Components ---
raw_material_inr  = 450 × 250        = ₹112,500
labour_inr        = (10 + 2) × 500   = ₹6,000
packaging_inr     = (25 + 2×50)×10   = ₹1,250
                  + 0.50×500         = +₹250
                  = ₹1,500
sanitization_inr  = 100 × 250        = ₹25,000
cert_inr          = 250 × 250        = ₹62,500   (FDA)
loading_inr       = 0.80 × 250       = ₹200
transport_inr     = 1.50 × 250       = ₹375

subtotal_inr      = 112,500 + 6,000 + 1,500 + 25,000
                  + 62,500 + 200 + 375
                  = ₹208,075

cost_per_kg_inr   = 208,075 / 250    = ₹832.30 / kg
```

---

## 4. Margin Engine

The margin is not fixed. It starts at a **base rate** and is adjusted up or down by **7 weighted factors**.

### Formula

```
margin_pct = base_margin + weighted_adjustment

weighted_adjustment = sum( factor_score[i] × factor_weight[i]  for i in 7 factors )

margin_pct = clamp(margin_pct, floor, cap)
           = max(floor, min(cap, margin_pct))

selling_price_per_kg_inr = cost_per_kg_inr × (1 + margin_pct / 100)
```

### System Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `base_margin` | 10% | Starting margin before adjustments |
| `margin_floor` | 3% | Minimum margin (never go below this) |
| `margin_cap` | 25% | Maximum margin (never exceed this) |

`margin_floor` can be overridden per client (e.g., a key account locked at 2% floor).

### The 7 Adaptive Factors

Each factor takes an input value, scores it against **tiers**, and returns an **adjustment** (positive = add margin, negative = reduce margin).

```
Factor input value
       |
       v
  [Tier 1: value < X]  --> adjustment_a
  [Tier 2: X <= value < Y] --> adjustment_b
  [Tier 3: value >= Y] --> adjustment_c
       |
       v
  adjustment × weight  -->  added to weighted_adjustment
```

#### Factor Table

| # | Factor | Input | Weight | Low → Adj | Mid → Adj | High → Adj |
|---|---|---|---|---|---|---|
| 1 | Volume | order_kg | 1.5 | <500 kg → -1.0% | 500–2000 kg → 0% | >2000 kg → +1.5% |
| 2 | Advance Payment | advance_% | 1.2 | <25% → -1.0% | 25–50% → 0% | >50% → +1.0% |
| 3 | Client History | order_count | 1.0 | <1 order → -0.5% | 1–5 → 0% | >5 → +1.0% |
| 4 | Competition | level (1–3) | 1.0 | Scarce(1) → +1.5% | Normal(2) → 0% | Commodity(3) → -1.0% |
| 5 | Price Volatility | volatility_% | 0.8 | Stable → 0% | Moderate → -0.5% | High → -1.0% |
| 6 | Country Risk | risk_score (1–5) | 1.0 | Low(1–2) → -0.5% | Medium(2–4) → 0% | High(4–5) → +1.5% |
| 7 | Urgency | days_to_ship | 0.8 | Rush(<1) → -0.5% | Normal(1–2) → 0% | Flexible(>2) → +1.0% |

> Adjustment signs explained:
> - Large volume → buyer deserves a discount → margin goes DOWN (-1.0)
> - High country risk → need cushion → margin goes UP (+1.5)
> - Commodity product → competitive market → margin goes DOWN (-1.0)
> - Rush order → buyer needs it urgently → margin goes DOWN (you may need to cut price to win)

### Margin Example

```
cost_per_kg_inr = ₹832.30
base_margin     = 10%

Context:
  volume_kg          = 250 kg    (factor 1: low → -1.0 × 1.5 = -1.5)
  advance_pct        = 50%       (factor 2: mid → 0.0 × 1.2 =  0.0)
  client_order_count = 3         (factor 3: mid → 0.0 × 1.0 =  0.0)
  competition_level  = 2         (factor 4: mid → 0.0 × 1.0 =  0.0)
  price_volatility   = 1%        (factor 5: low → 0.0 × 0.8 =  0.0)
  country_risk       = 1 (USA)   (factor 6: low → -0.5 × 1.0 = -0.5)
  urgency_days       = 2         (factor 7: mid → 0.0 × 0.8 =  0.0)

weighted_adjustment = -1.5 + 0 + 0 + 0 + 0 + (-0.5) + 0 = -2.0

margin_pct = 10 + (-2.0) = 8.0%
clamp(8.0, 3, 25)        = 8.0%   (within bounds)

selling_price = 832.30 × (1 + 8.0/100)
             = 832.30 × 1.08
             = ₹898.88 / kg
```

### Margin Clamp Diagram

```
     3%        10%       25%
      |---------|---------|
   FLOOR     BASE       CAP

If calculated margin = 1.5%:
      1.5%  is below FLOOR (3%)
      result = 3%   (floored)

If calculated margin = 27%:
      27% is above CAP (25%)
      result = 25%  (capped)

If calculated margin = 8%:
      8% is between FLOOR and CAP
      result = 8%   (as-is)
```

---

## 5. FX Conversion

The selling price is calculated in INR, then converted to the buyer's currency.

### Why a buffer?

FX rates fluctuate. If you quote ₹898.88 = $10.77 today and the rate moves before shipment, you could lose money. The buffer is a small haircut on the rate to protect against this.

### Formulas

```
rate_with_buffer = raw_rate × (1 - fx_variation_buffer)

fx_amount = amount_inr / rate_with_buffer
```

### Example

```
selling_price_per_kg_inr = ₹898.88
raw_rate (USD/INR)        = 83.50  (i.e. 1 USD = ₹83.50)
fx_variation_buffer       = 0.02   (2%)

rate_with_buffer = 83.50 × (1 - 0.02) = 83.50 × 0.98 = ₹81.83 per USD

selling_price_usd = 898.88 / 81.83 = $10.985 / kg
```

### Buffer Visualised

```
Raw rate:          1 USD = ₹83.50
                           ↑
Buffer (2%):        shrink rate by ₹1.67
                           ↓
Effective rate:    1 USD = ₹81.83

Effect on buyer:   Same INR amount now = MORE USD
                   You get $10.99 instead of $10.77
                   ← extra $0.22/kg covers rate movement risk
```

### Buffer by Currency (defaults)

| Currency | Buffer | Rationale |
|---|---|---|
| USD | 2% | Moderate volatility |
| EUR | 2% | Moderate volatility |
| GBP | 2% | Moderate volatility |
| AED | 1% | Pegged to USD, more stable |
| CAD | 2% | Moderate volatility |
| AUD | 2% | Moderate volatility |
| INR | 0% | Domestic, no conversion needed |

---

## 6. CBM (Cubic Metre) Calculation

CBM is the physical volume of the shipment, used to determine which container size fits.

### What is CBM?

1 CBM = 1 cubic metre = 100cm × 100cm × 100cm = 1,000,000 cm³

### Formulas

```
cbm_per_carton = (length_cm × breadth_cm × height_cm) / 1,000,000

total_cbm = cbm_per_carton × num_cartons
```

### Example

```
Carton dimensions: 40cm × 30cm × 25cm
num_cartons: 10

cbm_per_carton = (40 × 30 × 25) / 1,000,000
               = 30,000 / 1,000,000
               = 0.03 CBM

total_cbm = 0.03 × 10 = 0.30 CBM
```

---

## 7. Container Recommendation

Once total CBM and total KG are known across all line items, the system recommends the smallest container that fits — checking both volume AND weight limits.

### Container Limits

```
+---------------------------+----------+-----------+
| Container                 | Max CBM  | Max KG    |
+---------------------------+----------+-----------+
| 20-foot standard          | 28 CBM   | 21,700 kg |
| 40-foot standard          | 56 CBM   | 26,500 kg |
+---------------------------+----------+-----------+
```

### Decision Logic

```
fits_20ft = (total_cbm <= 28) AND (total_kg <= 21,700)
fits_40ft = (total_cbm <= 56) AND (total_kg <= 26,500)

if fits_20ft:
    recommended = "20ft"
    utilization_cbm = total_cbm / 28 × 100%
    utilization_kg  = total_kg / 21700 × 100%

elif fits_40ft:
    recommended = "40ft"
    utilization_cbm = total_cbm / 56 × 100%
    utilization_kg  = total_kg / 26500 × 100%

else:
    recommended = "multiple containers"
```

**Both conditions must pass.** A shipment that is light but bulky, OR heavy but compact, still needs the larger container.

### Container Diagram

```
20-foot Container (side view, not to scale):
+---------------------------------------------+
|                                             |
|   MAX LOAD: 28 CBM  /  21,700 kg            |
|                                             |
|  [carton][carton][carton][carton][carton]   |
|  [carton][carton][carton][carton][carton]   |
|                                             |
+---------------------------------------------+
 <-------- ~6 metres ----------------------->

40-foot Container:
+---------------------------------------------+---------------------------------------------+
|                                             |                                             |
|   MAX LOAD: 56 CBM  /  26,500 kg                                                         |
|                                             |                                             |
+---------------------------------------------+---------------------------------------------+
 <-------------------------------- ~12 metres ------------------------------------------->
```

### Utilization Example

```
Order: 10 cartons × 0.03 CBM = 0.30 CBM, total weight 250 kg

fits_20ft = (0.30 <= 28) AND (250 <= 21,700) → TRUE

recommended = "20ft"
utilization_cbm = 0.30 / 28 × 100 = 1.1%   (nearly empty by volume)
utilization_kg  = 250 / 21700 × 100 = 1.2%  (nearly empty by weight)
```

This tells the sales team: "you have huge space left in this container — consider adding other products to this shipment."

---

## 8. Stale Price Logic

A vendor price is considered **stale** if it is older than the configured threshold.

### Formula

```
age_days = julianday(NOW) - julianday(price.created_at)

is_stale = age_days >= stale_days_threshold
```

Default threshold: **7 days** (configurable in `system_settings`).

### Behaviour

```
Price entered: Day 0
                |
Day 1-6:  age_days < 7   --> FRESH (quote can proceed)
                |
Day 7+:   age_days >= 7  --> STALE (quote is blocked)
```

When stale:
- Quote wizard shows a warning on the review page
- User must either enter a new vendor price, OR
- Provide a written override reason (requires `quote.stale_override` feature)

```
STALE PRICE BLOCKING FLOW:

  Line item has stale price?
          |
         YES
          |
          v
  Does user have quote.stale_override?
          |
    YES   |   NO
    |     |    |
    v     |    v
  Enter   |  BLOCKED — must
  reason  |  update price first
    |     |
    v     |
  Quote   |
  proceeds|
```

---

## 9. Full Quote Line Item — Numbers From Start to Finish

Putting it all together with one realistic example.

```
=== INPUT ===
Product:        Turmeric Powder, A Grade
Quantity:       250 kg
Package:        500g packets
Label sides:    1
Sanitization:   Steam
Certifications: FDA
Country:        USA (risk_score=1, currency=USD)
Client:         Premium Foods Inc (no margin_floor_override)
Vendor price:   ₹450/kg

=== STEP 1: PACKAGE PLANNING ===
num_pkts    = ceil(250,000 / 500) = 500 packets
num_cartons = ceil(500 / 50)      = 10 cartons

=== STEP 2: COST ENGINE ===
raw_material  = 450 × 250            = ₹112,500.00
labour        = (10 + 2) × 500       =   ₹6,000.00
packaging     = (25 + 2×50)×10       =   ₹1,250.00
              + 0.50×500             =     ₹250.00   = ₹1,500.00
sanitization  = 100 × 250            =  ₹25,000.00
certification = 250 × 250            =  ₹62,500.00  (FDA)
loading       = 0.80 × 250           =     ₹200.00
transport     = 1.50 × 250           =     ₹375.00
cha           =                           ₹0.00
customs       =                           ₹0.00
                                     ───────────────
SUBTOTAL                             = ₹208,075.00

cost_per_kg   = 208,075 / 250        = ₹832.30 / kg

=== STEP 3: MARGIN ENGINE ===
base_margin          = 10%
volume adj           = -1.0 × 1.5 = -1.5%   (250 kg is small order)
advance_payment adj  =  0.0 × 1.2 =  0.0%
client_history adj   =  0.0 × 1.0 =  0.0%
competition adj      =  0.0 × 1.0 =  0.0%
volatility adj       =  0.0 × 0.8 =  0.0%
country_risk adj     = -0.5 × 1.0 = -0.5%   (USA is low risk)
urgency adj          =  0.0 × 0.8 =  0.0%
                                   ───────
weighted_adjustment  =              -2.0%

margin_pct = 10 + (-2.0) = 8.0%
clamp(8.0, 3, 25)         = 8.0%

selling_price_inr = 832.30 × 1.08 = ₹898.88 / kg

=== STEP 4: FX CONVERSION ===
raw_rate (INR per USD)   = 83.50
fx_variation_buffer      = 2%
rate_with_buffer         = 83.50 × 0.98 = 81.83

selling_price_usd = 898.88 / 81.83 = $10.985 / kg ≈ $10.99/kg

=== STEP 5: CBM CALCULATION ===
carton dims: 40 × 30 × 25 cm
cbm_per_carton = (40 × 30 × 25) / 1,000,000 = 0.03 CBM
total_cbm      = 0.03 × 10 = 0.30 CBM
total_kg       = 250 kg

=== STEP 6: CONTAINER RECOMMENDATION ===
fits_20ft = (0.30 <= 28) AND (250 <= 21,700) = TRUE
recommended = "20ft"
utilization_cbm = 0.30 / 28  × 100 = 1.1%
utilization_kg  = 250 / 21700 × 100 = 1.2%

=== FINAL QUOTE LINE ITEM ===
+-------------------------------------------------+
| Turmeric Powder A Grade — 250 kg               |
| Package:       500g × 500 pkts × 10 cartons    |
|-------------------------------------------------|
| Raw Material   ₹112,500  (₹450/kg × 250kg)     |
| Labour           ₹6,000  (₹12/pkt × 500 pkts)  |
| Packaging        ₹1,500  (cartons + pouches)    |
| Sanitization    ₹25,000  (₹100/kg, steam)       |
| Certification   ₹62,500  (₹250/kg, FDA)         |
| Loading            ₹200  (₹0.80/kg)             |
| Transport          ₹375  (₹1.50/kg)             |
|-------------------------------------------------|
| TOTAL COST     ₹208,075  = ₹832.30/kg           |
| MARGIN              8.0% (base 10%, adj -2%)    |
|-------------------------------------------------|
| SELLING PRICE  ₹898.88/kg  =  $10.99/kg (USD)  |
| CONTAINER: 20ft  (1.1% CBM used, 1.2% kg used) |
+-------------------------------------------------+
```

---

## 10. Quick Formula Cheat Sheet

```
PACKAGE PLANNING
  num_pkts    = ceil( qty_kg × 1000 / weight_grams )
  num_cartons = ceil( num_pkts / pkts_per_carton )

COST COMPONENTS
  raw_material  = vendor_price_per_kg × qty_kg
  labour        = (packing_cost + sticker_cost) × num_pkts
  packaging     = (carton_rate + pouch_price × pkts_per_carton) × num_cartons
                + sticker_rate × num_pkts
  sanitization  = san_cost_per_kg × qty_kg
  certifications= sum( cert_cost_per_kg × qty_kg )
  loading       = loading_per_kg × qty_kg
  transport     = transport_per_kg × qty_kg

  subtotal      = sum of all 9 components
  cost_per_kg   = subtotal / qty_kg

MARGIN ENGINE
  weighted_adj  = sum( score(factor_i) × weight_i )
  margin_pct    = clamp( base_margin + weighted_adj, floor, cap )
  selling_price = cost_per_kg × (1 + margin_pct / 100)

FX CONVERSION
  effective_rate = raw_rate × (1 - fx_buffer)
  price_in_fx    = selling_price_inr / effective_rate

CBM
  cbm_per_carton = (L_cm × W_cm × H_cm) / 1,000,000
  total_cbm      = cbm_per_carton × num_cartons

CONTAINER CHECK
  fits_20ft = total_cbm <= 28  AND total_kg <= 21,700
  fits_40ft = total_cbm <= 56  AND total_kg <= 26,500

STALE CHECK
  age_days = today - price_date
  is_stale = age_days >= stale_threshold (default: 7)
```
