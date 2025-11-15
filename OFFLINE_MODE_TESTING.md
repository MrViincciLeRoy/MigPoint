# SQLite Offline Mode - Testing Checklist

## ✅ All Fixes Applied

### 1. Query Parameter Conversion
- ✅ `convert_query()` helper function added to models.py
- ✅ All SQL queries wrapped with `convert_query()`
- ✅ Blueprint files: main.py (11 queries), auth.py, wallet.py

### 2. Row Data Access
- ✅ `safe_row_access()` helper function added to models.py
- ✅ All dictionary accesses (`row['key']`) updated to use helper
- ✅ User model methods updated (get, create, verify_password)
- ✅ Blueprint functions updated (dashboard, watch_ad, complete_ad, etc.)

### 3. Imports Updated
- ✅ main.py imports convert_query and safe_row_access
- ✅ auth.py imports convert_query and safe_row_access
- ✅ wallet.py imports convert_query and safe_row_access

## 📋 Testing Steps

### Test 1: Offline Mode - Login Flow
```bash
# 1. Set DB_MODE=offline in .env
# 2. Run: python app.py
# 3. Navigate to login page
# 4. Try demo login with: Phone=0821234567, Password=demo123
# Expected: Login succeeds, shows dashboard
```

### Test 2: Offline Mode - Watch Ad Flow
```bash
# 1. After login, click on an ad
# 2. Wait for loading timer
# 3. After 30 seconds, complete ad
# Expected: MIGP balance increases, no errors in console
```

### Test 3: Offline Mode - Wallet
```bash
# 1. Go to Wallet section
# 2. Try to convert MIGP to airtime or data
# Expected: Transaction completes, balance decreases
```

### Test 4: Online Mode - Verify Still Works
```bash
# 1. Set DB_MODE=online in .env
# 2. Run: python app.py
# 3. Repeat tests 1-3
# Expected: All functionality works with PostgreSQL
```

### Test 5: Mode Switch - Offline to Online
```bash
# 1. In offline mode, create a transaction
# 2. Change DB_MODE=online
# 3. Restart app
# 4. Login with online user
# Expected: Original data still there, new data doesn't cross databases
```

## 🐛 Known Limitations - SQLite

| Feature | PostgreSQL | SQLite |
|---------|-----------|--------|
| `RETURNING` clause | ✅ Full support | ⚠️ Works but limited |
| `EXTRACT()` function | ✅ Works | ❌ May not work |
| Complex date math | ✅ Works | ⚠️ Use simpler queries |
| Connection pooling | ✅ Optimized | ❌ Not needed (auto) |

**Note**: Current queries are designed to work on both databases

## 🔍 Files to Monitor for Errors

If you see errors, check these files:
1. `models.py` - Database initialization and connection
2. `blueprints/main.py` - Ad watching logic
3. `blueprints/auth.py` - Login/registration
4. `blueprints/wallet.py` - Conversion transactions

## ✨ Error Messages to Look For

If something is still broken, you might see:
- `sqlite3.OperationalError: near "%": syntax error` → Need more convert_query() calls
- `TypeError: 'sqlite3.Row' object is not subscriptable` → Need safe_row_access() calls
- `sqlite3.OperationalError: no such table` → offline_data.db not created
- `KeyError: 'column_name'` → Row access issue, use safe_row_access()

## 🎯 Success Indicators

You'll know it's working when:
1. ✅ Login succeeds without errors
2. ✅ Dashboard loads with ads
3. ✅ Balance updates after completing ads
4. ✅ No SQL errors in console
5. ✅ Can switch between online/offline without rebuilding

---

**Status**: All code fixes complete, ready for testing!
