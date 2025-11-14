"""
reset_ads.py - Safely reset ads by removing foreign key constraints first
"""

from models import get_db, return_db

def reset_ads():
    """Reset ads by cleaning up watched_ads first"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        print("\n" + "="*60)
        print("🔧 RESETTING ADS DATABASE")
        print("="*60 + "\n")
        
        # Step 1: Check current state
        cursor.execute("SELECT COUNT(*) as count FROM watched_ads")
        watched_count = cursor.fetchone()['count']
        print(f"📊 Current watched_ads records: {watched_count}")
        
        cursor.execute("SELECT COUNT(*) as count FROM ads")
        ads_count = cursor.fetchone()['count']
        print(f"📊 Current ads records: {ads_count}")
        
        # Step 2: Delete watched_ads first (removes foreign key references)
        print("\n⚠️  This will delete ALL watched ad history!")
        confirm = input("Continue? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("❌ Cancelled")
            return
        
        print("\n1. Deleting watched_ads records...")
        cursor.execute("DELETE FROM watched_ads")
        print(f"   ✓ Deleted {cursor.rowcount} records")
        
        # Step 3: Now we can safely delete ads
        print("\n2. Deleting old ads...")
        cursor.execute("DELETE FROM ads")
        print(f"   ✓ Deleted {cursor.rowcount} ads")
        
        # Step 3.5: Add ad_type column if it doesn't exist
        print("\n3. Checking for ad_type column...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='ads' AND column_name='ad_type'
        """)
        
        if not cursor.fetchone():
            print("   Adding ad_type column...")
            cursor.execute("""
                ALTER TABLE ads 
                ADD COLUMN ad_type VARCHAR(20) DEFAULT 'demo'
            """)
            print("   ✓ ad_type column added")
        else:
            print("   ✓ ad_type column already exists")
        
        # Step 4: Insert new ads with proper tier system
        print("\n4. Inserting new tiered ads...")
        
        new_ads = [
            # PREMIUM TIER (10 MIGP)
            ('MTN Mega Data Deal', 'MTN South Africa', 
             'Get 50% more data on all recharges!', 
             'https://via.placeholder.com/400x300/0066CC/FFF?text=MTN', 
             10, 30, 'premium'),
            
            ('Vodacom LTE Special', 'Vodacom', 
             'Unlimited streaming with LTE upgrade!', 
             'https://via.placeholder.com/400x300/E60000/FFF?text=Vodacom', 
             10, 30, 'premium'),
            
            # HIGH TIER (7 MIGP)
            ('Nike Back to School', 'Nike', 
             'New gear for the new school year!', 
             'https://via.placeholder.com/400x300/000/FFF?text=Nike', 
             7, 25, 'high_tier'),
            
            ('Shoprite Mega Sale', 'Shoprite', 
             'Unbeatable prices on fresh produce!', 
             'https://via.placeholder.com/400x300/00AA00/FFF?text=Shoprite', 
             7, 20, 'high_tier'),
            
            # MID TIER (5 MIGP)
            ('Checkers Specials', 'Checkers', 
             'Weekly specials you can\'t miss!', 
             'https://via.placeholder.com/400x300/0066FF/FFF?text=Checkers', 
             5, 20, 'mid_tier'),
            
            ('Nandos Combo Deal', 'Nandos', 
             'Flame-grilled perfection at great prices!', 
             'https://via.placeholder.com/400x300/FF0000/FFF?text=Nandos', 
             5, 15, 'mid_tier'),
            
            # LOW TIER (3 MIGP)
            ('Coca-Cola Refresh', 'Coca-Cola', 
             'Share a Coke with friends!', 
             'https://via.placeholder.com/400x300/FF0000/FFF?text=Coca+Cola', 
             3, 15, 'low_tier'),
            
            ('Pick n Pay Essentials', 'Pick n Pay', 
             'Daily essentials at low prices!', 
             'https://via.placeholder.com/400x300/00B140/FFF?text=Pick+n+Pay', 
             3, 10, 'low_tier'),
        ]
        
        for ad in new_ads:
            cursor.execute("""
                INSERT INTO ads (title, advertiser, description, image_url, reward, duration, ad_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, ad)
        
        print(f"   ✓ Inserted {len(new_ads)} new ads")
        
        # Commit all changes
        conn.commit()
        
        # Verify
        cursor.execute("SELECT id, title, reward, ad_type FROM ads ORDER BY reward DESC")
        ads = cursor.fetchall()
        
        print("\n4. New ads created:")
        print("   " + "-"*56)
        for ad in ads:
            print(f"   ID {ad['id']:2d} | {ad['title']:30s} | {ad['reward']}pts | {ad['ad_type']}")
        print("   " + "-"*56)
        
        print("\n" + "="*60)
        print("✅ ADS RESET COMPLETE!")
        print("="*60 + "\n")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        cursor.close()
        return_db(conn)

if __name__ == '__main__':
    reset_ads()
