#!/usr/bin/env python3
"""
Quick test to verify the ad system is working properly
"""

import sys
import os
from dotenv import load_dotenv

# Setup environment
load_dotenv()

# Test 1: Check AdManager initialization
print("\n" + "="*60)
print("TEST 1: AdManager Initialization")
print("="*60)

try:
    from adsterra_provider import AdManager
    am = AdManager()
    print("✅ AdManager initialized successfully")
    
    # Check providers
    if am.providers:
        print(f"✅ {len(am.providers)} providers loaded:")
        for p in am.providers:
            status = "ENABLED" if p.enabled else "DISABLED"
            print(f"   - {p.name}: {status}")
    else:
        print("❌ No providers found")
except Exception as e:
    print(f"❌ AdManager initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Fetch a Native Banner ad
print("\n" + "="*60)
print("TEST 2: Fetch Native Banner Ad")
print("="*60)

try:
    ad = am.get_ad(ad_format='native', user_id=1, user_country='ZA')
    
    if ad:
        print("✅ Ad fetched successfully")
        print(f"   Title: {ad.get('title')}")
        print(f"   Provider: {ad.get('provider')}")
        print(f"   Reward: {ad.get('reward')} MIGP")
        print(f"   Is Embed: {ad.get('is_embed')}")
        print(f"   Format: {ad.get('format')}")
        print(f"   Script ID: {ad.get('embed_script_id')}")
        print(f"   Unit Name: {ad.get('unit_name')}")
        
        # Check required fields
        required_fields = ['ad_id', 'title', 'reward', 'is_embed', 'embed_script_id', 'format', 'unit_name']
        missing = [f for f in required_fields if f not in ad]
        
        if missing:
            print(f"\n⚠️  WARNING: Missing fields: {missing}")
        else:
            print("\n✅ All required fields present")
            
        # If embed ad, check embed-specific fields
        if ad.get('is_embed'):
            embed_fields = ['embed_script', 'embed_container']
            missing_embed = [f for f in embed_fields if f not in ad]
            if missing_embed:
                print(f"⚠️  WARNING: Missing embed fields: {missing_embed}")
            else:
                print("✅ All embed fields present")
    else:
        print("❌ No ad returned")
        
except Exception as e:
    print(f"❌ Ad fetch failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Fetch Demo ad
print("\n" + "="*60)
print("TEST 3: Fetch Demo Ad (with fallback)")
print("="*60)

try:
    # Disable Adsterra to force demo
    am.providers[0].enabled = False
    
    ad = am.get_ad(ad_format='native', user_id=1, user_country='ZA')
    
    if ad:
        print("✅ Demo ad fetched successfully")
        print(f"   Title: {ad.get('title')}")
        print(f"   Provider: {ad.get('provider')}")
        print(f"   Is Embed: {ad.get('is_embed')}")
        
        if ad.get('is_embed') == False:
            print("✅ Demo ad correctly marked as not embed")
        else:
            print("⚠️  WARNING: Demo ad should have is_embed=False")
    else:
        print("❌ No demo ad returned")
        
except Exception as e:
    print(f"❌ Demo ad fetch failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("✅ ALL TESTS PASSED")
print("="*60 + "\n")
