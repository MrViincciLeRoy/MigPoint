"""
setup_adsterra.py - Initialize MIG Points with Adsterra integration
Run this script to set up your database with Adsterra-optimized ads
"""

from models import get_db_connection
from config_adsterra import AdsterraConfig

def setup_adsterra_integration():
    """Set up database for Adsterra integration"""
    
    print("\n" + "="*60)
    print("🚀 SETTING UP ADSTERRA INTEGRATION")
    print("="*60 + "\n")
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Step 1: Check if ad_impressions table exists
            print("1. Checking ad_impressions table...")
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'ad_impressions'
            """)
            
            if not cursor.fetchone():
                print("   Creating ad_impressions table...")
                cursor.execute("""
                    CREATE TABLE ad_impressions (
                        id SERIAL PRIMARY KEY,
                        provider VARCHAR(50) NOT NULL,
                        ad_id VARCHAR(255) NOT NULL,
                        user_id INTEGER NOT NULL REFERENCES users(id),
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status VARCHAR(20) DEFAULT 'shown',
                        watch_time INTEGER,
                        completed_at TIMESTAMP
                    )
                """)
                cursor.execute("""
                    CREATE INDEX idx_impressions_user ON ad_impressions(user_id, timestamp)
                """)
                cursor.execute("""
                    CREATE INDEX idx_impressions_provider ON ad_impressions(provider, status)
                """)
                print("   ✓ ad_impressions table created")
            else:
                print("   ✓ ad_impressions table exists")
            
            # Step 2: Update ads table structure
            print("\n2. Updating ads table...")
            
            # Add format column if missing
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='ads' AND column_name='format'
            """)
            if not cursor.fetchone():
                cursor.execute("""
                    ALTER TABLE ads ADD COLUMN format VARCHAR(20) DEFAULT 'native'
                """)
                print("   ✓ Added 'format' column")
            
            # Add click_url column if missing
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='ads' AND column_name='click_url'
            """)
            if not cursor.fetchone():
                cursor.execute("""
                    ALTER TABLE ads ADD COLUMN click_url TEXT
                """)
                print("   ✓ Added 'click_url' column")
            
            # Add impression_url column if missing
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='ads' AND column_name='impression_url'
            """)
            if not cursor.fetchone():
                cursor.execute("""
                    ALTER TABLE ads ADD COLUMN impression_url TEXT
                """)
                print("   ✓ Added 'impression_url' column")
            
            # Step 3: Clear old ads
            print("\n3. Clearing old ads...")
            cursor.execute("DELETE FROM watched_ads")
            print(f"   ✓ Cleared {cursor.rowcount} watched_ads records")
            cursor.execute("DELETE FROM ads")
            print(f"   ✓ Cleared {cursor.rowcount} old ads")
            
            # Step 4: Insert Adsterra-optimized demo ads
            print("\n4. Creating Adsterra-optimized ads...")
            
            # Calculate reward based on eCPM
            base_reward = AdsterraConfig.get_reward_from_ecpm(
                ecpm_usd=1.65,  # Average Adsterra eCPM for SA
                user_share=0.70  # 70% to user, 30% profit
            )
            
            ads = [
                # High-value ads (2.5 MIGP)
                {
                    'title': 'MTN Mega Data Deal',
                    'advertiser': 'MTN South Africa',
                    'description': 'Get 50% more data on all recharges this month!',
                    'image_url': 'https://via.placeholder.com/400x300/0066CC/FFF?text=MTN',
                    'reward': round(base_reward * 1.2, 1),  # 20% above base
                    'duration': 30,
                    'type': 'native',
                    'format': 'native',
                    'provider': 'demo'
                },
                {
                    'title': 'Vodacom LTE Special',
                    'advertiser': 'Vodacom',
                    'description': 'Unlimited streaming with LTE upgrade!',
                    'image_url': 'https://via.placeholder.com/400x300/E60000/FFF?text=Vodacom',
                    'reward': round(base_reward * 1.2, 1),
                    'duration': 30,
                    'type': 'native',
                    'format': 'native',
                    'provider': 'demo'
                },
                
                # Standard ads (2.1 MIGP - base rate)
                {
                    'title': 'Shoprite Fresh Specials',
                    'advertiser': 'Shoprite',
                    'description': 'Fresh produce at unbeatable prices all week!',
                    'image_url': 'https://via.placeholder.com/400x300/00AA00/FFF?text=Shoprite',
                    'reward': base_reward,
                    'duration': 25,
                    'type': 'native',
                    'format': 'native',
                    'provider': 'demo'
                },
                {
                    'title': 'Checkers Sixty60',
                    'advertiser': 'Checkers',
                    'description': 'Groceries delivered to your door in 60 minutes!',
                    'image_url': 'https://via.placeholder.com/400x300/0066FF/FFF?text=Sixty60',
                    'reward': base_reward,
                    'duration': 25,
                    'type': 'native',
                    'format': 'native',
                    'provider': 'demo'
                },
                {
                    'title': 'Pick n Pay Smart Shopper',
                    'advertiser': 'Pick n Pay',
                    'description': 'Earn points on every purchase!',
                    'image_url': 'https://via.placeholder.com/400x300/00B140/FFF?text=Pick+n+Pay',
                    'reward': base_reward,
                    'duration': 20,
                    'type': 'banner',
                    'format': 'banner',
                    'provider': 'demo'
                },
                
                # Quick ads (1.5 MIGP)
                {
                    'title': 'Coca-Cola Refresh',
                    'advertiser': 'Coca-Cola',
                    'description': 'Share a Coke with friends this summer!',
                    'image_url': 'https://via.placeholder.com/400x300/FF0000/FFF?text=Coca+Cola',
                    'reward': round(base_reward * 0.7, 1),
                    'duration': 15,
                    'type': 'banner',
                    'format': 'banner',
                    'provider': 'demo'
                },
                {
                    'title': 'KFC Streetwise',
                    'advertiser': 'KFC',
                    'description': 'Get more for less with Streetwise specials!',
                    'image_url': 'https://via.placeholder.com/400x300/E4002B/FFF?text=KFC',
                    'reward': round(base_reward * 0.7, 1),
                    'duration': 15,
                    'type': 'banner',
                    'format': 'banner',
                    'provider': 'demo'
                }
            ]
            
            for ad in ads:
                cursor.execute("""
                    INSERT INTO ads 
                    (title, advertiser, description, image_url, reward, duration, 
                     type, format, provider)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    ad['title'], ad['advertiser'], ad['description'],
                    ad['image_url'], ad['reward'], ad['duration'],
                    ad['type'], ad['format'], ad['provider']
                ))
                print(f"   ✓ {ad['title']} - {ad['reward']} MIGP ({ad['format']})")
            
            conn.commit()
            
            # Step 5: Show summary
            print("\n" + "="*60)
            print("📊 SETUP SUMMARY")
            print("="*60)
            
            cursor.execute("SELECT COUNT(*) as count FROM ads")
            ad_count = cursor.fetchone()['count']
            print(f"\nTotal ads created: {ad_count}")
            
            cursor.execute("""
                SELECT format, COUNT(*) as count, AVG(reward) as avg_reward
                FROM ads GROUP BY format
            """)
            for row in cursor.fetchall():
                print(f"  {row['format']}: {row['count']} ads, avg {row['avg_reward']:.1f} MIGP")
            
            print("\n" + "="*60)
            print("💰 EARNINGS PROJECTION")
            print("="*60)
            print(f"\nBase reward per ad: {base_reward} MIGP (R{base_reward/10:.2f})")
            print(f"\nDaily (10 ads):")
            print(f"  User earns: {base_reward * 10:.0f} MIGP (R{base_reward:.2f})")
            print(f"  Your revenue: R{base_reward * 10 * 0.3 / 10:.2f}")
            print(f"  Your profit: R{base_reward * 10 * 0.3 / 10 * 0.3:.2f} (30% margin)")
            
            print(f"\nMonthly (22 days, 10 ads/day):")
            print(f"  User earns: {base_reward * 10 * 22:.0f} MIGP (R{base_reward * 10 * 22 / 10:.2f})")
            print(f"  Your revenue: R{base_reward * 10 * 22 * 0.3 / 10:.2f}")
            print(f"  Your profit: R{base_reward * 10 * 22 * 0.3 / 10 * 0.3:.2f}")
            
            print("\n" + "="*60)
            print("✅ ADSTERRA INTEGRATION READY!")
            print("="*60)
            print("\nNext steps:")
            print("  1. Copy .env.example to .env")
            print("  2. Add your Adsterra API key and Publisher ID")
            print("  3. Run: python app.py")
            print("  4. Test with demo ads first")
            print("  5. When ready, set ADSTERRA_ENABLED=True")
            print("="*60 + "\n")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    setup_adsterra_integration()
