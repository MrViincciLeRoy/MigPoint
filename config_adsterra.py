"""
config_adsterra.py - Adsterra-specific configuration
For your watch-to-earn web app prototype
"""

import os
from dotenv import load_dotenv

load_dotenv()

class AdsterraConfig:
    """Adsterra Configuration - Multi-Unit Smart Rotation"""
    
    # Adsterra Settings
    # Set ADSTERRA_ENABLED=True to use real Adsterra ads
    ADSTERRA_ENABLED = os.getenv('ADSTERRA_ENABLED', 'False').lower() == 'true'
    ADSTERRA_PUBLISHER_ID = os.getenv('ADSTERRA_PUBLISHER_ID', None)  # e.g., "5408450"
    
    # Multi-unit support (NEW: replaces single ADSTERRA_AD_UNIT_ID)
    ADSTERRA_AD_UNIT_IDS = os.getenv('ADSTERRA_AD_UNIT_IDS', None)  # e.g., "27951368,27951380,27950195"
    
    # Backward compatibility: support old single unit ID for migration
    ADSTERRA_AD_UNIT_ID = os.getenv('ADSTERRA_AD_UNIT_ID', None)  # DEPRECATED: use ADSTERRA_AD_UNIT_IDS
    
    # Validate that at least one ad unit ID is set if enabled
    if ADSTERRA_ENABLED and not ADSTERRA_AD_UNIT_IDS and not ADSTERRA_AD_UNIT_ID:
        print("⚠️  WARNING: ADSTERRA_ENABLED=True but no ad unit IDs configured")
        print("   Add ADSTERRA_AD_UNIT_IDS to .env (e.g., 27951368,27951380,27950195)")
        print("   Or use ADSTERRA_AD_UNIT_ID for single unit (deprecated)")
        print("   Falling back to DEMO_ENABLED=True")
        ADSTERRA_ENABLED = False
    
    # Ad Format Settings
    ADSTERRA_AD_FORMAT = os.getenv('ADSTERRA_AD_FORMAT', 'native_banner')
    
    # Demo/Fallback
    DEMO_ENABLED = os.getenv('DEMO_ENABLED', 'True').lower() == 'true'
    FALLBACK_TO_DEMO = os.getenv('FALLBACK_TO_DEMO', 'True').lower() == 'true'
    
    # Request timeout
    REQUEST_TIMEOUT = int(os.getenv('AD_REQUEST_TIMEOUT', '5'))
    
    # Provider Priority
    PROVIDER_PRIORITY = {
        'adsterra': 5,   # Your primary provider
        'demo': 1        # Fallback
    }
    
    # Expected eCPM for South Africa (for revenue calculation)
    ADSTERRA_ECPM_ZA = 1.65  # USD per 1000 impressions (average from your research)
    
    @classmethod
    def get_reward_from_ecpm(cls, ecpm_usd=1.65, user_share=0.7, min_reward=0.05):
        """
        Calculate MIGP reward based on eCPM
        
        Args:
            ecpm_usd: Actual eCPM in USD (e.g., 0.003, 1.65)
            user_share: Percentage of revenue shared with user (0.7 = 70%)
            min_reward: Minimum MIGP reward to avoid rounding to 0 (default 0.05)
        
        Returns:
            MIGP reward per ad view
        """
        # Convert to ZAR (approx 18.5 ZAR per USD)
        ecpm_zar = ecpm_usd * 18.5
        
        # Revenue per impression
        revenue_per_impression = ecpm_zar / 1000
        
        # User's share
        user_revenue = revenue_per_impression * user_share
        
        # Convert to MIGP (10 MIGP = R1)
        migp_reward = user_revenue * 10
        
        # Ensure minimum reward so low CPM doesn't round to 0
        if migp_reward < min_reward:
            migp_reward = min_reward
        
        return round(migp_reward, 2)


# Example usage:
if __name__ == '__main__':
    print("\n" + "="*60)
    print("💰 ADSTERRA REWARD CALCULATOR")
    print("="*60 + "\n")
    
    # Calculate at different eCPMs
    ecpms = [0.80, 1.65, 2.50]  # Low, Average, High
    
    for ecpm in ecpms:
        reward = AdsterraConfig.get_reward_from_ecpm(ecpm)
        print(f"eCPM ${ecpm:.2f}:")
        print(f"  → User earns: {reward} MIGP per ad")
        print(f"  → 10 ads: {reward * 10} MIGP (R{reward * 10 / 10:.2f})")
        print()
    
    print("="*60)
    print("✓ With average $1.65 eCPM:")
    print(f"  User watches 10 ads/day = {AdsterraConfig.get_reward_from_ecpm() * 10} MIGP")
    print(f"  Monthly (22 days) = {AdsterraConfig.get_reward_from_ecpm() * 10 * 22} MIGP")
    print(f"  = R{AdsterraConfig.get_reward_from_ecpm() * 10 * 22 / 10:.2f}/month")
    print("="*60 + "\n")
