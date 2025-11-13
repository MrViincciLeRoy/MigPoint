"""
config.py - Configuration for Ad Providers
Store your API keys and settings here
"""

import os
from dotenv import load_dotenv

load_dotenv()

class AdConfig:
    """Configuration for ad providers"""
    
    # Google AdMob
    ADMOB_ENABLED = os.getenv('ADMOB_ENABLED', 'False').lower() == 'true'
    ADMOB_API_KEY = os.getenv('ADMOB_API_KEY', None)
    ADMOB_APP_ID = os.getenv('ADMOB_APP_ID', None)
    
    # Unity Ads
    UNITY_ENABLED = os.getenv('UNITY_ENABLED', 'False').lower() == 'true'
    UNITY_GAME_ID = os.getenv('UNITY_GAME_ID', None)
    UNITY_API_KEY = os.getenv('UNITY_API_KEY', None)
    
    # Facebook Audience Network
    FACEBOOK_ENABLED = os.getenv('FACEBOOK_ENABLED', 'False').lower() == 'true'
    FACEBOOK_PLACEMENT_ID = os.getenv('FACEBOOK_PLACEMENT_ID', None)
    FACEBOOK_API_KEY = os.getenv('FACEBOOK_API_KEY', None)
    
    # Smaato
    SMAATO_ENABLED = os.getenv('SMAATO_ENABLED', 'False').lower() == 'true'
    SMAATO_PUBLISHER_ID = os.getenv('SMAATO_PUBLISHER_ID', None)
    SMAATO_ADSPACE_ID = os.getenv('SMAATO_ADSPACE_ID', None)
    
    # AppLovin MAX
    APPLOVIN_ENABLED = os.getenv('APPLOVIN_ENABLED', 'False').lower() == 'true'
    APPLOVIN_SDK_KEY = os.getenv('APPLOVIN_SDK_KEY', None)
    
    # ironSource
    IRONSOURCE_ENABLED = os.getenv('IRONSOURCE_ENABLED', 'False').lower() == 'true'
    IRONSOURCE_APP_KEY = os.getenv('IRONSOURCE_APP_KEY', None)
    
    # Demo/Test Mode
    DEMO_ENABLED = os.getenv('DEMO_ENABLED', 'True').lower() == 'true'
    
    # Provider Priority (higher = preferred)
    PROVIDER_PRIORITY = {
        'admob': 6,
        'applovin': 5,
        'unity': 4,
        'facebook': 3,
        'ironsource': 3,
        'smaato': 2,
        'demo': 1
    }
    
    # Request timeout in seconds
    REQUEST_TIMEOUT = int(os.getenv('AD_REQUEST_TIMEOUT', '5'))
    
    # Fallback to demo if all providers fail
    FALLBACK_TO_DEMO = os.getenv('FALLBACK_TO_DEMO', 'True').lower() == 'true'
