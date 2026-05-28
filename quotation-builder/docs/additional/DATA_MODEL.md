# TradeWind — Data Model & System Design
### Version 4 — Phased build plan, compliance context separation, shipment templates

---

## The Rolls Royce Principle

> Too many controls → airplane cockpit. Powerful but needs a trained pilot. Can't sell to general users.
> Too few controls → toy car. Feels good in demo, useless in production.
> Right controls, right defaults → Rolls Royce. Everything works out of the box. The controls that exist are the ones that matter.

Applied to this data model:
- **Default everything.** When a quote is created: certifications from client profile, FX from auto-fetch, packaging from product catalog, margin from engine. Salesperson changes only what's unusual.
- **One source of truth per concept.** Risk isn't defined in two places. Margin floors aren't split between a `clients` column and settings. Every rule lives in the `rules` table.
- **Seed data is not configuration.** A 20ft container has fixed ISO dimensions. You don't give users a text box to change it. Seed data is loaded once; tenant configuration is separate.
- **Compliance doesn't touch the order flow.** HS codes, FSSAI licenses, shipping bills — none of these appear when creating a quote. They're captured at the right moment later, or generated automatically.

---

## The 4 Contexts

Every table in this system belongs to one of four contexts. The context determines when data is captured, by whom, and whether it ever appears in the order creation flow.

```
CONTEXT A — SETUP         (once, ever — during onboarding)
  Tenant profile, products, clients, packaging configs, vendors
  → Filled once. AI reads it. User never types it again per order.

CONTEXT B — ORDER FLOW    (per order, AI-assisted, fast)
  Quotes, sales orders
  → Human inputs: client + product + quantity
  → AI fills: certs, FX, packaging, freight, margin
  → Human reviews: price waterfall only

CONTEXT C — EXECUTION     (per shipment, by ops team)
  Purchase orders, packaging plans, packing runs
  → After SO is confirmed. Salesperson not involved.
  → Compliance data captured here at the right moment.

CONTEXT D — COMPLIANCE    (generated or post-shipment)
  Shipping bills, FIRC, quality certs, export incentive claims
  → Mostly generated from data already in the system.
  → Where manual entry exists, it's ops/finance, not sales.
```

---

## Build Phases

The 39 MUP tables are fully functional as a standalone export management system. Compliance tables are added in phases — they never add friction to the order flow.

```
PHASE 1 — MUP (build now)
  The complete commercial + operational loop:
  Quote → Sales Order → Purchase Order → Packaging → Packing → Analytics
  Includes: shipment templates, rule engine, packaging plans
  Target: SME exporter can run their full operation without spreadsheets

PHASE 2 — COMPLIANCE LAYER (3–6 months post-launch)
  Add regulatory data to existing flows at the right moment:
  HS codes on product records, FSSAI license on tenant profile,
  shipping bill ref on SOs, FIRC on payment receipt,
  batch records during packing execution
  Target: FSSAI traceability reports, eBRC reconciliation, DGFT compliance

PHASE 3 — INTELLIGENCE LAYER (AI-native, 6–12 months)
  Compliance documents generated automatically from Phase 2 data.
  AI coaches on margin, anomaly detection, demand forecasting,
  procurement consolidation, auto-draft POs for packaging materials.
  Target: system runs itself; humans approve, not operate
```

---

## Multi-Tenancy Architecture

TradeWind is a SaaS platform for multiple Indian export businesses. Each tenant is a separate company with fully isolated operational data.

### Isolation model: Row-level with PostgreSQL RLS

```sql
-- Every tenant-specific table has:
tenant_id  TEXT NOT NULL  REFERENCES tenants(id)

-- RLS policy on every such table:
CREATE POLICY tenant_isolation ON <table>
  USING (tenant_id = get_current_tenant());   -- SECURITY DEFINER function, not inline

-- Middleware sets this per request (SET LOCAL — not SET):
SET LOCAL app.current_tenant = '<tenant_id_from_session>';

-- Every table must have FORCE applied:
ALTER TABLE <table> FORCE ROW LEVEL SECURITY;

-- Every table must have composite index, tenant_id FIRST:
CREATE INDEX ON <table>(tenant_id, id);
CREATE INDEX ON <table>(tenant_id, created_at DESC);
```

**Three non-negotiable RLS rules (from production incident research):**
1. `FORCE ROW LEVEL SECURITY` on every table — table owners bypass policies without this
2. Always `SET LOCAL` in connection pools — `SET` persists to the next client on a pooled connection
3. Wrap `current_setting` in a `SECURITY DEFINER` function — without this, PostgreSQL evaluates it per row instead of caching it, causing 10–100× slowdown on analytics queries

### Shared vs Tenant-specific

| Category | Shared (no tenant_id) | Tenant-specific (has tenant_id) |
|---|---|---|
| Reference data | countries, currencies, ports, container_types | — |
| Product catalog | — | products, product_grades |
| Packaging | — | pack_materials, pack_configs |
| Markets | countries (base ISO data) | market_configs (your behaviour per country) |
| Clients & vendors | — | clients, vendors |
| Certifications | standard certs (tenant_id = null) | custom certs (tenant_id = X) |
| Rules | — | rules, margin_factors |
| Cost data | fx_rates (rate is universal) | material_prices, freight_rates |
| All operational | — | quotes, orders, POs, packing, events |

---

## Phase 1 — MUP Tables

---

### Layer 0 — Platform

---

#### `tenants` · Phase 1 · Context: Setup

The organisation using TradeWind.

| Column | Notes |
|---|---|
| `id` | TEXT slug — "sandg_exports" |
| `name` | Legal business name |
| `plan` | ENUM: starter / growth / enterprise |
| `country_iso2` | Where this exporter is based |
| `is_active` | |
| `created_at` | |

---

### Layer 1 — Reference Data (Global, Shared, Seed)

These tables describe the world. Populated once from official sources. Tenants cannot edit them.

---

#### `countries` · Phase 1 · Context: Setup (seed)

ISO country data — facts, not configuration.

| Column | Notes |
|---|---|
| `iso2` | PK — "DE", "IN", "AE" |
| `name` | "Germany" |
| `region` | "Europe", "Middle East" |
| `ispm15_required` | BOOL — EU/US/AU require heat-treated wooden packaging |
| `risk_tier` | ENUM: low / medium / high — sovereign/payment culture baseline |

---

#### `ports` · Phase 1 · Context: Setup (seed)

UN/LOCODE port registry. Used for freight rates, shipment docs, and delivery date estimates.

| Column | Notes |
|---|---|
| `locode` | PK — "INNSA", "DEHAM", "USLAX" |
| `name` | "Nhava Sheva", "Port of Hamburg" |
| `country_iso2` | FK → countries |
| `port_type` | ENUM: sea / air / road |
| `is_active` | Common ports active; obscure ones hidden |

---

#### `currencies` · Phase 1 · Context: Setup (seed)

| Column | Notes |
|---|---|
| `code` | PK — "EUR", "USD", "GBP", "AED" |
| `name` | "Euro" |
| `symbol` | "€" |
| `default_fx_buffer` | Default hedge buffer (0.015 = 1.5%). Tenant can override in tenant_settings. |

---

#### `container_types` · Phase 1 · Context: Setup (seed, read-only)

ISO standard container specs. **Physical facts, not configurable.** Never shown as editable fields in UI.

| Column | Notes |
|---|---|
| `iso_code` | PK — "20GP", "40GP", "40HC", "20RF" |
| `name` | "20ft Standard", "40ft High Cube" |
| `internal_length_mm` | 5,898 for 20GP |
| `internal_width_mm` | 2,352 |
| `internal_height_mm` | 2,395 (2,698 for HC) |
| `max_payload_kg` | 21,727 for 20GP |
| `tare_weight_kg` | Container's own weight |

Usable CBM = `(L × W × H) / 1,000,000,000` — computed, never stored.

---

### Layer 2 — Product Domain · Context: Setup

---

#### `products` · Phase 1

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `name` | "Cinnamon Sticks", "Turmeric Powder" |
| `category` | "spices", "herbs", "seeds" |
| `competition_level` | ENUM: low / medium / high — feeds margin engine |
| `is_active` | |

**Phase 2 addition:** `hs_code TEXT` — 8-digit ITC-HS code. Added to this table, not a separate table. One extra field on the product form, visible in "advanced" section. Required for shipping bills and customs docs.

---

#### `product_grades` · Phase 1

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `product_id` | FK → products |
| `name` | "Extra Bold", "FAQ", "C4 Special" |
| `grade_code` | Short code for labels |
| `sort_order` | Best grade first in dropdowns |

---

### Layer 3 — Packaging Domain · Context: Setup

The three physical levels of export packaging:

```
Consumer Unit  →  (optional Inner Pack)  →  Master Carton  →  Pallet  →  Container
 100g pouch          display box of 6         24 pouches/ctn
```
Levels 1–3 defined here. Pallet + Container handled by the Packaging Plan (Layer 12).

---

#### `pack_materials` · Phase 1

Physical packaging items your business stocks and procures. Every pouch, carton, and jar is a SKU here.

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `name` | "100g Kraft Pouch — Brown", "Std Corrugated Carton A" |
| `sku` | Internal stock code |
| `material_level` | ENUM: consumer_unit / inner_pack / master_carton / pallet |
| `quality_grade` | ENUM: standard / premium / export_grade |
| `unit_cost_inr` | Cost per piece |
| `current_stock_qty` | Live stock count |
| `reorder_point_qty` | Alert trigger level |
| `preferred_vendor_name` | Which supplier to reorder from |
| `lead_time_days` | |
| `is_active` | |

When an SO is confirmed, the system calculates material requirements. If `current_stock_qty < required`, a procurement alert fires. `po_lines` can reference `pack_material_id` to create a packaging materials PO alongside the raw materials PO.

---

#### `pack_configs` · Phase 1

The recipe for how a product+grade is packed for export. Replaces 4 V1 tables (`package_sizes`, `labour_rates`, `packaging_materials`, `cbm_dimensions`).

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `product_id` | FK → products |
| `grade_id` | FK → product_grades (nullable — some configs apply to all grades) |
| `name` | "100g Kraft Pouch, 24/ctn — Standard Export" |
| **Consumer unit** | |
| `consumer_unit_material_id` | FK → pack_materials |
| `net_weight_g` | Net product weight per unit |
| `label_sides` | 1 or 2 |
| **Inner pack (optional)** | |
| `inner_pack_material_id` | FK → pack_materials (nullable) |
| `units_per_inner_pack` | Nullable |
| **Master carton** | |
| `carton_material_id` | FK → pack_materials |
| `units_per_carton` | Consumer units (or inner packs if inner pack exists) per carton |
| `carton_length_mm` | |
| `carton_width_mm` | |
| `carton_height_mm` | |
| `carton_gross_weight_g` | Full loaded carton weight |
| `dimension_source` | ENUM: measured / manufacturer_stated / assumed — resolves carrier CBM disputes |
| **Packing constraints** | |
| `stackable` | BOOL — can cartons be stacked? |
| `orientation_locked` | BOOL — "this side up" requirement |
| `max_stack_layers` | Maximum cartons stacked vertically |
| `max_stack_weight_kg` | Weight limit per layer |
| `fragility` | ENUM: standard / fragile / delicate |
| `is_active` | |

Carton CBM = `(L × W × H) / 1,000,000,000` — computed at runtime.
Cartons needed = `ceil(qty_kg × 1000 / net_weight_g / units_per_carton)` — computed in cost engine.

**Phase 2 addition:** `label_batch_number_required BOOL`, `label_mfg_date_required BOOL`, `label_irradiation_declared BOOL` — FSSAI label compliance flags. Added to this form in the "compliance" tab, not the main config form.

---

### Layer 4 — Market & Compliance · Context: Setup

---

#### `certifications` · Phase 1

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | **Nullable** — null = global standard; non-null = tenant custom cert |
| `code` | "organic_usda", "kosher", "halal_isa", "fssai" |
| `name` | Display name |
| `issuing_body` | "USDA-NOP", "KSA" |
| `cost_per_kg_inr` | Default cost; overridable per product via rules |
| `validity_months` | For Phase 2 expiry tracking |

---

#### `market_configs` · Phase 1

Per-tenant settings for each export market. What `countries` *is* (ISO facts); what `market_configs` *means to your business* (your operational behaviour).

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `country_iso2` | FK → countries |
| `default_sanitization` | ENUM: steam / chemical / none |
| `preferred_loading_port_locode` | FK → ports |
| `required_cert_ids` | JSON array of cert IDs |
| `documentary_requirements` | JSON — `["fumigation_cert", "phytosanitary", "coo"]` |
| `notes` | |

One row per (tenant, country) pair. Only create rows for countries you actively export to.

---

### Layer 5 — Client Management · Context: Setup

---

#### `clients` · Phase 1

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `name` | "Müller GmbH", "Star Spices UK" |
| `country_iso2` | FK → countries |
| `city` | For shipping address on documents |
| `payment_terms` | ENUM: lc / tt / dp / open_account |
| `payment_risk` | ENUM: low / medium / high — this client's actual track record |
| `preferred_currency_code` | FK → currencies (nullable) |
| `is_active` | |
| `notes` | |
| `created_at` | |

---

#### `client_certs` · Phase 1

| Column | Notes |
|---|---|
| `tenant_id` | |
| `client_id` | FK → clients |
| `cert_id` | FK → certifications |
| `is_mandatory` | BOOL — true: always include; false: default-checked but removable |

---

#### `client_price_agreements` · Phase 1

Negotiated fixed prices. When active, overrides current market price in cost calculations.

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `client_id` | FK → clients |
| `product_id` | FK → products |
| `grade_id` | FK → product_grades |
| `agreed_price_inr_per_kg` | Fixed raw material cost for this client |
| `valid_from` | DATE |
| `valid_to` | DATE |
| `agreed_by` | FK → users |
| `notes` | |

---

### Layer 6 — Vendor Management · Context: Setup

---

#### `vendors` · Phase 1

Raw material and packaging suppliers.

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `name` | Supplier business name |
| `vendor_type` | ENUM: raw_material / packaging / both |
| `country_iso2` | FK → countries |
| `city` | |
| `cert_ids_held` | JSON array — certifications this vendor holds (critical: kosher order needs kosher vendor) |
| `product_categories` | JSON array — what they supply |
| `payment_terms` | ENUM |
| `lead_time_days` | |
| `min_order_kg` | |
| `contact_info` | JSON — email, phone, contact person |
| `is_active` | |

---

### Layer 7 — Cost Inputs · Context: Setup + Order Flow

All three are timeseries — each row is a point-in-time observation. "Current" always means `ORDER BY created_at DESC LIMIT 1`.

---

#### `material_prices` · Phase 1

Raw material cost timeseries. The most recent row for a (tenant, product, grade) is the current price.

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `product_id` | FK → products |
| `grade_id` | FK → product_grades |
| `vendor_id` | FK → vendors (nullable) |
| `price_per_kg_inr` | |
| `source` | ENUM: vendor_quote / market_spot / negotiated |
| `entered_by` | FK → users |
| `created_at` | When recorded |
| `valid_from` | DATE (nullable) |
| `valid_to` | DATE (nullable) |

**Stale detection:** `age_days = today − created_at`. If `age_days > tenant_settings.stale_threshold_days`, price is stale. UI flags orange. Override requires a reason. Reason is logged.

*Performance note: BRIN index on `created_at` — append-only timeseries data benefits dramatically from BRIN over B-tree.*

---

#### `fx_rates` · Phase 1 · Shared (no tenant_id)

Exchange rate timeseries. Shared — EUR/INR is the same rate for all exporters.

| Column | Notes |
|---|---|
| `id` | PK |
| `currency_code` | FK → currencies |
| `rate_vs_inr` | e.g., 89.42 = 1 USD = ₹89.42 |
| `source` | ENUM: auto_api / manual |
| `fetched_at` | Exact moment recorded |
| `entered_by` | FK → users (null if auto-fetched) |

**Auto-fetch:** Background job runs every 24h. Inserts row with `source = auto_api`. Rates are never modified — only appended.
**Snapshot on save:** At quote save time, latest rate is read and stored in `quote_lines.fx_rate_used`. Immutable forever after.
**Staleness:** Latest rate > 24h → warning in UI. Warn, not block.

*Performance note: BRIN index on `fetched_at`, composite covering index `(currency_code, fetched_at DESC)` for the common "latest rate per currency" query.*

---

#### `freight_rates` · Phase 1

Port-to-port freight rates. Replaces the flat `transport_per_kg` global setting.

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | Your negotiated rates |
| `carrier_name` | "Maersk", "MSC", "Road via Mundra" |
| `mode` | ENUM: sea / air / road |
| `origin_locode` | FK → ports |
| `destination_locode` | FK → ports |
| `container_iso_code` | FK → container_types (nullable — for LCL use rate_per_cbm) |
| `rate_inr` | Base rate |
| `rate_basis` | ENUM: per_container / per_kg / per_cbm |
| `valid_from` | DATE |
| `valid_to` | DATE |
| `transit_days` | For delivery date estimation |

If no matching freight rate row exists, cost engine falls back to `tenant_settings.default_freight_per_kg` and flags it for confirmation.

---

### Layer 8 — Rules & Margin Engine · Context: Setup

---

#### `rules` · Phase 1

Every piece of business logic that operations teams change over time. One table, one pattern. No special-case columns on other tables.

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `rule_key` | What this rule controls — see table below |
| `scope_level` | ENUM: global / product / country / client |
| `scope_id` | ID of the country/client/product this applies to. NULL if global. |
| `product_id` | Optional — narrow a country/client rule to a specific product |
| `grade_id` | Optional — narrow further to a grade |
| `rule_value` | JSON — shape depends on rule_key |
| `priority` | INT — higher wins on conflict |
| `active_from` | DATE |
| `active_to` | DATE (nullable = still active) |
| `created_by` | FK → users |
| `notes` | Why was this rule created |

**Valid rule keys:**

| key | rule_value example | Controls |
|---|---|---|
| `sanitization_method` | `{"method": "chemical"}` | Sanitisation for this market/product |
| `cert_required` | `{"cert_id": 2, "mandatory": true}` | Certification required at this scope |
| `margin_floor` | `{"floor_pct": 12.0}` | Minimum acceptable margin |
| `margin_cap` | `{"cap_pct": 22.0}` | Maximum margin |
| `fx_buffer` | `{"buffer": 0.02}` | FX hedge buffer |
| `packaging_restriction` | `{"max_stack": 3, "fragility": "fragile"}` | Packing constraints for this product/market |

**Resolution:** Collect all matching active rows for (rule_key, context). Sort by priority DESC. Take the first. If none, fall back to `tenant_settings`.

**What this replaces:** `margin_floor_override` column on `clients`, `country_product_overrides` table, hardcoded fallback logic in `rule_resolver.py`. One place. One UI.

---

#### `rule_audit_log` · Phase 1

Every rule change with reason and actor. Required for compliance: "show me why we changed the sanitisation requirement for cinnamon to Egypt in March."

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `rule_id` | FK → rules |
| `action` | ENUM: created / updated / deactivated |
| `old_value` | JSON |
| `new_value` | JSON |
| `reason` | Required, non-empty |
| `changed_by` | FK → users |
| `changed_at` | DATETIME |

---

#### `margin_factors` · Phase 1

Scoring model for margin suggestions. Each factor has weighted tiers that adjust base margin up or down.

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `factor_key` | volume_kg / advance_payment_pct / client_order_count / competition_level / price_volatility_pct / country_risk / urgency_days |
| `label` | Display name |
| `weight` | How much this factor's adjustment contributes |
| `scoring_tiers` | JSON — `[{"min": 0, "max": 100, "adjustment": -2.0}, {"min": 500, "adjustment": 1.5}]` |

---

### Layer 9 — Quotation · Context: Order Flow

---

#### `shipment_templates` · Phase 1

**The single most impactful table for reducing input friction.** 95% of an exporter's orders are the same products, same client, same packaging, same certifications — repeated. A template pre-fills a new quote to ~80% complete. Data entry becomes "select template, confirm differences."

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `name` | "Müller Hamburg — Cinnamon Standard", "Star UK — Mixed Spices" |
| `description` | When to use this template |
| `client_id` | FK → clients |
| `country_iso2` | FK → countries |
| `currency_code` | FK → currencies |
| `incoterm` | ENUM: exw / fob / cfr / cif |
| `port_of_loading_locode` | FK → ports |
| `port_of_discharge_locode` | FK → ports |
| `payment_terms` | ENUM |
| `template_lines` | JSON — array of line item defaults: `[{"product_id": 1, "grade_id": 2, "pack_config_id": 3, "cert_ids": [1,2], "sanitization_type": "steam", "default_qty_kg": 500}]` |
| `notes` | |
| `is_active` | |
| `created_by` | FK → users |
| `last_used_at` | DATETIME — for surfacing most-used templates first |

When a new quote is created from a template, all fields pre-populate. The salesperson changes only: quantity (if different), margin (if special), and any client-specific adjustments. Everything else is already correct.

---

#### `quotes` · Phase 1

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `quote_number` | "SGE-2025-1047" |
| `template_id` | FK → shipment_templates (nullable — which template was used) |
| `client_id` | FK → clients |
| `country_iso2` | Denormalised — one client ships to multiple destinations |
| `currency_code` | FK → currencies |
| `incoterm` | ENUM: exw / fob / cfr / cif / cpt |
| `status` | ENUM: draft / sent / confirmed / cancelled / expired |
| `valid_until` | DATE |
| `has_stale_override` | BOOL |
| `stale_override_reason` | TEXT |
| `parent_quote_id` | FK → quotes — for duplicated/revised quotes |
| `source` | ENUM: manual / excel_import / template / ai_intake |
| `intake_raw` | JSON — raw WhatsApp/email text if AI-parsed (Phase 3 forward hook) |
| `created_by` | FK → users |
| `created_at` | |
| `confirmed_at` | |
| `notes` | External-facing (appears on PDF) |
| `internal_notes` | Internal only |

---

#### `quote_lines` · Phase 1

Full cost waterfall — every component named and stored separately.

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `quote_id` | FK → quotes |
| `product_id` | FK → products |
| `grade_id` | FK → product_grades |
| `pack_config_id` | FK → pack_configs |
| `quantity_kg` | |
| `sanitization_type` | ENUM — resolved from rules at calculation time |
| `label_sides` | 1 or 2 |
| `cert_ids_applied` | JSON array |
| `material_price_id` | FK → material_prices — which entry was used (for audit) |
| **Cost components (INR)** | |
| `raw_material_inr` | vendor_price × quantity_kg |
| `labour_inr` | Packing + labelling |
| `packaging_inr` | Pouches + cartons + stickers |
| `sanitization_inr` | |
| `certification_inr` | Sum of cert costs |
| `freight_inr` | From freight_rates or manual |
| `loading_inr` | Port loading/handling |
| `customs_inr` | CHA + customs duty allocation |
| `subtotal_inr` | Sum of all 8 components |
| `cost_per_kg_inr` | subtotal / quantity_kg |
| **Margin & selling price** | |
| `margin_pct` | |
| `selling_price_per_kg_inr` | cost × (1 + margin/100) |
| `fx_rate_used` | **Snapshot.** Rate at save time. Never recalculated. |
| `selling_price_per_kg_fx` | selling_price_inr / fx_rate_used |
| **CBM** | |
| `carton_dims_snapshot` | JSON — L/W/H at calculation time. Snapshot so CBM is stable if config changes later. |
| `num_cartons` | |
| `total_cbm` | |
| **Override tracking** | |
| `overridden_fields` | JSON: `{"margin_pct": true, "freight_inr": true}` |
| `override_values` | JSON: the manually entered values |
| `original_calc_values` | JSON: what the engine computed before override |
| `calculation_steps` | JSON: full waterfall array for price breakdown display |

---

#### `quote_snapshots` · Phase 1

Immutable version history. When a quote is sent, its full state is frozen here. Allows PDF regeneration for any historical version without re-querying 8 tables.

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `quote_id` | FK → quotes |
| `version_number` | Auto-incrementing per quote |
| `trigger` | ENUM: draft_saved / sent_to_client / revised / confirmed |
| `snapshot_json` | Complete state: header + all lines + all computed values |
| `created_by` | FK → users |
| `created_at` | |
| `change_summary` | "Increased cinnamon margin from 12% to 15% per client request" |

---

### Layer 10 — Sales Order · Context: Order Flow

---

#### `sales_orders` · Phase 1

Confirmed quote becomes a Sales Order. The SO drives everything downstream: procurement, packaging, packing.

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `so_number` | "SO-2025-0089" |
| `quote_id` | FK → quotes |
| `quote_snapshot_id` | FK → quote_snapshots — which version was confirmed |
| `client_id` | Denormalised |
| `status` | ENUM: pending / processing / packed / shipped / delivered / cancelled |
| `incoterm` | Locked from confirmed quote |
| `payment_terms` | ENUM |
| `delivery_deadline` | Client's required delivery date |
| `estimated_ship_date` | |
| `port_of_loading_locode` | FK → ports |
| `port_of_discharge_locode` | FK → ports |
| `created_at` | |
| `confirmed_at` | |
| `notes` | |

---

#### `so_lines` · Phase 1

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `so_id` | FK → sales_orders |
| `quote_line_id` | FK → quote_lines |
| `product_id` | Denormalised |
| `grade_id` | |
| `pack_config_id` | |
| `qty_kg_quoted` | From confirmed snapshot |
| `qty_kg_confirmed` | Actual confirmed qty (may differ slightly) |
| `unit_price_fx` | Locked from snapshot |
| `total_value_fx` | |
| `num_cartons` | Recalculated from confirmed qty |

---

### Layer 11 — Purchase Orders · Context: Execution

Two types of procurement: raw materials from product vendors, and packaging materials from packaging suppliers. Both are POs.

---

#### `purchase_orders` · Phase 1

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `po_number` | "PO-2025-0412" |
| `vendor_id` | FK → vendors |
| `so_id` | FK → sales_orders (nullable — speculative/stock POs have no SO) |
| `po_type` | ENUM: raw_material / packaging / mixed |
| `status` | ENUM: draft / sent / confirmed / partially_received / fully_received / cancelled |
| `expected_delivery_date` | DATE |
| `actual_delivery_date` | DATE |
| `total_value_inr` | |
| `created_by` | FK → users |
| `created_at` | |
| `confirmed_at` | |
| `notes` | |

---

#### `po_lines` · Phase 1

One PO line is EITHER a raw material line OR a packaging material line. The two `_id` columns are mutually exclusive.

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `po_id` | FK → purchase_orders |
| `line_type` | ENUM: raw_material / pack_material |
| `product_id` | FK → products (non-null if raw_material) |
| `grade_id` | FK → product_grades (non-null if raw_material) |
| `pack_material_id` | FK → pack_materials (non-null if pack_material) |
| `so_line_id` | FK → so_lines (nullable) |
| `qty_ordered` | kg for raw material; pcs for pack material |
| `unit` | "kg" or "pcs" |
| `unit_price_inr` | |
| `total_inr` | |
| `qty_received` | Updated on receipt |
| `batch_number` | Vendor's batch/lot number — Phase 2 traceability link |

---

### Layer 12 — Packaging Plan · Context: Execution

**Who uses this:** The system calculates; ops supervisor reviews and approves. No floor data entry.

The system runs the packing algorithm automatically when the SO is confirmed: given the carton dimensions from `pack_configs` and container specs from `container_types`, it figures out how many cartons fit, whether CBM or payload is the binding constraint, and which container type to book. The ops supervisor sees the result and either approves it or adjusts the container type.

```
System calculates:  expected cartons, CBM, weight, container recommendation
Ops confirms:       "yes, book a 40HC"  or  changes container type
Floor does nothing: all they need is the expected carton count per SKU (printed label / task card)
```

---

#### `pack_plans` · Phase 1

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `so_id` | FK → sales_orders |
| `calculated_by` | FK → users |
| `calculated_at` | DATETIME |
| `container_iso_code` | FK → container_types — recommended container |
| `container_count` | How many containers needed |
| `total_cartons` | |
| `total_gross_weight_kg` | Calculated from carton weights in pack_configs |
| `total_net_weight_kg` | |
| `total_cbm` | |
| `utilisation_cbm_pct` | total_cbm / container usable CBM |
| `utilisation_weight_pct` | total_weight / container max_payload |
| `binding_constraint` | ENUM: cbm / weight / stack_height / none — which limit was hit first |
| `constraint_checks` | JSON — warnings only: `[{"check": "ispm15", "status": "warn", "msg": "EU needs heat-treated pallets"}]` |
| `is_current` | BOOL — true for most recent plan on this SO |

Note: `plan_layout` (3D container visualisation) is Phase 3 — AI generates the optimal loading sequence. Not needed for Phase 1.

---

#### `pack_plan_items` · Phase 1

One row per SO line. The expected carton count is what the floor team works from.

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `plan_id` | FK → pack_plans |
| `so_line_id` | FK → so_lines |
| `pack_config_id` | FK → pack_configs |
| `qty_kg` | |
| `num_cartons` | **The one number the floor team needs** |
| `total_cbm` | |
| `gross_weight_kg` | |

---

### Layer 13 — Packing Execution · Context: Execution

**The industry model: expected plan → exception-based confirmation.**

The system pre-builds the expected load from the packaging plan. The floor supervisor's job is to confirm it happened — not re-enter it. Every WMS (SAP EWM, Oracle, Dynamics 365, Increff) works this way: scan-and-confirm, not form-fill.

```
Before loading:
  System shows: "Expected 480 cartons · 3 SKUs · ~12,000 kg net"

During loading:
  Floor worker loads cartons (no software interaction required)

After loading — supervisor opens mobile screen:
  [Scan/enter container number]    ← 1 field
  [Carton count matches? ✓ / edit] ← 1 tap or adjustment
  [Seal number]                    ← 1 field (entered after sealing)
  [Gross weight from weigh-bridge] ← 1 field (actual measurement)
  [Generate Packing List →]        ← document auto-generated
```

**Total new data entered at stuffing: 4 fields.** Everything else was captured earlier.

The packing list for the CHA is generated automatically from those 4 fields + the packing run item data. No re-typing of product descriptions, quantities, or HS codes.

---

#### `packing_runs` · Phase 1

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `so_id` | FK → sales_orders |
| `plan_id` | FK → pack_plans |
| `status` | ENUM: not_started / in_progress / completed / qc_hold / cancelled |
| `supervisor_id` | FK → users |
| `warehouse` | Location identifier |
| `started_at` | |
| `completed_at` | |
| `container_booking_ref` | Booking ref from shipping line — entered by ops before stuffing |
| **Stuffing fields (4 fields entered at loading dock)** | |
| `container_number` | e.g., "MSCU1234567" — scanned or typed once |
| `actual_gross_weight_kg` | Weigh-bridge reading — the only measurement taken at stuffing |
| `seal_number` | Entered after sealing — must match B/L exactly |
| `bl_number` | Bill of Lading number — entered after carrier issues B/L |
| `stuffing_date` | DATE |
| `photo_keys` | JSON array of file paths — optional documentation |
| `notes` | Exceptions only: "3 cartons damaged, left behind" |

---

#### `packing_run_items` · Phase 1

Actuals vs plan per product. If everything went to plan, `actual_cartons = planned_cartons` and no one types anything — it is set automatically on run completion. Supervisor only edits if there was an exception (damage, short load, substitution).

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `run_id` | FK → packing_runs |
| `so_line_id` | FK → so_lines |
| `plan_item_id` | FK → pack_plan_items |
| `planned_cartons` | From packaging plan — pre-filled, shown to supervisor |
| `actual_cartons` | Defaults to planned_cartons; edit only on exception |
| `planned_kg` | |
| `actual_kg` | Defaults to planned_kg; edit only on exception |
| `variance_pct` | (actual − planned) / planned × 100 — computed |
| `batch_numbers` | JSON array — vendor batch/lot numbers (Phase 2 traceability) |
| `qc_status` | ENUM: pending / passed / failed |
| `qc_notes` | |
| `qc_by` | FK → users |
| `qc_at` | DATETIME |

---

### Layer 14 — Identity & Access · Context: Setup

---

#### `users` · Phase 1

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `name` | |
| `email` | UNIQUE within tenant |
| `password_hash` | bcrypt |
| `role` | ENUM: admin / sales / operations / viewer |
| `is_active` | |
| `created_at` | |
| `last_login_at` | |

#### `features` · Phase 1 · Global

Fine-grained feature flags: `quote.create`, `rule_engine.edit`, `analytics.export`, etc.

#### `user_features` · Phase 1

user_id + feature_id junction — which features this user has.

#### `feature_templates` · Phase 1 · Global

Pre-packaged feature bundles: "sales_pack", "ops_pack", "admin_pack".

---

### Layer 15 — Settings & Audit · Context: Setup + All

---

#### `tenant_settings` · Phase 1

Per-tenant operational defaults.

| Key examples | Value |
|---|---|
| `base_margin` | "10.0" |
| `margin_floor` | "8.0" |
| `margin_cap` | "25.0" |
| `stale_threshold_days` | "5" |
| `quote_number_prefix` | "SGE" |
| `loading_per_kg_inr` | "0.80" |
| `default_freight_per_kg` | "1.50" |
| `fx_buffer_usd` | "0.015" |

Columns: `tenant_id`, `key`, `value` TEXT, `description`, `updated_by`, `updated_at`.

---

#### `override_log` · Phase 1 · Context: Order Flow

Per-field audit when a calculated value is manually changed in a quote.

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `quote_line_id` | FK → quote_lines |
| `field_name` | "margin_pct", "freight_inr" |
| `original_value` | What engine computed |
| `override_value` | What was manually entered |
| `reason` | Required |
| `user_id` | FK → users |
| `created_at` | |

---

#### `events` · Phase 1 · Context: All

Append-only event log with SHA-256 hash chain. Scoped to orders, SOs, and packing — NOT applied to POs, quotes, or packaging plans (overhead not justified for those). Powers the traceability timeline and Phase 3 AI coaching.

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `aggregate_type` | ENUM: sales_order / packing_run — strictly scoped |
| `aggregate_id` | INT |
| `event_type` | so_confirmed / so_status_changed / packing_started / qc_failed / container_stuffed / bl_issued |
| `event_data` | JSON — event payload |
| `actor_id` | FK → users |
| `source` | ENUM: manual / system / api |
| `occurred_at` | DATETIME |
| `prev_hash` | SHA-256 of previous event row |
| `event_hash` | SHA-256(prev_hash + event_type + event_data + occurred_at) |

*Performance note: BRIN index on `occurred_at`. Separate from OLTP queries — analytics views read this table via materialized views, not direct joins.*

---

## Phase 2 — Compliance Layer

> **When to build:** 3–6 months post-launch, once the MUP is live and tenants are actively using it.
> **Who fills it:** Ops and finance teams, not salespeople.
> **How it's surfaced:** Existing forms get a "Compliance" tab. No new screens for order creation.

---

### Added to existing tables

These are columns added to Phase 1 tables — not new screens, just new fields in the "advanced" or "compliance" section of existing forms:

| Table | Column added | Moment captured |
|---|---|---|
| `products` | `hs_code TEXT` | Admin fills once on product record |
| `tenants` | `iec_code TEXT`, `fssai_license_number TEXT`, `fssai_license_expiry DATE`, `spice_board_reg TEXT` | Filled during onboarding step 2 |
| `sales_orders` | `shipping_bill_number TEXT`, `shipping_bill_date DATE` | Ops fills after customs clearance |
| `sales_orders` | `firc_number TEXT`, `firc_date DATE`, `firc_amount_inr REAL` | Finance fills after payment receipt (RBI FEMA compliance) |
| `po_lines` | `batch_number` already exists — surfaced in packing execution UI in Phase 2 |
| `pack_configs` | `label_batch_number_required BOOL`, `label_mfg_date_required BOOL`, `label_irradiation_declared BOOL` | Admin fills on packaging config |

---

### New Phase 2 Tables

---

#### `batch_records` · Phase 2 · Context: Execution

Lot-level traceability from raw material to shipped container. Required by FSSAI and EU RASFF. The 1,200+ EU safety rejections on Indian spices in 2024 (₹1,800 crore in losses) trace back to inability to prove which lot was contaminated.

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `product_id` | FK → products |
| `grade_id` | FK → product_grades |
| `batch_number` | Internal batch identifier |
| `mfg_date` | Manufacturing / packing date |
| `expiry_date` | |
| `po_line_id` | FK → po_lines — which purchase this batch came from |
| `packing_run_item_id` | FK → packing_run_items — which packing execution used this batch |
| `quantity_kg` | |
| `test_result_status` | ENUM: pending / passed / failed |
| `test_certificate_path` | File path/S3 key of the test report |
| `notes` | |

Connects the full chain: vendor batch → PO receipt → packing execution → exported container. One query generates the FSSAI traceability report.

---

#### `quality_certificates` · Phase 2 · Context: Execution

Test certificates required before loading: pesticide residue, aflatoxin, moisture content. Required by EU, US FDA, and Gulf countries.

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `batch_id` | FK → batch_records |
| `cert_type` | ENUM: pesticide_residue / aflatoxin / moisture / microbiological / coa |
| `lab_name` | Which lab issued it |
| `certificate_number` | |
| `issue_date` | DATE |
| `expiry_date` | DATE |
| `result_summary` | TEXT — e.g., "All parameters within EU MRL limits" |
| `file_path` | S3 key or file path |
| `so_id` | FK → sales_orders (nullable — cert may cover multiple SOs) |

---

#### `letters_of_credit` · Phase 2 · Context: Execution

LC is the dominant payment instrument in Indian B2B export. Every Indian EXIM software tracks it. Expires, has partial shipment allowances, requires documents presented within a deadline.

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `so_id` | FK → sales_orders |
| `lc_number` | Issued by buyer's bank |
| `issuing_bank` | |
| `advising_bank` | Your bank |
| `lc_amount_fx` | Amount in quote currency |
| `currency_code` | FK → currencies |
| `expiry_date` | DATE — must present documents before this |
| `partial_shipment_allowed` | BOOL |
| `transhipment_allowed` | BOOL |
| `latest_shipment_date` | DATE |
| `status` | ENUM: received / documents_presented / negotiated / retired |
| `notes` | |

---

#### `export_incentive_claims` · Phase 2 · Context: Compliance

RoDTEP (Remission of Duties and Taxes on Exported Products), DFIA, and EPCG scheme tracking. These are cash-equivalent refunds — real money that exporters claim per shipment but often don't track systematically.

| Column | Notes |
|---|---|
| `id` | PK |
| `tenant_id` | |
| `so_id` | FK → sales_orders |
| `scheme` | ENUM: rodtep / dfia / epcg / meis_legacy |
| `shipping_bill_number` | Reference |
| `claim_amount_inr` | |
| `status` | ENUM: eligible / filed / scrip_received / credited |
| `filed_date` | DATE |
| `scrip_number` | RoDTEP scrip number when received |
| `notes` | |

---

## Phase 3 — Intelligence Layer

> **When to build:** 6–12 months post-launch. Built on top of Phase 2 data.
> **How it works:** AI reads from existing tables. No new data entry for users.

Phase 3 adds no new tables — it adds AI services that READ from what's already there:

| AI Feature | Data it reads |
|---|---|
| Quote intake from WhatsApp/email | `clients`, `products`, `pack_configs`, `market_configs` → auto-fills `quotes` |
| Margin coaching | `quote_lines` history, `margin_factors`, country + client risk → suggests margin |
| Material requirements prediction | `so_lines` pipeline, `pack_materials.current_stock_qty` → auto-drafts `po_lines` |
| Packing anomaly detection | `events`, `packing_run_items.variance_pct` → flags delays vs. historical average |
| FSSAI traceability report | `batch_records`, `quality_certificates`, `packing_run_items`, `po_lines` → generated PDF |
| RoDTEP auto-filing prep | `export_incentive_claims`, `shipping_bills`, `so_lines` → auto-populated claim form |
| CBM optimisation suggestion | `pack_configs`, `so_lines`, `container_types` → "switch to 30/carton, save ₹8,000 freight" |
| Procurement consolidation | Multiple `so_lines` → "combine 3 cinnamon POs to one vendor this week" |

The forward-compatibility hooks (JSON columns: `intake_raw` on `quotes`, `event_data` on `events`) were built in Phase 1 specifically for this — no schema changes needed when Phase 3 arrives.

---

## Cross-Cutting: Risk, Margin, FX

### Risk — one formula, two inputs

```
country_risk_score:  countries.risk_tier  → {low: 2, medium: 3, high: 4}
client_risk_score:   clients.payment_risk → {low: -1, medium: 0, high: +1}
effective_risk = clamp(country_risk_score + client_risk_score, 1, 5)
```

Neither alone is complete. Both are inputs to ONE function. Effective risk feeds `margin_factors` as the `country_risk` scoring tier input.

### Margin — one source of truth

```
Resolution order (most specific wins):
  1. rules WHERE scope_level='client'  AND scope_id=quote.client_id
  2. rules WHERE scope_level='country' AND scope_id=quote.country_iso2
  3. rules WHERE scope_level='product' AND scope_id=quote.product_id
  4. tenant_settings.margin_floor / margin_cap  ← ultimate fallback

Base = tenant_settings.base_margin
Adjustments = Σ(margin_factor scoring results × weights)
Final = clamp(base + adjustments, effective_floor, effective_cap)
```

No `margin_floor_override` column on `clients`. All margin rules live in the `rules` table.

### FX — auto-fetch with snapshot

```
Background job (every 24h) → fetch from ExchangeRate API → INSERT fx_rates (source=auto_api)
Manual entry always allowed → INSERT fx_rates (source=manual)
At quote save: read latest rate, apply buffer, store in quote_lines.fx_rate_used (immutable)
UI warning if latest rate > 24h old. Warn, not block.
Buffer = tenant_settings.fx_buffer_{code} OR currencies.default_fx_buffer
```

---

## Full Table Index

| # | Table | Phase | Context | Shared/Tenant |
|---|---|---|---|---|
| 1 | `tenants` | 1 | Setup | Global |
| 2 | `countries` | 1 | Setup seed | Shared |
| 3 | `ports` | 1 | Setup seed | Shared |
| 4 | `currencies` | 1 | Setup seed | Shared |
| 5 | `container_types` | 1 | Setup seed, read-only | Shared |
| 6 | `products` | 1 | Setup | Tenant |
| 7 | `product_grades` | 1 | Setup | Tenant |
| 8 | `pack_materials` | 1 | Setup | Tenant |
| 9 | `pack_configs` | 1 | Setup | Tenant |
| 10 | `certifications` | 1 | Setup | Shared + Tenant |
| 11 | `market_configs` | 1 | Setup | Tenant |
| 12 | `clients` | 1 | Setup | Tenant |
| 13 | `client_certs` | 1 | Setup | Tenant |
| 14 | `client_price_agreements` | 1 | Setup | Tenant |
| 15 | `vendors` | 1 | Setup | Tenant |
| 16 | `material_prices` | 1 | Setup | Tenant |
| 17 | `fx_rates` | 1 | Order Flow | Shared |
| 18 | `freight_rates` | 1 | Setup | Tenant |
| 19 | `rules` | 1 | Setup | Tenant |
| 20 | `rule_audit_log` | 1 | Setup | Tenant |
| 21 | `margin_factors` | 1 | Setup | Tenant |
| 22 | `shipment_templates` | 1 | Setup | Tenant |
| 23 | `quotes` | 1 | Order Flow | Tenant |
| 24 | `quote_lines` | 1 | Order Flow | Tenant |
| 25 | `quote_snapshots` | 1 | Order Flow | Tenant |
| 26 | `sales_orders` | 1 | Order Flow | Tenant |
| 27 | `so_lines` | 1 | Order Flow | Tenant |
| 28 | `purchase_orders` | 1 | Execution | Tenant |
| 29 | `po_lines` | 1 | Execution | Tenant |
| 30 | `pack_plans` | 1 | Execution | Tenant |
| 31 | `pack_plan_items` | 1 | Execution | Tenant |
| 32 | `packing_runs` | 1 | Execution | Tenant |
| 33 | `packing_run_items` | 1 | Execution | Tenant |
| 34 | `users` | 1 | Setup | Tenant |
| 35 | `features` | 1 | Setup | Global |
| 36 | `user_features` | 1 | Setup | Tenant |
| 37 | `feature_templates` | 1 | Setup | Global |
| 38 | `tenant_settings` | 1 | Setup | Tenant |
| 39 | `override_log` | 1 | Order Flow | Tenant |
| 40 | `events` | 1 | All | Tenant |
| 41 | `batch_records` | 2 | Execution | Tenant |
| 42 | `quality_certificates` | 2 | Execution | Tenant |
| 43 | `letters_of_credit` | 2 | Execution | Tenant |
| 44 | `export_incentive_claims` | 2 | Compliance | Tenant |
| — | `hs_code` column | 2 | Added to `products` | — |
| — | `iec_code`, `fssai_license_*` | 2 | Added to `tenants` | — |
| — | `shipping_bill_*`, `firc_*` | 2 | Added to `sales_orders` | — |
| — | Label compliance flags | 2 | Added to `pack_configs` | — |

**Phase 1: 40 tables.** Complete commercial + operational loop.
**Phase 2: 4 new tables + ~12 new columns across existing tables.** Zero new friction on order creation flow.
**Phase 3: 0 new tables.** AI reads Phase 1 + 2 data. No schema changes.
