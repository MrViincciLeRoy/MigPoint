"""
ad_units_config.py - Multi-Unit Ad Configuration for Adsterra

Strategy to increase CPM from $0.003 to $0.05-$0.10:
1. Use multiple ad units with different placements
2. Rotate between high-performing units
3. Test different formats (banner, native, interstitial)
4. Higher-value placements earn 10-30x more
"""

# Adsterra Ad Units Configuration
# Create these in your Adsterra dashboard
AD_UNITS = {
    'banner_top': {
        'id': 27950195,  # Current: Native Banner (Top)
        'name': 'Top Banner',
        'format': 'native_banner',
        'placement': 'top',
        'expected_cpm': 0.003,  # Current ZA traffic
        'priority': 1,
        'enabled': True
    },
    'interstitial': {
        'id': 27950196,  # NEW: Interstitial (higher CPM)
        'name': 'Interstitial Modal',
        'format': 'interstitial',
        'placement': 'modal',
        'expected_cpm': 0.50,  # Interstitials pay 100-200x more
        'priority': 3,
        'enabled': False,  # Create this in Adsterra first
        'notes': 'Show after every 5 ads - highest CPM'
    },
    'video_banner': {
        'id': 27950197,  # NEW: Video Banner (mid CPM)
        'name': 'Video Banner',
        'format': 'video_banner',
        'placement': 'video',
        'expected_cpm': 0.08,  # Video ads pay 15-25x more
        'priority': 2,
        'enabled': False,  # Create this in Adsterra first
        'notes': 'Video ads between regular ads'
    },
    'social_bar': {
        'id': 27950198,  # NEW: Social Bar (low CPM but high volume)
        'name': 'Social Bar',
        'format': 'social_bar',
        'placement': 'floating',
        'expected_cpm': 0.001,  # Lower but fills gaps
        'priority': 0,
        'enabled': False,  # Create this in Adsterra first
        'notes': 'Floating widget for passive income'
    }
}

# Recommended Deployment Strategy
DEPLOYMENT_STRATEGY = {
    'phase_1_current': {
        'units': ['banner_top'],
        'cpm_estimate': 0.003,
        'monthly_per_1k_views': '$3',
        'status': 'ACTIVE NOW'
    },
    'phase_2_add_video': {
        'units': ['banner_top', 'video_banner'],
        'rotation': 'every 2nd ad = video',
        'cpm_estimate': 0.045,  # (0.003 + 0.08) / 2
        'monthly_per_1k_views': '$45',
        'status': 'INCREASES 15x'
    },
    'phase_3_add_interstitial': {
        'units': ['banner_top', 'video_banner', 'interstitial'],
        'rotation': 'every 5 ads = interstitial',
        'cpm_estimate': 0.15,  # (0.003 * 3 + 0.08 * 1 + 0.50 * 1) / 5
        'monthly_per_1k_views': '$150',
        'status': 'INCREASES 50x'
    },
    'phase_4_all_units': {
        'units': ['banner_top', 'video_banner', 'interstitial', 'social_bar'],
        'rotation': 'smart rotation by performance',
        'cpm_estimate': 0.20,  # Blended average
        'monthly_per_1k_views': '$200',
        'status': 'INCREASES 67x'
    }
}

# CPM Comparison by Format
CPM_BY_FORMAT = {
    'native_banner': {
        'avg_cpm': 0.003,
        'range': '$0.001 - $0.005',
        'pros': 'Non-intrusive, user-friendly',
        'cons': 'Lowest CPM'
    },
    'video_banner': {
        'avg_cpm': 0.08,
        'range': '$0.05 - $0.15',
        'pros': 'High engagement, good CPM',
        'cons': 'Requires video content'
    },
    'interstitial': {
        'avg_cpm': 0.50,
        'range': '$0.20 - $1.00',
        'pros': 'HIGHEST CPM, 100-200x better',
        'cons': 'Can hurt user experience if overused'
    },
    'social_bar': {
        'avg_cpm': 0.001,
        'range': '$0.0005 - $0.003',
        'pros': 'Passive, no interaction required',
        'cons': 'Lowest CPM but passive income'
    }
}

# Implementation Steps
IMPLEMENTATION_STEPS = """
STEP 1: Create New Ad Units in Adsterra Dashboard
=====================================================
1. Log in: https://adsterra.com/dashboard
2. Go to Publisher ID: 5408450
3. Create new ad units:
   - Video Banner (NativeBanner format, set to "Video")
   - Interstitial (choose "Interstitial" format)
   - Social Bar (choose "Social Bar" format)
4. Get their IDs and update ad_units_config.py

STEP 2: Update adsterra_provider.py
=====================================
1. Rotate between units instead of always using 27950195
2. Prioritize higher CPM units more often
3. Implement cooldown between interstitials (every 5 ads)

STEP 3: Monitor Performance
=============================
1. Check Adsterra dashboard daily for first week
2. Track CPM changes in stats.csv
3. Adjust rotation if needed

EXPECTED RESULTS:
- Week 1: $0.003 CPM (current)
- Week 2: $0.045 CPM (add video, +15x)
- Week 3: $0.15 CPM (add interstitial, +50x)
- Week 4+: $0.20 CPM (balanced mix)

Example: 1000 impressions
- Current: 1000 × $0.003 = $3.00
- With optimization: 1000 × $0.15 = $150.00
- With premium mix: 1000 × $0.20 = $200.00
"""

def get_unit_by_priority(enabled_only=True):
    """Get ad units sorted by priority (highest first)"""
    units = AD_UNITS.values()
    if enabled_only:
        units = [u for u in units if u['enabled']]
    return sorted(units, key=lambda x: x['priority'], reverse=True)

def get_next_unit_for_rotation(current_unit_id, view_count):
    """
    Smart rotation: Show high CPM units more strategically
    Every 5 views: try to show interstitial
    Every 2 views: try to show video
    Default: show banner
    """
    if view_count % 5 == 0:
        # Try interstitial every 5 ads
        unit = AD_UNITS.get('interstitial')
        if unit and unit['enabled']:
            return unit
    
    if view_count % 2 == 0:
        # Try video every 2 ads
        unit = AD_UNITS.get('video_banner')
        if unit and unit['enabled']:
            return unit
    
    # Default to banner
    return AD_UNITS.get('banner_top')

def calculate_blended_cpm(enabled_units_only=True):
    """Calculate average CPM from enabled units"""
    units = [u for u in AD_UNITS.values() if not enabled_units_only or u['enabled']]
    if not units:
        return 0.003
    
    total_cpm = sum(u['expected_cpm'] for u in units)
    return total_cpm / len(units)
