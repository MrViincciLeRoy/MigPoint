"""
fix_cooldown.py - Debug and fix the cooldown system
"""

from models import get_db, return_db
from datetime import datetime, timedelta

def check_cooldown_system():
    """Check if cooldown system is working"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        print("\n" + "="*60)
        print("🔧 CHECKING COOLDOWN SYSTEM")
        print("="*60 + "\n")
        
        # Step 1: Check watched_ads table structure
        print("1. Checking watched_ads table structure...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name='watched_ads'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        print("   Columns:")
        for col in columns:
            print(f"   - {col['column_name']:15} | {col['data_type']:20} | Default: {col['column_default']}")
        
        # Step 2: Check if timestamp column exists and has default
        has_timestamp = any(col['column_name'] == 'timestamp' for col in columns)
        
        if not has_timestamp:
            print("\n   ❌ ERROR: 'timestamp' column is missing!")
            print("   Adding timestamp column...")
            cursor.execute("""
                ALTER TABLE watched_ads 
                ADD COLUMN timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
            conn.commit()
            print("   ✓ Timestamp column added")
        else:
            print("   ✓ Timestamp column exists")
        
        # Step 3: Check recent watched ads
        print("\n2. Checking recent watched_ads records...")
        cursor.execute("""
            SELECT w.id, w.user_id, w.ad_id, w.timestamp,
                   u.name as user_name,
                   a.title as ad_title,
                   EXTRACT(EPOCH FROM (NOW() - w.timestamp))/60 as minutes_ago
            FROM watched_ads w
            JOIN users u ON w.user_id = u.id
            JOIN ads a ON w.ad_id = a.id
            ORDER BY w.timestamp DESC
            LIMIT 10
        """)
        recent = cursor.fetchall()
        
        if recent:
            print("   Recent watches:")
            print("   " + "-"*80)
            for r in recent:
                minutes = r['minutes_ago']
                time_str = f"{int(minutes)}m ago" if minutes else "just now"
                cooldown_status = "✓ Available" if minutes >= 5 else f"⏳ Cooldown ({5-int(minutes)}m left)"
                print(f"   {r['user_name']:15} | {r['ad_title']:25} | {time_str:15} | {cooldown_status}")
            print("   " + "-"*80)
        else:
            print("   No watched ads yet")
        
        # Step 4: Test cooldown query
        print("\n3. Testing cooldown detection query...")
        five_minutes_ago = (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
        print(f"   Five minutes ago: {five_minutes_ago}")
        
        cursor.execute("""
            SELECT user_id, ad_id, timestamp
            FROM watched_ads 
            WHERE timestamp > %s
        """, (five_minutes_ago,))
        on_cooldown = cursor.fetchall()
        
        if on_cooldown:
            print(f"   Found {len(on_cooldown)} ads on cooldown:")
            for item in on_cooldown:
                print(f"   - User {item['user_id']} / Ad {item['ad_id']} at {item['timestamp']}")
        else:
            print("   No ads currently on cooldown")
        
        # Step 5: Check if timestamps are being set
        print("\n4. Checking if new records get timestamps...")
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM watched_ads 
            WHERE timestamp IS NULL
        """)
        null_timestamps = cursor.fetchone()['count']
        
        if null_timestamps > 0:
            print(f"   ❌ WARNING: {null_timestamps} records have NULL timestamps!")
            print("   Fixing NULL timestamps...")
            cursor.execute("""
                UPDATE watched_ads 
                SET timestamp = CURRENT_TIMESTAMP 
                WHERE timestamp IS NULL
            """)
            conn.commit()
            print(f"   ✓ Fixed {cursor.rowcount} records")
        else:
            print("   ✓ All records have timestamps")
        
        print("\n" + "="*60)
        print("✅ COOLDOWN SYSTEM CHECK COMPLETE")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        return_db(conn)


def test_cooldown_for_user(user_id=1):
    """Test cooldown detection for a specific user"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        print("\n" + "="*60)
        print(f"🧪 TESTING COOLDOWN FOR USER {user_id}")
        print("="*60 + "\n")
        
        five_minutes_ago = (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Get all ads
        cursor.execute('SELECT id, title, reward FROM ads')
        all_ads = cursor.fetchall()
        
        # Get ads on cooldown
        cursor.execute("""
            SELECT ad_id, timestamp,
                   EXTRACT(EPOCH FROM (NOW() - timestamp))/60 as minutes_ago
            FROM watched_ads 
            WHERE user_id = %s AND timestamp > %s
        """, (user_id, five_minutes_ago))
        cooldown_ads = {row['ad_id']: row for row in cursor.fetchall()}
        
        print("Ad Status:")
        print("-"*70)
        for ad in all_ads:
            if ad['id'] in cooldown_ads:
                minutes_ago = cooldown_ads[ad['id']]['minutes_ago']
                remaining = 5 - int(minutes_ago)
                print(f"⏳ {ad['title']:30} | Cooldown: {remaining}m remaining")
            else:
                print(f"✅ {ad['title']:30} | Available now!")
        print("-"*70)
        
    finally:
        cursor.close()
        return_db(conn)


if __name__ == '__main__':
    check_cooldown_system()
    print("\nTesting for user 1...")
    test_cooldown_for_user(1)
