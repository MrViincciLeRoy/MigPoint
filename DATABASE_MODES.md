# Database Configuration Guide

## Overview
This application now supports **two database modes**:
- **Online Mode** (default): Uses PostgreSQL via Aiven for production
- **Offline Mode**: Uses local SQLite for development/testing without internet

## Quick Start

### Online Mode (Default - PostgreSQL)
```bash
# In .env file:
DB_MODE=online

# Then run the app normally:
python app.py
```

The app will connect to your Aiven PostgreSQL database.

### Offline Mode (SQLite)
```bash
# First time: Create the offline database
python create_offline_db.py

# In .env file:
DB_MODE=offline

# Then run the app:
python app.py
```

The app will use the local `offline_data.db` SQLite database.

## File Structure

```
├── create_offline_db.py      # Script to generate offline database
├── offline_data.db           # SQLite offline database (created after running script)
├── .env                      # Configuration file with DB_MODE setting
├── models.py                 # Database abstraction layer (auto-switches based on DB_MODE)
└── app.py                    # Flask app (uses model auto-detection)
```

## Database Details

### Online Mode Configuration (.env)
```env
DB_MODE=online
AIVEN_HOST=pg-55db8a5-semblence1317-b92d.f.aivencloud.com
AIVEN_PORT=12120
AIVEN_DB=defaultdb
AIVEN_USER=avnadmin
AIVEN_PASSWORD=AVNS_8ofE0CJ0sHFlKwQrMXR
```

### Offline Mode Configuration (.env)
```env
DB_MODE=offline
OFFLINE_DB_PATH=offline_data.db
```

## Demo Users (Available in Both Modes)

| Phone | Password | Role | Balance |
|-------|----------|------|---------|
| 0821234567 | demo123 | Admin | 1250 MIGP |
| 0829876543 | - | User | 450 MIGP |
| 0834567890 | - | User | 280 MIGP |

All demo users use password: `demo123`

## Schema

Both databases use the same schema:

```sql
-- Users table
users (id, phone, password_hash, name, is_admin, balance, created_at)

-- Transactions table  
transactions (id, user_id, type, amount, description, timestamp)

-- Ads table
ads (id, title, advertiser, description, image_url, reward, duration, type, ad_type, provider)

-- Watched ads table
watched_ads (id, user_id, ad_id, timestamp)

-- Ad impressions table
ad_impressions (id, provider, ad_id, user_id, timestamp, status, watch_time, completed_at)
```

## How It Works

### models.py Auto-Detection
```python
DB_MODE = os.getenv('DB_MODE', 'online').lower()

if DB_MODE == 'offline':
    USE_SQLITE = True          # Use sqlite3
    # Load offline_data.db
else:
    USE_SQLITE = False         # Use psycopg2 (PostgreSQL)
    # Use Aiven connection
```

### Unified Interface
All database calls remain the same regardless of mode:

```python
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    # Works in BOTH online and offline modes!
```

## Switching Modes

1. **Edit `.env`**:
   ```bash
   DB_MODE=offline  # Change from 'online' to 'offline' or vice versa
   ```

2. **Restart the app**:
   ```bash
   # Ctrl+C to stop current app
   python app.py  # Start app (will auto-detect mode and switch databases)
   ```

## Important Notes

⚠️ **Data Isolation**: 
- Online and Offline databases are completely separate
- Changes in one mode don't affect the other
- Plan your testing accordingly!

⚠️ **Offline Database Creation**:
- Run `python create_offline_db.py` BEFORE setting `DB_MODE=offline`
- This creates `offline_data.db` with demo data
- The script only needs to run once

✅ **Connection Pooling**:
- PostgreSQL: Uses ThreadedConnectionPool (2-20 connections)
- SQLite: Direct connections (thread-safe)
- No manual connection management needed!

## Troubleshooting

### "Offline database not found: offline_data.db"
```bash
# Solution: Create the database first
python create_offline_db.py

# Then set DB_MODE=offline in .env
```

### "Missing database configuration!"
```bash
# Solution: Make sure DB_MODE=online has Aiven credentials in .env
# Check:
# - AIVEN_HOST
# - AIVEN_PORT
# - AIVEN_DB
# - AIVEN_USER
# - AIVEN_PASSWORD
```

### "Database error: ..."
- Check that the .env file has the correct DB_MODE
- Verify PostgreSQL credentials if using online mode
- Verify offline_data.db exists if using offline mode
- Check console output for mode confirmation (looks for 🔄, 📁, or 🗄️ emoji)

## Production Considerations

| Aspect | Online | Offline |
|--------|--------|---------|
| **Best for** | Production | Development/Testing |
| **Data persistence** | Remote server | Local file |
| **Performance** | Network-dependent | Very fast |
| **Multi-user** | Yes | Single-machine only |
| **Backup** | Aiven managed | Manual (.db file) |
| **Data sync** | Live | None (separate) |

## Advanced: Syncing Data Between Modes

To export data from online to offline (manual sync):
```python
# This would require a custom sync script
# Not implemented yet - let us know if you need it!
```

To import offline data to online:
```python
# Also requires custom implementation
# Please request if needed
```
