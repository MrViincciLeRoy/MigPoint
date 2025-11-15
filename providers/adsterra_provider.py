"""
adsterra_provider.py - Adsterra Integration with Multi-Unit Rotation
Implements Adsterra's 5 ad formats with smart CPM optimization
"""

import requests
import random
from datetime import datetime
from models import get_db_connection
from config_adsterra import AdsterraConfig
import os

class AdsterraProvider:
    """
    Adsterra Ad Provider - Multi-Unit Smart Rotation
    
    Supports 5 ad formats:
    1. Popunder ($0.05-0.15) - High CPM, show every 5 ads
    2. Smartlink ($0.02-0.08) - Medium-high CPM, show every 3 ads
    3. Native Banner ($0.003) - Low CPM, fallback/default
    4. Banner 728x90 ($0.002-0.005) - Low CPM, alternative
    5. Social Bar ($0.01-0.03) - Medium CPM, passive widget
    """
    
    # Ad unit configurations
    AD_UNITS = {
        'popunder': {
            'id': '27951368',
            'script_id': '0e95d61a022fea5177f5dce50bc90756',
            'name': 'Popunder',
            'ecpm': 0.10,  # Average of $0.05-0.15
            'priority': 3,  # Highest priority
            'frequency': 5,  # Show every 5 ads
            'embed_url': '//pl28051867.effectivegatecpm.com'
        },
        'native_banner': {
            'id': '27950195',
            'script_id': 'efeb8c7d77558041c397af667df46f35',
            'name': 'Native Banner',
            'ecpm': 0.005,  # Increased from 0.003 (more reliable fallback)
            'priority': 1,  # Medium priority (fallback)
            'frequency': 1,  # Default
            'embed_url': '//pl28050694.effectivegatecpm.com'
        },
        'banner_728x90': {
            'id': '27951329',
            'script_id': 'ea94e189bad2ba9142b47502f4c99bba',
            'name': 'Banner 728x90',
            'ecpm': 0.003,
            'priority': 0,  # Lowest priority
            'frequency': 10,  # Rarely show
            'embed_url': '//www.highperformanceformat.com'
        }
    }
    
    def __init__(self, enabled=True):
        self.name = 'adsterra'
        self.enabled = enabled
        self.timeout = 5
        import time
        self._base_time = int(time.time() * 1000)  # milliseconds for variety
        self._call_count = 0
        
    def _get_next_unit(self):
        """
        Select ad unit based on time + call count for guaranteed variety
        
        Rotation strategy:
        - Popunder (30%): unit 0
        - Banner 728x90 (20%): unit 1
        - Native Banner (50%): unit 2
        """
        import random
        import time
        
        # Use combination of time and call count to ensure variety
        self._call_count += 1
        current_time_ms = int(time.time() * 1000)
        time_variance = (current_time_ms - self._base_time) % 100
        
        # Create a seed that changes frequently and between calls
        combined_seed = (time_variance + self._call_count * 17) % 100
        
        print(f"[{self.name}] Seed: {combined_seed} (time_var: {time_variance}, call: {self._call_count})")
        
        if combined_seed < 30:
            # 30%: Popunder
            unit = self.AD_UNITS.get('popunder')
            if unit:
                print(f"[{self.name}] -> Selected: Popunder")
                return unit
        elif combined_seed < 50:
            # 20%: Banner 728x90
            unit = self.AD_UNITS.get('banner_728x90')
            if unit:
                print(f"[{self.name}] -> Selected: Banner 728x90")
                return unit
        
        # 50%: Native Banner
        unit = self.AD_UNITS.get('native_banner')
        print(f"[{self.name}] -> Selected: Native Banner")
        return unit
        
    def fetch_ad(self, ad_format='native', user_country='ZA', view_count=0):
        """
        Return rotating Adsterra ad with smart CPM optimization
        
        Args:
            ad_format: preferred format (ignored - uses smart rotation)
            user_country: ISO country code (ZA = South Africa)
            view_count: user's current ad view count (for rotation)
        
        Returns:
            Ad data dict with embed code or None
        """
        if not self.enabled:
            print(f"[{self.name}] Not enabled")
            return None
        
        try:
            # Get next unit based on smart rotation
            unit = self._get_next_unit()
            if not unit:
                print(f"[{self.name}] No valid unit available")
                return None
            
            # Calculate reward based on this unit's eCPM
            reward_amount = AdsterraConfig.get_reward_from_ecpm(
                ecpm_usd=unit['ecpm'],
                user_share=0.7,
                min_reward=0.1
            )
            
            # Format the embed based on unit type
            if unit['name'] == 'Popunder':
                # Popunder: https://pl28051867.effectivegatecpm.com/0e/95/d6/0e95d61a022fea5177f5dce50bc90756.js
                embed_script = f'<script type="text/javascript" src="//pl28051867.effectivegatecpm.com/{unit["script_id"]}.js"></script>'
                embed_container = ''
            elif unit['name'] == 'Smartlink':
                # Smartlink: https://pl28051870.effectivegatecpm.com/4a/86/ea/4a86ea279595978600ecb939c3f7b4b8.js
                embed_script = f'<script type="text/javascript" src="//pl28051870.effectivegatecpm.com/{unit["script_id"]}.js"></script>'
                embed_container = ''
            elif unit['name'] == 'Banner 728x90':
                # Banner: Uses atOptions format with highperformanceformat CDN
                embed_script = f'''<script type="text/javascript">
    atOptions = {{
        'key' : '{unit["script_id"]}',
        'format' : 'iframe',
        'height' : 90,
        'width' : 728,
        'params' : {{}}
    }};
</script>
<script type="text/javascript" src="//www.highperformanceformat.com/{unit["script_id"]}/invoke.js"></script>'''
                embed_container = ''
            elif unit['name'] == 'Social Bar':
                # Social Bar uses direct invoke
                embed_script = f'<script type="text/javascript" src="//pl28051870.effectivegatecpm.com/{unit["script_id"]}.js"></script>'
                embed_container = ''
            else:  # Native Banner
                # Native Banner: needs container div
                embed_script = f'<script async="async" data-cfasync="false" src="{unit["embed_url"]}/{unit["script_id"]}/invoke.js"></script>'
                embed_container = f'<div id="container-{unit["script_id"]}"></div>'
            
            return {
                'provider': 'adsterra',
                'ad_id': f'adsterra_{unit["id"]}_{unit["script_id"]}',
                'type': unit['name'].lower().replace(' ', '_'),
                'ad_unit_id': unit['id'],
                'title': f'Adsterra {unit["name"]}',
                'description': 'View premium content and earn rewards',
                'advertiser': 'Adsterra Network',
                'duration': 10,
                'reward': reward_amount,
                'format': unit['name'],
                'embed_script': embed_script,
                'embed_container': embed_container,
                'is_embed': True,
                'embed_script_id': unit['script_id'],
                'ecpm': unit['ecpm'],
                'unit_name': unit['name']
            }
                
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def track_impression(self, ad_id, user_id, impression_url=None):
        """Track ad impression"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO ad_impressions 
                    (provider, ad_id, user_id, timestamp, status) 
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP, 'shown')
                ''', (self.name, ad_id, user_id))
                conn.commit()
            
            # Fire impression tracking pixel if provided
            if impression_url:
                try:
                    requests.get(impression_url, timeout=2)
                except:
                    pass
                    
        except Exception as e:
            print(f"Error tracking impression: {e}")
    
    def track_completion(self, ad_id, user_id, watch_time):
        """Track ad completion"""
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


class DemoAdProvider:
    """Demo/Fallback ads when Adsterra is unavailable"""
    
    def __init__(self, enabled=True):
        self.name = 'demo'
        self.enabled = enabled
        self.demo_ads = [
            {
                'provider': 'demo',
                'ad_id': 'demo_mtn_001',
                'creative_url': 'https://via.placeholder.com/800x600/0066CC/FFF?text=MTN+Data',
                'title': 'MTN Mega Data Deal',
                'description': 'Get 50% more data on all recharges this month!',
                'advertiser': 'MTN South Africa',
                'duration': 30,
                'reward': 2.0,
                'format': 'native',
                'image_url': 'https://via.placeholder.com/400x300/0066CC/FFF?text=MTN'
            },
            {
                'provider': 'demo',
                'ad_id': 'demo_shoprite_001',
                'creative_url': 'https://via.placeholder.com/800x600/00AA00/FFF?text=Shoprite',
                'title': 'Shoprite Fresh Specials',
                'description': 'Fresh produce at unbeatable prices all week!',
                'advertiser': 'Shoprite',
                'duration': 10,
                'reward': 1.5,
                'format': 'banner',
                'image_url': 'https://via.placeholder.com/400x300/00AA00/FFF?text=Shoprite'
            },
            {
                'provider': 'demo',
                'ad_id': 'demo_vodacom_001',
                'creative_url': 'https://via.placeholder.com/800x600/E60000/FFF?text=Vodacom',
                'title': 'Vodacom LTE Upgrade',
                'description': 'Unlimited streaming with LTE upgrade!',
                'advertiser': 'Vodacom',
                'duration': 10,
                'reward': 2.0,
                'format': 'native',
                'image_url': 'https://via.placeholder.com/400x300/E60000/FFF?text=Vodacom'
            }
        ]
    
    def fetch_ad(self, ad_format='native', user_country='ZA'):
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


class AdManager:
    """Manages Adsterra multi-unit + Demo fallback"""
    
    def __init__(self, ad_unit_id=None, publisher_id=None):
        from config_adsterra import AdsterraConfig
        
        self.config = AdsterraConfig
        
        # Initialize providers (no longer need ad_unit_id - uses smart rotation)
        self.providers = [
            AdsterraProvider(enabled=self.config.ADSTERRA_ENABLED),
            DemoAdProvider(enabled=self.config.DEMO_ENABLED)
        ]
        
        self.fallback_to_demo = self.config.FALLBACK_TO_DEMO
        
        # Log status
        enabled = [p.name for p in self.providers if p.enabled]
        print(f"\n{'='*60}")
        print(f"🎬 AD MANAGER INITIALIZED - MULTI-UNIT ROTATION")
        print(f"{'='*60}")
        print(f"Enabled providers: {', '.join(enabled)}")
        print(f"Adsterra Units: Native Banner (60%), Popunder (20%), Banner 728x90 (20%) - Random Rotation")
        print(f"Fallback to demo: {self.fallback_to_demo}")
        print(f"{'='*60}\n")
    
    def get_ad(self, ad_format='native', user_id=None, user_country='ZA'):
        """
        Fetch ad from providers with fallback
        
        Args:
            ad_format: 'native', 'banner', or 'social_bar'
            user_id: Current user ID
            user_country: ISO country code
        
        Returns:
            Ad data dict or None
        """
        print(f"\n{'='*60}")
        print(f"🎬 Fetching {ad_format} ad for {user_country}")
        print(f"{'='*60}")
        
        # Try Adsterra first
        for provider in self.providers:
            # Skip demo unless fallback is enabled
            if provider.name == 'demo' and not self.fallback_to_demo:
                if len([p for p in self.providers if p.enabled and p.name != 'demo']) > 0:
                    continue
            
            if not provider.enabled:
                continue
            
            print(f"→ Trying provider: {provider.name}")
            
            ad_data = provider.fetch_ad(ad_format, user_country)
            
            if ad_data:
                print(f"✓ Ad fetched from {provider.name}")
                print(f"  Title: {ad_data.get('title')}")
                print(f"  Reward: {ad_data.get('reward')} MIGP")
                print(f"{'='*60}\n")
                
                # Track impression
                if user_id:
                    provider.track_impression(
                        ad_data['ad_id'], 
                        user_id,
                        ad_data.get('impression_url')
                    )
                
                # Add provider info
                ad_data['provider_name'] = provider.name
                ad_data['provider'] = provider.name  # Also set 'provider' field
                return ad_data
        
        print(f"✗ No ads available")
        print(f"{'='*60}\n")
        return None
    
    def complete_ad(self, provider_name, ad_id, user_id, watch_time, click_url=None):
        """
        Mark ad as completed
        
        Args:
            provider_name: Provider that served the ad
            ad_id: Ad ID
            user_id: User ID
            watch_time: Seconds watched
            click_url: Optional click tracking URL
        """
        provider = next((p for p in self.providers if p.name == provider_name), None)
        if provider:
            provider.track_completion(ad_id, user_id, watch_time)
            
            # Fire click tracking if provided
            if click_url:
                try:
                    requests.get(click_url, timeout=2)
                except:
                    pass


# Test the implementation
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🧪 TESTING ADSTERRA INTEGRATION")
    print("="*60 + "\n")
    
    # Initialize manager (will use .env variables)
    manager = AdManager()
    
    # Test fetching an ad
    print("1. Fetching native ad...")
    ad = manager.get_ad(ad_format='native', user_id=1, user_country='ZA')
    
    if ad:
        print(f"\n✓ Ad received:")
        print(f"  Provider: {ad['provider_name']}")
        print(f"  Title: {ad['title']}")
        print(f"  Advertiser: {ad['advertiser']}")
        print(f"  Reward: {ad['reward']} MIGP")
        print(f"  Format: {ad['format']}")
    else:
        print("\n✗ No ad received")
    
    print("\n" + "="*60 + "\n")
