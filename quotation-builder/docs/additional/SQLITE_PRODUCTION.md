# SQLite in Production Deployment

## Short Answer
**SQLite works great for your app.** You have 3-5 concurrent users, ~100 queries/day. SQLite handles 100K+ transactions/day. No need for PostgreSQL/MySQL.

---

## Why SQLite is Perfect for S&G Exports

| Concern | SQLite Solution | Why It Works |
|---------|-----------------|-------------|
| **Scaling** | Single-file database | 5 users × WAL mode = no bottleneck |
| **Reliability** | PRAGMA journal_mode=WAL | Crash-safe, concurrent reads |
| **Backup** | Copy one .db file | Atomic single-file backup to OneDrive |
| **Deployment** | No separate DB server | Ship app + quotation.db together |
| **Cost** | Zero | No database server fees |
| **Performance** | Sub-100ms queries | Even 1000 daily queries = trivial |

---

## Deployment Architecture

### Current (Development)
```
Local machine:
  ├── app/
  ├── quotation.db (SQLite)
  └── run.py (FastAPI + uvicorn)
```

### Production (Railway/Render/VPS)
```
Server:
  ├── /app/                    (Flask/FastAPI code)
  │   ├── routes/
  │   ├── services/
  │   ├── templates/
  │   ├── static/
  │   └── main.py
  ├── quotation.db             (SQLite database file)
  ├── requirements.txt
  ├── seed.py                  (run once on first deploy)
  ├── backup_onedrive.py       (cron: daily backup to OneDrive)
  └── fetch_fx.py              (cron: daily FX rate fetch)
```

---

## Deployment Steps

### 1. **Initial Setup (First Time)**
```bash
# On prod server:
git clone <your-repo>
cd quotation-builder
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Initialize database
python seed.py
# → Creates quotation.db with schema + dummy data

# Start app
python run.py
```

### 2. **Subsequent Deploys**
```bash
# On prod server:
git pull origin main
pip install -r requirements.txt
python run.py
# ← quotation.db already exists, not regenerated
```

### 3. **Backup Strategy**
```bash
# In cron (add to crontab):
0 2 * * * /app/backup_onedrive.py
# Runs daily at 2 AM, copies quotation.db to OneDrive
# Keeps rolling 5-day backup
```

---

## Key SQLite Settings for Production

### 1. **WAL Mode** (Write-Ahead Logging)
```python
# In app initialization (main.py):
conn.execute("PRAGMA journal_mode=WAL")
```
**Why:** Allows concurrent reads while writes are happening. Critical for multi-user.

### 2. **Foreign Keys**
```python
conn.execute("PRAGMA foreign_keys=ON")
```
**Why:** Prevents orphaned records. Required for data integrity.

### 3. **Timeout**
```python
conn.execute("PRAGMA busy_timeout=5000")  # 5 seconds
```
**Why:** If database is locked (another write happening), wait up to 5s instead of failing immediately.

---

## Redeploying with Fresh Database

**Scenario:** You want to reset to fresh seed data.

```bash
# On prod server:
rm quotation.db
rm quotation.db-shm
rm quotation.db-wal
# ↑ Remove all 3 files (WAL mode creates -shm and -wal files)

python seed.py
# → Creates fresh quotation.db with all seed data

python run.py
```

---

## Monitoring in Production

### 1. **Check Database Size**
```bash
ls -lh quotation.db
# Expected: 5-50 MB (grows slowly unless you have millions of quotes)
```

### 2. **Check Database Integrity**
```bash
python -c "
import sqlite3
conn = sqlite3.connect('quotation.db')
result = conn.execute('PRAGMA integrity_check').fetchone()
print(result)  # Should print: ('ok',)
"
```

### 3. **Monitor Backup**
```bash
# Check last backup:
ls -lh backup_onedrive.py logs
# Should have logs showing successful upload
```

---

## Scaling Beyond 5 Concurrent Users

**If you hit 50+ concurrent users:**

| Scenario | What To Do |
|----------|-----------|
| <5 users | Stay with SQLite ← YOU ARE HERE |
| 5-20 users | SQLite with WAL + connection pooling |
| 20-100 users | Migrate to PostgreSQL (still cheap) |
| 100+ users | PostgreSQL + read replicas |

**For S&G Exports:** Scenario 1 is permanent. Marketing doesn't have 50 simultaneous quote builders.

---

## What if quotation.db Gets Corrupted?

### Prevention
```bash
# In seed.py (already added):
PRAGMA integrity_check;  # Database validates on startup
```

### Recovery
```bash
# Restore from backup:
rm quotation.db quotation.db-shm quotation.db-wal
# Download quotation.db from OneDrive (your 5-day rolling backup)
# Restart app
```

---

## File Locations on Different Platforms

### Production (Railway)
```
/app/quotation.db
/app/backup_onedrive.py
```

### Production (Render)
```
/opt/render/project/app/quotation.db
```

### Production (VPS like DigitalOcean)
```
/home/appuser/quotation-builder/quotation.db
```

**Key:** Always use absolute paths or relative paths from app root.

---

## Environment Variables (if needed)

### .env
```
DATABASE_URL=quotation.db  # or /opt/quotation.db if you want it elsewhere
LOG_LEVEL=INFO
```

### Load in main.py
```python
import os
db_path = os.getenv("DATABASE_URL", "quotation.db")
conn = sqlite3.connect(db_path)
```

---

## Cost Breakdown

| Component | Development | Production |
|-----------|------------|-----------|
| Database | Free (SQLite) | Free (SQLite) |
| Server | Local machine | Railway: ₹0–500/mo (free tier available) |
| OneDrive backup | Part of your M365 | Part of your M365 |
| Total | ₹0 | ₹0–500/mo |

---

## TL;DR

1. **Deploy:** `git clone` + `pip install` + `python seed.py` + `python run.py`
2. **Backup:** Cron copies `quotation.db` to OneDrive daily
3. **Redeploy with fresh data:** Delete .db file + `python seed.py`
4. **SQLite never changes** — it goes to prod as-is, stays on server
5. **No separate DB server** = simpler, cheaper, faster

🚀 Ready to deploy!
