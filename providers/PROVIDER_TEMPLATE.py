"""
PROVIDER_TEMPLATE.py - Template for adding new ad providers

Copy this template and customize for each new provider you want to add.
"""

from .base_provider import BaseProvider
from models import get_db_connection


class PROVIDER_TEMPLATEProvider(BaseProvider):
    """
    PROVIDER_TEMPLATE Ad Provider
    
    Replace PROVIDER_TEMPLATE with your provider name (e.g., PropellerAds, AdMaven, etc.)
    
    Setup Instructions:
    1. Sign up at [provider website]
    2. Create an account and get API keys/Publisher ID
    3. Create ad units and get the embed codes/script IDs
    4. Fill in the configuration below
    5. Implement fetch_ad() to return ad data
    6. Update provider_manager.py to import this provider
    7. Add to app.py initialization
    """
    
    def __init__(self, enabled=True, publisher_id=None, api_key=None):
        super().__init__('provider_name', enabled)  # Change 'provider_name'
        self.priority = 4  # Set priority (5=highest, 0=lowest)
        self.publisher_id = publisher_id
        self.api_key = api_key
        
        # Provider configuration
        self.base_ecpm = 1.65  # Expected CPM in USD
        self.timeout = 5
        
        print(f"\n[{self.name}] Initialized")
        print(f"  Enabled: {self.enabled}")
        print(f"  Expected CPM: ${self.base_ecpm}")
    
    def fetch_ad(self, ad_format='native', user_country='ZA', view_count=0):
        """
        Fetch an ad from this provider
        
        Implement your provider's API call here.
        Return dict with ad data or None if unavailable.
        """
        if not self.enabled:
            print(f"[{self.name}] Not enabled")
            return None
        
        try:
            # TODO: Implement API call to fetch ad
            # Example:
            # response = requests.get(
            #     f'https://api.provider.com/ads',
            #     params={'publisher_id': self.publisher_id, 'country': user_country},
            #     timeout=self.timeout
            # )
            # ad_data = response.json()
            
            # Return ad in standard format
            return {
                'provider': self.name,
                'ad_id': 'provider_ad_id',  # Unique ad ID
                'title': 'Ad Title',
                'description': 'Ad Description',
                'advertiser': 'Advertiser Name',
                'duration': 30,
                'reward': 0.5,  # MIGP reward based on CPM
                'format': ad_format,
                'image_url': 'https://example.com/ad.jpg',
                'is_embed': False,  # True if requires script embed
                'ecpm': self.base_ecpm
            }
        
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            return None
    
    def track_impression(self, ad_id, user_id, impression_url=None):
        """Track when an ad is shown"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO ad_impressions 
                    (provider, ad_id, user_id, timestamp, status) 
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP, 'shown')
                ''', (self.name, ad_id, user_id))
                conn.commit()
            
            # Optional: Fire impression tracking pixel
            if impression_url:
                try:
                    import requests
                    requests.get(impression_url, timeout=2)
                except:
                    pass
        
        except Exception as e:
            print(f"Error tracking impression: {e}")
    
    def track_completion(self, ad_id, user_id, watch_time):
        """Track when an ad is completed"""
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
