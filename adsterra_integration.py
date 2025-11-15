"""
adsterra_provider.py - Adsterra Integration for MIG Points
Integrates Adsterra Social Bar and display ads into the reward system

IMPORTANT: Adsterra doesn't provide a REST API for serving ads.
Instead, you get placement codes from your publisher dashboard.
This implementation uses a hybrid approach:
1. Store Adsterra placement codes in database
2. Serve them through your reward flow
3. Track impressions via postbacks
"""

import requests
import random
from datetime import datetime
from models import get_db, return_db

class AdsterraProvider:
    """
    Adsterra Publisher Integration
    
    Setup Steps:
    1. Sign up at https://adsterra.com as a PUBLISHER
    2. Add your website/domain
    3. Create ad placements (Social Bar, Native, Display)
    4. Copy the placement codes
    5. Add them to your database via setup_adsterra_ads()
    """
    
    def __init__(self):
        self.name = 'adsterra'
        self.enabled = True
        
        # Adsterra typically pays:
        # - Social Bar: $1.50-3.00 CPM
        # - Native: $1.00-2.50 CPM  
        # - Display: $0.80-2.00 CPM
        # South Africa eCPM: ~$1.65 average
        
        self.formats = {
            'social_bar': {
                'name': 'Social Bar',
                'reward_migp': 2.0,  # R0.20 = 2 MIGP
                'description': 'Interactive notification-style ad'
            },
            'native': {
                'name': 'Native Ad',
                'reward_migp': 2.0,  # R0.20 = 2 MIGP
                'description': 'Blends with content'
            },
            'display': {
                'name': 'Display Banner',
                'reward_migp': 1.5,  # R0.15 = 1.5 MIGP
                'description': 'Standard banner ad'
            }
        }
    
    def fetch_ad(self, ad_type='social_bar', duration=30):
        """
        Fetch Adsterra ad placement from database
        
        Args:
            ad_type: 'social_bar', 'native', or 'display'
            duration: Display time in seconds
        
        Returns:
            Ad data dictionary or None
        """
        if not self.enabled:
            print(f"[{self.name}] Not enabled")
            return None
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Get Adsterra placement from database
            cursor.execute("""
                SELECT * FROM ads 
                WHERE provider = 'adsterra' 
                AND ad_type = %s
                ORDER BY RANDOM()
                LIMIT 1
            """, (ad_type,))
            
            ad = cursor.fetchone()
            cursor.close()
            return_db(conn)
            
            if not ad:
                print(f"[{self.name}] No {ad_type} placement found in database")
                return None
            
            # Return ad data
            return {
                'provider': 'adsterra',
                'ad_id': ad['id'],
                'title': ad['title'],
                'advertiser': 'Adsterra Network',
                'description': ad['description'],
                'image_url': ad.get('image_url', 'https://via.placeholder.com/400x300/FF6B35/FFF?text=Adsterra'),
                'reward': ad['reward'],
                'duration': duration,
                'ad_type': ad_type,
                'placement_code': ad.get('placement_code', ''),  # JavaScript code
                'tracking_url': ad.get('tracking_url', '')
            }
            
        except Exception as e:
            print(f"[{self.name}] Error fetching ad: {e}")
            return None
    
    def track_impression(self, ad_id, user_id):
        """Track when ad is shown"""
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ad_impressions 
                (provider, ad_id, user_id, timestamp, status) 
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP, 'shown')
            """, (self.name, ad_id, user_id))
            conn.commit()
            cursor.close()
            return_db(conn)
            print(f"[{self.name}] Tracked impression for ad {ad_id}")
        except Exception as e:
            print(f"[{self.name}] Error tracking impression: {e}")
    
    def track_completion(self, ad_id, user_id, watch_time):
        """Track when ad is completed"""
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE ad_impressions 
                SET status = 'completed', 
                    watch_time = %s, 
                    completed_at = CURRENT_TIMESTAMP
                WHERE provider = %s 
                AND ad_id = %s 
                AND user_id = %s 
                AND status = 'shown'
            """, (watch_time, self.name, ad_id, user_id))
            conn.commit()
            cursor.close()
            return_db(conn)
            print(f"[{self.name}] Tracked completion for ad {ad_id}")
        except Exception as e:
            print(f"[{self.name}] Error tracking completion: {e}")


def setup_adsterra_ads():
    """
    ONE-TIME SETUP: Add Adsterra placements to database
    
    Run this after you:
    1. Sign up at Adsterra as publisher
    2. Add your domain
    3. Create ad placements
    4. Get placement codes
    
    Replace the placeholder codes with YOUR actual codes from Adsterra dashboard
    """
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        print("\n" + "="*60)
        print("🎯 SETTING UP ADSTERRA AD PLACEMENTS")
        print("="*60 + "\n")
        
        # Check if Adsterra ads already exist
        cursor.execute("SELECT COUNT(*) as count FROM ads WHERE provider = 'adsterra'")
        existing = cursor.fetchone()['count']
        
        if existing > 0:
            print(f"⚠️  Found {existing} existing Adsterra ads")
            confirm = input("Delete and recreate? (yes/no): ")
            if confirm.lower() != 'yes':
                print("❌ Cancelled")
                return
            
            cursor.execute("DELETE FROM ads WHERE provider = 'adsterra'")
            print(f"✓ Deleted {cursor.rowcount} old ads")
        
        # Adsterra placements to add
        # Replace these with YOUR actual placement codes from Adsterra dashboard
        adsterra_ads = [
            {
                'title': 'Adsterra Social Bar',
                'advertiser': 'Adsterra Network',
                'description': 'Interactive notification-style advertisement',
                'reward': 2.0,  # 2 MIGP = R0.20
                'duration': 30,
                'ad_type': 'social_bar',
                'provider': 'adsterra',
                'placement_code': '''
                    <!-- Replace with YOUR Social Bar code from Adsterra -->
                    <script type="text/javascript">
                        atOptions = {
                            'key' : 'YOUR_PLACEMENT_KEY_HERE',
                            'format' : 'iframe',
                            'height' : 50,
                            'width' : 320,
                            'params' : {}
                        };
                    </script>
                    <script type="text/javascript" src="//www.topcreativeformat.com/YOUR_ID/invoke.js"></script>
                ''',
                'image_url': 'https://via.placeholder.com/400x300/FF6B35/FFF?text=Adsterra+Social+Bar'
            },
            {
                'title': 'Adsterra Native Ad',
                'advertiser': 'Adsterra Network',
                'description': 'Native advertisement that blends with content',
                'reward': 2.0,  # 2 MIGP = R0.20
                'duration': 30,
                'ad_type': 'native',
                'provider': 'adsterra',
                'placement_code': '''
                    <!-- Replace with YOUR Native Ad code from Adsterra -->
                    <script type="text/javascript">
                        atOptions = {
                            'key' : 'YOUR_PLACEMENT_KEY_HERE',
                            'format' : 'iframe',
                            'height' : 250,
                            'width' : 300,
                            'params' : {}
                        };
                    </script>
                    <script type="text/javascript" src="//www.topcreativeformat.com/YOUR_ID/invoke.js"></script>
                ''',
                'image_url': 'https://via.placeholder.com/400x300/FF6B35/FFF?text=Adsterra+Native'
            },
            {
                'title': 'Adsterra Display Banner',
                'advertiser': 'Adsterra Network',
                'description': 'Standard banner advertisement',
                'reward': 1.5,  # 1.5 MIGP = R0.15
                'duration': 20,
                'ad_type': 'display',
                'provider': 'adsterra',
                'placement_code': '''
                    <!-- Replace with YOUR Banner code from Adsterra -->
                    <script type="text/javascript">
                        atOptions = {
                            'key' : 'YOUR_PLACEMENT_KEY_HERE',
                            'format' : 'iframe',
                            'height' : 90,
                            'width' : 728,
                            'params' : {}
                        };
                    </script>
                    <script type="text/javascript" src="//www.topcreativeformat.com/YOUR_ID/invoke.js"></script>
                ''',
                'image_url': 'https://via.placeholder.com/400x300/FF6B35/FFF?text=Adsterra+Banner'
            }
        ]
        
        # Add placement_code column if it doesn't exist
        try:
            cursor.execute("""
                ALTER TABLE ads 
                ADD COLUMN IF NOT EXISTS placement_code TEXT
            """)
            cursor.execute("""
                ALTER TABLE ads 
                ADD COLUMN IF NOT EXISTS tracking_url TEXT
            """)
            print("✓ Added placement_code and tracking_url columns")
        except:
            print("ℹ️  Columns already exist")
        
        # Insert ads
        for ad in adsterra_ads:
            cursor.execute("""
                INSERT INTO ads 
                (title, advertiser, description, image_url, reward, duration, 
                 type, ad_type, provider, placement_code)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                ad['title'], ad['advertiser'], ad['description'],
                ad['image_url'], ad['reward'], ad['duration'],
                'video', ad['ad_type'], ad['provider'], ad['placement_code']
            ))
            print(f"✓ Added: {ad['title']} ({ad['reward']} MIGP)")
        
        conn.commit()
        
        print("\n" + "="*60)
        print("✅ ADSTERRA SETUP COMPLETE!")
        print("="*60)
        print("\n⚠️  IMPORTANT NEXT STEPS:")
        print("1. Log in to your Adsterra publisher account")
        print("2. Go to 'Websites' → Select your site → 'Add Code'")
        print("3. Create these ad units:")
        print("   - Social Bar")
        print("   - Native Ads")
        print("   - Display Banner (728x90 or 300x250)")
        print("4. Copy each placement code")
        print("5. Update the ads table with YOUR actual codes:")
        print("   UPDATE ads SET placement_code = 'YOUR_CODE' WHERE provider = 'adsterra' AND ad_type = 'social_bar';")
        print("\n💡 TIP: Social Bar works best for rewarded ads!")
        print("="*60 + "\n")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        return_db(conn)


def test_adsterra_integration():
    """Test Adsterra provider"""
    print("\n" + "="*60)
    print("🧪 TESTING ADSTERRA INTEGRATION")
    print("="*60 + "\n")
    
    provider = AdsterraProvider()
    
    # Test fetching each format
    for ad_type in ['social_bar', 'native', 'display']:
        print(f"\nTesting {ad_type}...")
        ad = provider.fetch_ad(ad_type=ad_type, duration=30)
        
        if ad:
            print(f"✓ {ad['title']}")
            print(f"  Reward: {ad['reward']} MIGP")
            print(f"  Duration: {ad['duration']}s")
            print(f"  Has placement code: {'Yes' if ad.get('placement_code') else 'No'}")
        else:
            print(f"✗ No {ad_type} ad found")
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETE")
    print("="*60 + "\n")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'setup':
        setup_adsterra_ads()
    elif len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_adsterra_integration()
    else:
        print("\nUsage:")
        print("  python adsterra_provider.py setup  - Set up Adsterra ads in database")
        print("  python adsterra_provider.py test   - Test Adsterra integration")
