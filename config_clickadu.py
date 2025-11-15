"""
config_clickadu.py - Clickadu Configuration
Manages Clickadu ad zones and API configuration
"""

class ClickaduConfig:
    """Clickadu ad configuration"""
    
    # Clickadu API Token (replace with your actual token)
    API_TOKEN = 'your_clickadu_api_token_here'
    
    # Clickadu Zone IDs for different placements
    ZONES = {
        'dashboard_top': {
            'zone_id': '123456',  # Replace with your zone ID
            'name': 'Dashboard Top',
            'format': 'native',
            'ecpm': 0.008,
            'enabled': True
        },
        'dashboard_bottom': {
            'zone_id': '123457',  # Replace with your zone ID
            'name': 'Dashboard Bottom',
            'format': 'banner',
            'ecpm': 0.006,
            'enabled': True
        },
        'watch_ad': {
            'zone_id': '123458',  # Replace with your zone ID
            'name': 'Watch Ad Page',
            'format': 'native',
            'ecpm': 0.010,
            'enabled': True
        }
    }
    
    # Clickadu API endpoints
    API_ENDPOINTS = {
        'stats': 'http://v2.api.clickadu.com/partner/stats',
        'ads': 'http://v2.api.clickadu.com/partner/ads'
    }
    
    # Script loading URL
    SCRIPT_URL = 'https://bot.clickadu.com/display.js'
    
    @classmethod
    def get_zone(cls, placement):
        """Get zone configuration for a placement"""
        return cls.ZONES.get(placement, None)
    
    @classmethod
    def is_enabled(cls):
        """Check if Clickadu is enabled"""
        return cls.API_TOKEN != 'your_clickadu_api_token_here'
