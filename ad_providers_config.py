"""
ad_providers_config.py - Multi-Provider Ad Network Configuration

Manage multiple ad providers for watch-to-earn app. Add providers one by one.
Each provider has its own CPM estimate and can be enabled/disabled independently.

Providers (to be added progressively):
1. ✅ Adsterra - $1.65 eCPM (ACTIVE)
2. ⏳ PropellerAds - $1.65 eCPM
3. ⏳ AdMaven - $2.00 eCPM
4. ⏳ Bidvertiser - $1.65 eCPM
5. ⏳ AppLixir - $2.75 eCPM
6. ⏳ Infolinks - $0.95 eCPM
7. ⏳ Adcash - $1.65 eCPM
8. ⏳ HilltopAds - $1.65 eCPM
9. ⏳ Clickadu - $1.60 eCPM
10. ⏳ ExoClick - $1.25 eCPM
"""

import os
from dotenv import load_dotenv

load_dotenv()

class AdProvidersConfig:
    """Configuration for all ad providers"""
    
    # Provider definitions with estimated eCPM
    PROVIDERS = {
        'adsterra': {
            'name': 'Adsterra',
            'enabled': os.getenv('ADSTERRA_ENABLED', 'True').lower() == 'true',
            'ecpm': 1.65,  # USD per 1000 impressions
            'priority': 5,  # Highest priority
            'config': {
                'publisher_id': os.getenv('ADSTERRA_PUBLISHER_ID'),
                'ad_unit_ids': os.getenv('ADSTERRA_AD_UNIT_IDS', '27950195'),
                'api_key': os.getenv('ADSTERRA_API_KEY'),
            },
            'status': '✅ ACTIVE',
            'notes': 'Instant approval, native banners + popunders'
        },
        'propellerads': {
            'name': 'PropellerAds',
            'enabled': os.getenv('PROPELLERADS_ENABLED', 'False').lower() == 'true',
            'ecpm': 1.65,  # USD per 1000 impressions
            'priority': 4,
            'config': {
                'publisher_id': os.getenv('PROPELLERADS_PUBLISHER_ID'),
                'api_key': os.getenv('PROPELLERADS_API_KEY'),
            },
            'status': '⏳ TODO',
            'notes': 'Similar to Adsterra, instant approval'
        },
        'admaven': {
            'name': 'AdMaven',
            'enabled': os.getenv('ADMAVEN_ENABLED', 'False').lower() == 'true',
            'ecpm': 2.00,  # USD per 1000 impressions (higher eCPM!)
            'priority': 3,
            'config': {
                'publisher_id': os.getenv('ADMAVEN_PUBLISHER_ID'),
                'api_key': os.getenv('ADMAVEN_API_KEY'),
            },
            'status': '⏳ TODO',
            'notes': 'Works well with SA traffic, highest eCPM'
        },
        'bidvertiser': {
            'name': 'Bidvertiser',
            'enabled': os.getenv('BIDVERTISER_ENABLED', 'False').lower() == 'true',
            'ecpm': 1.65,
            'priority': 2,
            'config': {
                'publisher_id': os.getenv('BIDVERTISER_PUBLISHER_ID'),
                'api_key': os.getenv('BIDVERTISER_API_KEY'),
            },
            'status': '⏳ TODO',
            'notes': 'No traffic requirements'
        },
        'applixir': {
            'name': 'AppLixir',
            'enabled': os.getenv('APPLIXIR_ENABLED', 'False').lower() == 'true',
            'ecpm': 2.75,  # Highest eCPM
            'priority': 1,
            'config': {
                'publisher_id': os.getenv('APPLIXIR_PUBLISHER_ID'),
                'api_key': os.getenv('APPLIXIR_API_KEY'),
            },
            'status': '⏳ TODO',
            'notes': 'Highest eCPM ($2.75), premium network'
        },
        'infolinks': {
            'name': 'Infolinks',
            'enabled': os.getenv('INFOLINKS_ENABLED', 'False').lower() == 'true',
            'ecpm': 0.95,
            'priority': 0,
            'config': {
                'publisher_id': os.getenv('INFOLINKS_PUBLISHER_ID'),
                'api_key': os.getenv('INFOLINKS_API_KEY'),
            },
            'status': '⏳ TODO',
            'notes': 'Modest traffic requirements'
        },
        'adcash': {
            'name': 'Adcash',
            'enabled': os.getenv('ADCASH_ENABLED', 'False').lower() == 'true',
            'ecpm': 1.65,
            'priority': 0,
            'config': {
                'publisher_id': os.getenv('ADCASH_PUBLISHER_ID'),
                'api_key': os.getenv('ADCASH_API_KEY'),
            },
            'status': '⏳ TODO',
            'notes': 'No traffic requirements'
        },
        'hilltopads': {
            'name': 'HilltopAds',
            'enabled': os.getenv('HILLTOPADS_ENABLED', 'False').lower() == 'true',
            'ecpm': 1.65,
            'priority': 0,
            'config': {
                'publisher_id': os.getenv('HILLTOPADS_PUBLISHER_ID'),
                'api_key': os.getenv('HILLTOPADS_API_KEY'),
            },
            'status': '⏳ TODO',
            'notes': 'Low payout threshold'
        },
        'clickadu': {
            'name': 'Clickadu',
            'enabled': os.getenv('CLICKADU_ENABLED', 'False').lower() == 'true',
            'ecpm': 1.60,
            'priority': 0,
            'config': {
                'publisher_id': os.getenv('CLICKADU_PUBLISHER_ID'),
                'api_key': os.getenv('CLICKADU_API_KEY'),
            },
            'status': '⏳ TODO',
            'notes': 'No traffic requirements'
        },
        'exoclick': {
            'name': 'ExoClick',
            'enabled': os.getenv('EXOCLICK_ENABLED', 'False').lower() == 'true',
            'ecpm': 1.25,
            'priority': 0,
            'config': {
                'publisher_id': os.getenv('EXOCLICK_PUBLISHER_ID'),
                'api_key': os.getenv('EXOCLICK_API_KEY'),
            },
            'status': '⏳ TODO',
            'notes': 'Starting from 0.01 CPM, very flexible'
        }
    }
    
    @classmethod
    def get_enabled_providers(cls):
        """Get list of enabled providers sorted by priority"""
        enabled = [
            (key, config) for key, config in cls.PROVIDERS.items() 
            if config['enabled']
        ]
        # Sort by priority (higher first)
        enabled.sort(key=lambda x: x[1]['priority'], reverse=True)
        return enabled
    
    @classmethod
    def get_provider_config(cls, provider_key):
        """Get specific provider configuration"""
        return cls.PROVIDERS.get(provider_key, {})
    
    @classmethod
    def get_blended_ecpm(cls):
        """Calculate blended eCPM from all enabled providers"""
        enabled = cls.get_enabled_providers()
        if not enabled:
            return 0.003  # Fallback to demo eCPM
        
        total_ecpm = sum(config['ecpm'] for _, config in enabled)
        avg_ecpm = total_ecpm / len(enabled)
        return avg_ecpm
    
    @classmethod
    def print_status(cls):
        """Print status of all providers"""
        print("\n" + "="*60)
        print("📊 AD PROVIDERS STATUS")
        print("="*60)
        
        for key, config in cls.PROVIDERS.items():
            status = config['status']
            ecpm = config['ecpm']
            name = config['name']
            print(f"{status} {name:20} - ${ecpm:.2f} eCPM")
        
        print("="*60)
        enabled = cls.get_enabled_providers()
        if enabled:
            blended = cls.get_blended_ecpm()
            print(f"✅ Enabled: {len(enabled)} provider(s)")
            print(f"📈 Blended eCPM: ${blended:.2f}")
        else:
            print("❌ No providers enabled - using demo ads")
        print("="*60 + "\n")

# Print status on import
if __name__ == '__main__':
    AdProvidersConfig.print_status()
