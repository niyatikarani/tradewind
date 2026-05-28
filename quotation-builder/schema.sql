-- schema.sql — S&G Exports Quotation Builder
-- 26 tables: 8 master + 12 IAM/config + 6 operational

PRAGMA foreign_keys=ON;

-- MASTER DATA (8 tables)

CREATE TABLE IF NOT EXISTS products (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    name              TEXT NOT NULL UNIQUE,
    category          TEXT NOT NULL,
    competition_level TEXT NOT NULL DEFAULT 'medium' CHECK(competition_level IN ('low','medium','high')),
    is_active         INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS qualities (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    name       TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    UNIQUE(product_id, name)
);

CREATE TABLE IF NOT EXISTS package_sizes (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    display_name TEXT NOT NULL UNIQUE,
    weight_grams INTEGER NOT NULL,
    is_standard  INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS labour_rates (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    package_size_id INTEGER NOT NULL REFERENCES package_sizes(id) ON DELETE CASCADE,
    packing_cost    REAL NOT NULL DEFAULT 0,
    sticker_1side   REAL NOT NULL DEFAULT 0,
    sticker_2side   REAL NOT NULL DEFAULT 0,
    UNIQUE(package_size_id)
);

CREATE TABLE IF NOT EXISTS packaging_materials (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    package_size_id INTEGER NOT NULL REFERENCES package_sizes(id) ON DELETE CASCADE,
    pkts_per_carton INTEGER NOT NULL DEFAULT 1,
    carton_rate     REAL NOT NULL DEFAULT 0,
    sticker_rate    REAL NOT NULL DEFAULT 0,
    pouch_price     REAL NOT NULL DEFAULT 0,
    UNIQUE(package_size_id)
);

CREATE TABLE IF NOT EXISTS cbm_dimensions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    package_size_id INTEGER NOT NULL REFERENCES package_sizes(id) ON DELETE CASCADE,
    length_cm       REAL NOT NULL,
    breadth_cm      REAL NOT NULL,
    height_cm       REAL NOT NULL,
    UNIQUE(package_size_id)
);

CREATE TABLE IF NOT EXISTS sanitization_costs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id  INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    type        TEXT NOT NULL CHECK(type IN ('steam','chemical','none')),
    cost_per_kg REAL NOT NULL DEFAULT 0,
    UNIQUE(product_id, type)
);

CREATE TABLE IF NOT EXISTS certification_types (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    cost_per_kg REAL NOT NULL DEFAULT 0
);

-- IAM & CONFIG (12 tables)

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_active     INTEGER NOT NULL DEFAULT 1,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS features (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    key         TEXT NOT NULL UNIQUE,
    label       TEXT NOT NULL,
    description TEXT,
    category    TEXT NOT NULL DEFAULT 'general'
);

CREATE TABLE IF NOT EXISTS user_features (
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    feature_id INTEGER NOT NULL REFERENCES features(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, feature_id)
);

CREATE TABLE IF NOT EXISTS feature_templates (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    feature_ids TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS currencies (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    code                TEXT NOT NULL UNIQUE,
    name                TEXT NOT NULL,
    is_active           INTEGER NOT NULL DEFAULT 1,
    fx_variation_buffer REAL NOT NULL DEFAULT 0.02
);

CREATE TABLE IF NOT EXISTS countries (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    name                  TEXT NOT NULL UNIQUE,
    code                  TEXT NOT NULL UNIQUE,
    default_currency_id   INTEGER REFERENCES currencies(id),
    default_sanitization  TEXT NOT NULL DEFAULT 'steam' CHECK(default_sanitization IN ('steam','chemical','none')),
    risk_score            INTEGER NOT NULL DEFAULT 3 CHECK(risk_score BETWEEN 1 AND 5),
    notes                 TEXT
);

CREATE TABLE IF NOT EXISTS country_product_overrides (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    country_id            INTEGER NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    product_id            INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    override_sanitization TEXT NOT NULL CHECK(override_sanitization IN ('steam','chemical','none')),
    UNIQUE(country_id, product_id)
);

CREATE TABLE IF NOT EXISTS clients (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    name                  TEXT NOT NULL,
    country_id            INTEGER NOT NULL REFERENCES countries(id),
    margin_floor_override REAL,
    payment_risk          TEXT NOT NULL DEFAULT 'medium' CHECK(payment_risk IN ('low','medium','high')),
    credit_terms          TEXT,
    is_active             INTEGER NOT NULL DEFAULT 1,
    created_at            TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS client_price_locks (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id    INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    product_id   INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quality_id   INTEGER NOT NULL REFERENCES qualities(id) ON DELETE CASCADE,
    locked_price REAL NOT NULL,
    valid_from   TEXT NOT NULL,
    valid_to     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS margin_factors (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    factor_key    TEXT NOT NULL UNIQUE,
    label         TEXT NOT NULL,
    weight        REAL NOT NULL DEFAULT 1.0,
    scoring_tiers TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS list_prices (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id      INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quality_id      INTEGER NOT NULL REFERENCES qualities(id) ON DELETE CASCADE,
    package_size_id INTEGER NOT NULL REFERENCES package_sizes(id) ON DELETE CASCADE,
    list_price      REAL NOT NULL DEFAULT 0,
    UNIQUE(product_id, quality_id, package_size_id)
);

CREATE TABLE IF NOT EXISTS system_settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- OPERATIONAL & AUDIT (6 tables)

CREATE TABLE IF NOT EXISTS vendor_prices (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id   INTEGER NOT NULL REFERENCES products(id),
    quality_id   INTEGER NOT NULL REFERENCES qualities(id),
    price_per_kg REAL NOT NULL CHECK(price_per_kg > 0),
    vendor_name  TEXT,
    entered_by   INTEGER NOT NULL REFERENCES users(id),
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS fx_rates (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    currency_id INTEGER NOT NULL REFERENCES currencies(id),
    rate_vs_inr REAL NOT NULL,
    source      TEXT NOT NULL DEFAULT 'manual',
    entered_by  INTEGER REFERENCES users(id),
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS quotes (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_number          TEXT NOT NULL UNIQUE,
    client_id             INTEGER NOT NULL REFERENCES clients(id),
    country_id            INTEGER NOT NULL REFERENCES countries(id),
    currency_id           INTEGER NOT NULL REFERENCES currencies(id),
    status                TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','confirmed','cancelled')),
    has_stale_override    INTEGER NOT NULL DEFAULT 0,
    stale_override_reason TEXT,
    uploaded_excel        TEXT,
    parent_quote_id       INTEGER REFERENCES quotes(id),
    created_by            INTEGER NOT NULL REFERENCES users(id),
    created_at            TEXT NOT NULL DEFAULT (datetime('now')),
    confirmed_at          TEXT,
    notes                 TEXT
);

CREATE TABLE IF NOT EXISTS quote_line_items (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_id                 INTEGER NOT NULL REFERENCES quotes(id) ON DELETE CASCADE,
    product_id               INTEGER NOT NULL REFERENCES products(id),
    quality_id               INTEGER NOT NULL REFERENCES qualities(id),
    package_size_id          INTEGER NOT NULL REFERENCES package_sizes(id),
    quantity_kg              REAL NOT NULL CHECK(quantity_kg > 0),
    sanitization_type        TEXT NOT NULL DEFAULT 'steam' CHECK(sanitization_type IN ('steam','chemical','none')),
    label_sides              INTEGER NOT NULL DEFAULT 1 CHECK(label_sides IN (1,2)),
    certifications           TEXT NOT NULL DEFAULT '[]',
    vendor_price_per_kg      REAL NOT NULL CHECK(vendor_price_per_kg > 0),
    raw_material_inr         REAL NOT NULL DEFAULT 0,
    labour_inr               REAL NOT NULL DEFAULT 0,
    packaging_inr            REAL NOT NULL DEFAULT 0,
    sanitization_inr         REAL NOT NULL DEFAULT 0,
    certification_inr        REAL NOT NULL DEFAULT 0,
    loading_inr              REAL NOT NULL DEFAULT 0,
    transport_inr            REAL NOT NULL DEFAULT 0,
    subtotal_inr             REAL NOT NULL DEFAULT 0,
    cost_per_kg_inr          REAL NOT NULL DEFAULT 0,
    margin_pct               REAL NOT NULL DEFAULT 0,
    selling_price_per_kg_inr REAL NOT NULL DEFAULT 0,
    selling_price_fx         REAL NOT NULL DEFAULT 0,
    fx_rate_used             REAL NOT NULL DEFAULT 1,
    cbm_per_carton           REAL NOT NULL DEFAULT 0,
    num_cartons              INTEGER NOT NULL DEFAULT 0,
    total_cbm                REAL NOT NULL DEFAULT 0,
    is_overridden            TEXT NOT NULL DEFAULT '{}',
    override_values          TEXT NOT NULL DEFAULT '{}',
    original_calc_values     TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS field_override_log (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_line_item_id INTEGER NOT NULL REFERENCES quote_line_items(id) ON DELETE CASCADE,
    field_name         TEXT NOT NULL,
    original_value     TEXT,
    override_value     TEXT,
    reason             TEXT NOT NULL,
    user_id            INTEGER NOT NULL REFERENCES users(id),
    created_at         TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS rule_change_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(id),
    rule_category TEXT NOT NULL,
    rule_key      TEXT NOT NULL,
    scope_type    TEXT,
    old_value     TEXT,
    new_value     TEXT,
    reason        TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- INDEXES

CREATE INDEX IF NOT EXISTS idx_vendor_prices_product_quality ON vendor_prices(product_id, quality_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_fx_rates_currency ON fx_rates(currency_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_quotes_client ON quotes(client_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_quote_line_items_quote ON quote_line_items(quote_id);
CREATE INDEX IF NOT EXISTS idx_field_override_log_line ON field_override_log(quote_line_item_id);
CREATE INDEX IF NOT EXISTS idx_rule_change_log_category ON rule_change_log(rule_category, created_at DESC);
