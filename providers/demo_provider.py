"""
demo_provider.py - Demo Ad Provider

Fallback provider with demo ads for testing when real providers are unavailable.
"""

import random
from .base_provider import BaseProvider
from models import get_db_connection


class DemoProvider(BaseProvider):
    """Demo/Fallback ads when real providers are unavailable"""
    
    def __init__(self, enabled=True):
        super().__init__('demo', enabled)
        self.priority = 0  # Lowest priority - fallback only
        self.demo_ads = [
            {
                'provider': 'demo',
                'ad_id': 'demo_mtn_001',
                'creative_url': 'https://via.placeholder.com/800x600/0066CC/FFF?text=MTN+Data',
                'title': 'MTN Mega Data Deal',
                'description': 'Get 50% more data on all recharges this month!',
                'advertiser': 'MTN South Africa',
                'duration': 30,
                'reward': 0.5,
                'format': 'native',
                'image_url': 'https://via.placeholder.com/400x300/0066CC/FFF?text=MTN',
                'is_embed': False
            },
            {
                'provider': 'demo',
                'ad_id': 'demo_shoprite_001',
                'creative_url': 'https://via.placeholder.com/800x600/00AA00/FFF?text=Shoprite',
                'title': 'Shoprite Fresh Specials',
                'description': 'Fresh produce at unbeatable prices all week!',
                'advertiser': 'Shoprite',
                'duration': 20,
                'reward': 0.3,
                'format': 'banner',
                'image_url': 'https://via.placeholder.com/400x300/00AA00/FFF?text=Shoprite',
                'is_embed': False
            },
            {
                'provider': 'demo',
                'ad_id': 'demo_vodacom_001',
                'creative_url': 'https://via.placeholder.com/800x600/E60000/FFF?text=Vodacom',
                'title': 'Vodacom LTE Upgrade',
                'description': 'Unlimited streaming with LTE upgrade!',
                'advertiser': 'Vodacom',
                'duration': 25,
                'reward': 0.4,
                'format': 'native',
                'image_url': 'https://via.placeholder.com/400x300/E60000/FFF?text=Vodacom',
                'is_embed': False
            }
        ]
    
    def fetch_ad(self, ad_format='native', user_country='ZA', view_count=0):
        """Return random demo ad"""
        if not self.enabled:
            return None
        print(f"[{self.name}] Returning demo ad")
        return random.choice(self.demo_ads)
    
    def track_impression(self, ad_id, user_id, impression_url=None):
        """Track demo ad impression"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO ad_impressions 
                    (provider, ad_id, user_id, timestamp, status) 
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP, 'shown')
                ''', (self.name, ad_id, user_id))
                conn.commit()
        except Exception as e:
            print(f"Error tracking impression: {e}")
    
    def track_completion(self, ad_id, user_id, watch_time):
        """Track demo ad completion"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE ad_impressions 
                    SET status = 'completed', 
                        watch_time = %s, 
                        completed_at = CURRENT_TIMESTAMP
                    WHERE provider = %s 
                    AND ad_id = %s 
                    AND user_id = %s 
                    AND status = 'shown'
                ''', (watch_time, self.name, ad_id, user_id))
                conn.commit()
        except Exception as e:
            print(f"Error tracking completion: {e}")
