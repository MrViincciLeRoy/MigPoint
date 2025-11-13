"""
ad_providers.py - Multi-Provider Ad Network Manager
Handles fetching ads from multiple networks with fallback and tracking
"""

import requests
import random
from datetime import datetime
from models import get_db

class AdProvider:
    """Base class for ad providers"""
    def __init__(self, name, api_key=None, enabled=True):
        self.name = name
        self.api_key = api_key
        self.enabled = enabled
    
    def fetch_ad(self, ad_type='video', duration=30):
        """Override this in subclasses"""
        raise NotImplementedError
    
    def track_impression(self, ad_id, user_id):
        """Track when ad is shown"""
        conn = get_db()
        conn.execute('''INSERT INTO ad_impressions 
                       (provider, ad_id, user_id, timestamp, status) 
                       VALUES (?, ?, ?, ?, ?)''',
                    (self.name, ad_id, user_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'shown'))
        conn.commit()
        conn.close()
    
    def track_completion(self, ad_id, user_id, watch_time):
        """Track when ad is completed"""
        conn = get_db()
        conn.execute('''UPDATE ad_impressions 
                       SET status = ?, watch_time = ?, completed_at = ?
                       WHERE provider = ? AND ad_id = ? AND user_id = ? 
                       AND status = 'shown' ''',
                    ('completed', watch_time, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                     self.name, ad_id, user_id))
        conn.commit()
        conn.close()


class GoogleAdMobProvider(AdProvider):
    """Google AdMob integration"""
    def __init__(self, api_key=None):
        super().__init__('admob', api_key)
        self.base_url = 'https://googleads.g.doubleclick.net/mads/gma'
    
    def fetch_ad(self, ad_type='video', duration=30):
        """Fetch ad from AdMob"""
        if not self.enabled or not self.api_key:
            return None
        
        try:
            # Real AdMob API call would go here
            # For now, return structured demo data
            response = requests.get(
                f'{self.base_url}/ads',
                headers={'Authorization': f'Bearer {self.api_key}'},
                params={
                    'ad_format': 'rewarded_video',
                    'duration': duration
                },
                timeout=5
            )
            
            if response.status_code == 200:
                ad_data = response.json()
                return {
                    'provider': 'admob',
                    'ad_id': ad_data.get('ad_id'),
                    'video_url': ad_data.get('video_url'),
                    'title': ad_data.get('title'),
                    'advertiser': ad_data.get('advertiser'),
                    'duration': ad_data.get('duration', duration),
                    'reward': 5,
                    'tracking_url': ad_data.get('tracking_url')
                }
        except Exception as e:
            print(f"AdMob fetch error: {e}")
            return None


class UnityAdsProvider(AdProvider):
    """Unity Ads integration"""
    def __init__(self, game_id=None, api_key=None):
        super().__init__('unity', api_key)
        self.game_id = game_id
        self.base_url = 'https://ads.unity3d.com/v1'
    
    def fetch_ad(self, ad_type='video', duration=30):
        """Fetch ad from Unity"""
        if not self.enabled or not self.game_id:
            return None
        
        try:
            response = requests.post(
                f'{self.base_url}/games/{self.game_id}/ads',
                headers={'Authorization': f'Bearer {self.api_key}'},
                json={
                    'placement': 'rewardedVideo',
                    'platform': 'android'
                },
                timeout=5
            )
            
            if response.status_code == 200:
                ad_data = response.json()
                return {
                    'provider': 'unity',
                    'ad_id': ad_data.get('id'),
                    'video_url': ad_data.get('video_url'),
                    'title': ad_data.get('creative_name'),
                    'advertiser': 'Unity Network',
                    'duration': ad_data.get('duration', duration),
                    'reward': 5,
                    'tracking_url': ad_data.get('tracking_url')
                }
        except Exception as e:
            print(f"Unity Ads fetch error: {e}")
            return None


class FacebookAudienceNetworkProvider(AdProvider):
    """Facebook Audience Network integration"""
    def __init__(self, placement_id=None, api_key=None):
        super().__init__('facebook', api_key)
        self.placement_id = placement_id
        self.base_url = 'https://graph.facebook.com/v18.0'
    
    def fetch_ad(self, ad_type='video', duration=30):
        """Fetch ad from Facebook"""
        if not self.enabled or not self.placement_id:
            return None
        
        try:
            response = requests.get(
                f'{self.base_url}/{self.placement_id}/ads',
                headers={'Authorization': f'Bearer {self.api_key}'},
                params={'format': 'rewarded_video'},
                timeout=5
            )
            
            if response.status_code == 200:
                ad_data = response.json()
                return {
                    'provider': 'facebook',
                    'ad_id': ad_data.get('id'),
                    'video_url': ad_data.get('video_url'),
                    'title': ad_data.get('title'),
                    'advertiser': ad_data.get('advertiser_name'),
                    'duration': ad_data.get('duration', duration),
                    'reward': 5,
                    'tracking_url': ad_data.get('impression_url')
                }
        except Exception as e:
            print(f"Facebook Ads fetch error: {e}")
            return None


class SmaatoProvider(AdProvider):
    """Smaato (African markets)"""
    def __init__(self, publisher_id=None, api_key=None):
        super().__init__('smaato', api_key)
        self.publisher_id = publisher_id
        self.base_url = 'https://soma.smaato.net/oapi'
    
    def fetch_ad(self, ad_type='video', duration=30):
        """Fetch ad from Smaato"""
        if not self.enabled or not self.publisher_id:
            return None
        
        try:
            response = requests.post(
                f'{self.base_url}/ad',
                headers={
                    'Content-Type': 'application/json',
                    'X-SMT-PUB-ID': self.publisher_id
                },
                json={
                    'adSpaceId': self.api_key,
                    'format': 'video'
                },
                timeout=5
            )
            
            if response.status_code == 200:
                ad_data = response.json()
                return {
                    'provider': 'smaato',
                    'ad_id': ad_data.get('adId'),
                    'video_url': ad_data.get('videoUrl'),
                    'title': 'Sponsored Content',
                    'advertiser': ad_data.get('advertiser', 'Smaato Network'),
                    'duration': ad_data.get('duration', duration),
                    'reward': 5,
                    'tracking_url': ad_data.get('impressionUrl')
                }
        except Exception as e:
            print(f"Smaato fetch error: {e}")
            return None


class DemoAdProvider(AdProvider):
    """Demo/Fallback ads when no real ads available"""
    def __init__(self):
        super().__init__('demo', enabled=True)
        self.demo_ads = [
            {
                'provider': 'demo',
                'ad_id': 'demo_1',
                'video_url': 'https://via.placeholder.com/400x300/0066CC/FFF?text=MTN',
                'title': 'MTN Mega Deal',
                'advertiser': 'MTN',
                'description': 'Get 50% more data with MTN!',
                'duration': 30,
                'reward': 5,
                'image_url': 'https://via.placeholder.com/400x300/0066CC/FFF?text=MTN'
            },
            {
                'provider': 'demo',
                'ad_id': 'demo_2',
                'video_url': 'https://via.placeholder.com/400x300/00AA00/FFF?text=Shoprite',
                'title': 'Shoprite Fresh Specials',
                'advertiser': 'Shoprite',
                'description': 'Fresh produce at unbeatable prices!',
                'duration': 15,
                'reward': 5,
                'image_url': 'https://via.placeholder.com/400x300/00AA00/FFF?text=Shoprite'
            },
            {
                'provider': 'demo',
                'ad_id': 'demo_3',
                'video_url': 'https://via.placeholder.com/400x300/000/FFF?text=Nike',
                'title': 'Nike Back to School',
                'advertiser': 'Nike',
                'description': 'New gear for the new term!',
                'duration': 45,
                'reward': 10,
                'image_url': 'https://via.placeholder.com/400x300/000/FFF?text=Nike'
            }
        ]
    
    def fetch_ad(self, ad_type='video', duration=30):
        """Return random demo ad"""
        return random.choice(self.demo_ads)


class AdManager:
    """Manages multiple ad providers with fallback and tracking"""
    def __init__(self):
        # Initialize all providers (set enabled=False until you have API keys)
        self.providers = [
            GoogleAdMobProvider(api_key=None),  # Add your API key when ready
            UnityAdsProvider(game_id=None, api_key=None),
            FacebookAudienceNetworkProvider(placement_id=None, api_key=None),
            SmaatoProvider(publisher_id=None, api_key=None),
            DemoAdProvider()  # Always enabled as fallback
        ]
        
        # Provider priority (higher number = higher priority)
        self.provider_priority = {
            'admob': 5,      # Highest CPM usually
            'unity': 4,
            'facebook': 3,
            'smaato': 2,
            'demo': 1        # Lowest priority, fallback only
        }
    
    def get_ad(self, ad_type='video', duration=30, user_id=None):
        """
        Fetch ad from providers in priority order with fallback
        Returns ad data or None
        """
        # Sort providers by priority
        sorted_providers = sorted(
            [p for p in self.providers if p.enabled],
            key=lambda p: self.provider_priority.get(p.name, 0),
            reverse=True
        )
        
        # Try each provider
        for provider in sorted_providers:
            print(f"Trying provider: {provider.name}")
            ad_data = provider.fetch_ad(ad_type, duration)
            
            if ad_data:
                print(f"✓ Ad fetched from {provider.name}")
                
                # Track impression
                if user_id:
                    provider.track_impression(ad_data['ad_id'], user_id)
                
                # Add provider info for tracking
                ad_data['provider_name'] = provider.name
                return ad_data
        
        print("✗ No ads available from any provider")
        return None
    
    def complete_ad(self, provider_name, ad_id, user_id, watch_time):
        """Mark ad as completed and track"""
        provider = next((p for p in self.providers if p.name == provider_name), None)
        if provider:
            provider.track_completion(ad_id, user_id, watch_time)
            
            # Update provider stats
            self.update_provider_stats(provider_name, completed=True)
    
    def update_provider_stats(self, provider_name, completed=False):
        """Update provider performance stats"""
        conn = get_db()
        
        # Check if stats exist
        stats = conn.execute(
            'SELECT * FROM provider_stats WHERE provider = ?',
            (provider_name,)
        ).fetchone()
        
        if stats:
            if completed:
                conn.execute('''UPDATE provider_stats 
                               SET completions = completions + 1,
                                   last_served = ?
                               WHERE provider = ?''',
                           (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), provider_name))
            else:
                conn.execute('''UPDATE provider_stats 
                               SET impressions = impressions + 1,
                                   last_served = ?
                               WHERE provider = ?''',
                           (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), provider_name))
        else:
            conn.execute('''INSERT INTO provider_stats 
                           (provider, impressions, completions, last_served) 
                           VALUES (?, ?, ?, ?)''',
                        (provider_name, 1, 1 if completed else 0,
                         datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        conn.commit()
        conn.close()
    
    def get_provider_stats(self):
        """Get performance stats for all providers"""
        conn = get_db()
        stats = conn.execute('''SELECT provider, impressions, completions, 
                                       last_served,
                                       ROUND(CAST(completions AS FLOAT) / 
                                       NULLIF(impressions, 0) * 100, 2) as completion_rate
                               FROM provider_stats 
                               ORDER BY impressions DESC''').fetchall()
        conn.close()
        return stats
    
    def enable_provider(self, provider_name):
        """Enable a specific provider"""
        provider = next((p for p in self.providers if p.name == provider_name), None)
        if provider:
            provider.enabled = True
            print(f"✓ {provider_name} enabled")
    
    def disable_provider(self, provider_name):
        """Disable a specific provider"""
        provider = next((p for p in self.providers if p.name == provider_name), None)
        if provider and provider.name != 'demo':  # Can't disable demo
            provider.enabled = False
            print(f"✗ {provider_name} disabled")


# Global ad manager instance
ad_manager = AdManager()