# Exhaustive Seed Data Guide

## Overview
The updated `seed.py` now creates a **complete demonstration database** with realistic dummy data covering all features described in the SRS document.

---

## Data Loaded by seed.py

### 1. **Features & RBAC** (15 features)
```
Features:
  ├── price.entry, price.bulk, price.stale, price.trends
  ├── quote.create, quote.manual_override, quote.stale_override, quote.export
  ├── rule_engine.view, rule_engine.edit
  ├── analytics.view, analytics.export
  ├── admin.master_data, admin.users, admin.system
```

**Feature Templates (4 predefined roles):**
- `Price Updater` → Can enter prices, view trends, check stale
- `Quote Builder` → Can create quotes, export, view prices
- `Super User` → Everything except admin (includes manual override, stale override)
- `Admin` → All features

---

### 2. **Currencies** (7 currencies)
```
USD, INR, EUR, GBP, AED, CAD, AUD
```
With FX variation buffers configured per currency (0.01–0.02).

---

### 3. **System Settings** (21 configurable rules)
```
Margin:
  ├── base_margin: 10%
  ├── margin_floor: 3%
  ├── margin_cap: 25%

Costs:
  ├── transport_per_kg: ₹1.50
  ├── loading_per_kg: ₹0.80
  ├── cha_flat: ₹25,000
  ├── customs_flat: ₹15,000

Container Limits:
  ├── 20ft: 28 CBM, 21,700 kg
  ├── 40ft: 56 CBM, 26,500 kg

System:
  ├── stale_days: 7 (configurable per order)
  ├── quote_number_prefix: SGE
  ├── quote_number_next: 1001
```

---

### 4. **Margin Factors** (7 adaptive factors)
Each with configurable weight and scoring tiers:
```
1. volume (Order Volume)
2. advance_payment (Payment Terms)
3. client_history (Repeat Client?)
4. competition (Product Scarcity)
5. price_volatility (Market Stability)
6. country_risk (Geo Risk)
7. urgency (Rush Order?)
```

---

### 5. **Products & Qualities** (100+ products from Product Library.xlsx)
**Source:** `Product Library.xlsx` (Category, Product, Quality sheets)

**Categories from Excel:**
- Spices Whole (low competition)
- Spices Powder (medium competition)
- Blended Spices
- Grains (high competition)
- Pulses

**Sample Products:**
- Ajwain Whole → Qualities: Madras, A, B, Hot, Mild
- Basmati Rice → Multiple quality grades
- Turmeric Powder → A, B, C grades
- *... and 100+ more from your Product Library*

---

### 6. **Package Sizes** (13 standard sizes)
```
20g → 25kg (standard export sizes)
├── 20g, 50g, 100g, 200g, 250g, 500g, 1kg
├── 2kg, 5kg, 10kg, 15kg, 20kg, 25kg
```

Each with:
- **Labour costs** (packing + stickers)
- **Packaging materials** (carton, pouch prices)
- **CBM dimensions** (for container planning)

---

### 7. **Sanitization Types** (4 types)
```
├── ETO (Ethylene Oxide) — ₹150/kg
├── Gamma Irradiation — ₹200/kg
├── Steam Sterilization — ₹100/kg
└── None (Ambient) — Free
```

---

### 8. **Certifications** (6 types)
```
├── FDA Certificate — ₹250/kg
├── Spice Board Cert — ₹150/kg
├── ISO 22000 — ₹300/kg
├── Halal Certificate — ₹200/kg
├── Organic Cert — ₹350/kg
└── None — Free
```

---

### 9. **Countries** (10 target export markets)
```
Countries:
├── USA (risk: low, default currency: USD)
├── UAE (risk: medium, Halal preferred)
├── UK (risk: low, EU-style regulations)
├── EU (risk: low, strict food safety)
├── Canada (risk: low)
├── Australia (risk: low)
├── Singapore (risk: medium, high quality)
├── China (risk: high, long lead time)
├── Japan (risk: low, premium pricing)
└── India (domestic, no export risk)
```

---

### 10. **Vendor Prices** (160+ price entries)
**Source:** Simulated from 4 vendors × 40 product-quality combinations

```
Example:
  Product: Turmeric Powder
  Quality: A Grade
  Vendors:
    ├── Sharma Spices — ₹450/kg (2 days old)
    ├── Patel & Co — ₹455/kg (4 days old)
    ├── Global Trade — ₹460/kg (6 days old)
    └── Mumbai Traders — ₹465/kg (8 days old)
```

**Stale Pricing Realistic:** Prices vary by age (first vendor freshest, others progressively older).

---

### 11. **Sample Clients** (7 export clients)
```
Clients:
├── Premium Foods Inc (USA) — floor override 2%, low risk
├── Spice World Trading (UAE) — medium risk
├── London Imports Ltd (UK) — low risk
├── Berlin GmbH (EU) — low risk
├── Toronto Distributor (Canada) — low risk
├── Sydney Wholesale (Australia) — low risk
└── Singapore Retail Corp (Singapore) — medium risk
```

Each with:
- Country assignment
- Payment risk profile
- Credit terms (Net 30 or Net 60)
- Optional margin floor override

---

### 12. **Sample Users** (5 users)
```
Admin:
  └── admin@sandgexports.com
      (All features — set password on first run)

Demo Users:
  ├── ravi@sandgexports.com (Price Updater role)
  │   Features: price.entry, price.bulk, price.stale, price.trends
  │
  ├── priya@sandgexports.com (Quote Builder role)
  │   Features: quote.create, quote.export, price.stale, price.trends
  │
  ├── suresh@sandgexports.com (Super User role)
  │   Features: price + quote + manual_override + stale_override + analytics
  │
  └── marketing@sandgexports.com (Basic Quote Creator)
      Features: quote.create, quote.export
```

**Demo Password:** `demo123456` (for all demo users except admin)

---

### 13. **Sample Quotes** (6 quotes)
```
Quotes Generated:
├── 3 clients
├── 2 quotes per client (total 6)
├── 3-5 line items per quote
└── Statuses: Draft
```

**Each Quote Includes:**
- Quote number (SGE-1001, SGE-1002, etc.)
- Client assignment
- Country-specific defaults
- Currency (USD)
- 3-5 line items with:
  - Product + quality + package size
  - Quantity (100–1000 kg)
  - Unit price (₹150/kg demo price)
  - Calculated totals

---

## Data Size Reference

| Data Type | Count | Notes |
|-----------|-------|-------|
| Features | 15 | + 4 feature templates |
| Products | 100+ | From Product Library.xlsx |
| Qualities | 200+ | Multi-quality products |
| Package Sizes | 13 | Standard export sizes |
| Sanitization Types | 4 | Per-product costing |
| Certifications | 6 | Per-line-item costs |
| Countries | 10 | Target export markets |
| Vendor Prices | 160+ | 4 vendors × 40 SKUs |
| Clients | 7 | With country assignment |
| Users | 5 | 1 admin + 4 demo users |
| Sample Quotes | 6 | With 18-30 line items total |
| Currencies | 7 | All S&G target currencies |
| Margin Factors | 7 | Weighted scoring system |

**Database Size After Seeding:** ~5-10 MB (SQLite is efficient)

---

## Running the Seed

### Quick Start
```bash
cd quotation-builder
python seed.py
```

**First run:** Creates `quotation.db` + schema + all dummy data
**Prompts for:** Admin password (one-time)

### With Custom Database Path
```bash
python seed.py --db /path/to/quotation.db --product-lib "Product Library.xlsx"
```

### Expected Output
```
📊 SEEDING DATABASE WITH COMPREHENSIVE DUMMY DATA

✓ Seeding features...
  Inserted 15 features
✓ Seeding feature templates...
  Inserted 4 feature templates
✓ Seeding currencies...
  Inserted 7 currencies
✓ Seeding system settings...
  Inserted 21 system settings
✓ Seeding margin factors...
  Inserted 7 margin factors
✓ Seeding product library from Product Library.xlsx...
  Loaded 100+ products from Product Library
  Loaded 200+ qualities from Product Library
✓ Seeding standard package sizes (18 sizes)...
  Seeded 13 standard package sizes
✓ Seeding countries (10 target markets)...
  Seeded 10 countries
✓ Seeding sanitization & certifications...
  Seeded 4 sanitization types & 6 certifications
✓ Seeding vendor prices (40+ products × 4 vendors)...
  Seeded 160 vendor prices (4 vendors × 40 products)
✓ Seeding sample clients (7 clients)...
  Seeded 7 sample clients
✓ Seeding sample users (4 users with roles)...
  Seeded 4 sample users with roles
✓ Seeding sample quotes (6 quotes with line items)...
  Seeded 6 sample quotes with line items

📝 Creating admin user...
  Password: ████████
  Confirm:  ████████
  Created admin user (id=1)

✅ SEED COMPLETE!

Database ready for demo. Login with:
  • Email: admin@sandgexports.com
  • Password: (as set above)

Or login as demo users:
  • ravi@sandgexports.com (Price Updater)
  • priya@sandgexports.com (Quote Builder)
  • suresh@sandgexports.com (Super User)
```

---

## What You Can Demo

1. **Login Scenarios**
   - As Admin: See all features
   - As Price Updater (Ravi): Price entry only
   - As Quote Builder (Priya): Quote wizard + export
   - As Super User (Suresh): Everything user-facing

2. **Price Entry**
   - View vendor prices from 4 vendors
   - See price age (freshness)
   - Stale price warnings (7 days configurable)

3. **Quote Building**
   - Wizard: Step 1 (Client) → Step 2 (SKUs) → Step 3 (Review) → Step 4 (Export)
   - Cascading dropdowns with real data
   - Live cost calculation
   - Container recommendations

4. **Adaptive Pricing**
   - Margin adjustment based on 7 factors
   - Country-specific defaults (USA = FDA, UAE = Halal, etc.)
   - Client-specific overrides

5. **Analytics**
   - Quotes over time
   - Top products
   - Revenue by country
   - Margin distribution

6. **Business Rules**
   - View all 21 system settings
   - See margin factors with weights
   - Country profiles
   - Client profiles

---

## Next Steps

1. **Run the seed:**
   ```bash
   python seed.py
   ```

2. **Start the app:**
   ```bash
   python run.py
   ```

3. **Open browser:**
   ```
   http://localhost:8000
   ```

4. **Login as any demo user and explore**

---

## FAQ

**Q: Can I reset the demo data?**
A: Yes — delete `quotation.db` and run `python seed.py` again.

**Q: What if I need different dummy data?**
A: Edit the seed functions (e.g., `seed_vendor_prices()`) or modify the Product Library.xlsx and rerun.

**Q: Will this affect production?**
A: No — seed.py only runs once. Production database is backed up to OneDrive daily.

**Q: Can demo users create quotes with this data?**
A: Yes! All sample data is realistic and complete. You can create quotes immediately.

**Q: How long does seeding take?**
A: ~5-10 seconds (fast because SQLite is in-memory during seed).

---

## Detailed Feature Checklist (From SRS)

✅ **FR-001–006:** Feature-based RBAC
  - 15 features seeded
  - 4 roles (Price Updater, Quote Builder, Super User, Admin)
  - Users assigned to roles

✅ **FR-020–022:** Vendor Price Management
  - 160+ prices seeded from 4 vendors
  - Stale price indicators (age-based)
  - Bulk entry support

✅ **FR-040–043:** Quotation Builder
  - 6 sample quotes pre-seeded
  - Line items with product, quality, size, qty
  - Status tracking

✅ **FR-080–100:** Multi-currency, Countries, Analytics
  - 7 currencies seeded
  - 10 country profiles seeded
  - Sample quotes ready for analytics

✅ **FR-110–114:** Stale Price Blocking
  - Stale threshold: 7 days (configurable)
  - Vendor prices seeded with age variation

✅ **System Settings:** All 21 rules configured
  - Margin rules, costs, containers, system config

---

**Ready to demo!** 🚀
