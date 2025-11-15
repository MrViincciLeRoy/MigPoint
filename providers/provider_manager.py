"""
provider_manager.py - Orchestrates multiple ad providers

Manages provider initialization, prioritization, and fallback logic.
"""

from config_adsterra import AdsterraConfig


class ProviderManager:
    """Manages multiple ad providers with fallback strategy"""
    
    def __init__(self, adsterra_enabled=True, demo_enabled=True, fallback_to_demo=True):
        from .adsterra_provider import AdsterraProvider
        from .demo_provider import DemoProvider
        
        self.providers = []
        self.fallback_to_demo = fallback_to_demo
        
        # Initialize Adsterra (primary)
        if adsterra_enabled:
            self.providers.append(AdsterraProvider(enabled=True))
            self.providers[-1].priority = 5
        
        # Initialize Demo (fallback)
        if demo_enabled:
            self.providers.append(DemoProvider(enabled=True))
            self.providers[-1].priority = 1
        
        # Sort by priority (highest first)
        self.providers.sort(key=lambda p: p.priority, reverse=True)
        
        # Log status
        enabled = [p.name for p in self.providers if p.enabled]
        print(f"\n{'='*60}")
        print(f"🎬 PROVIDER MANAGER INITIALIZED")
        print(f"{'='*60}")
        print(f"Enabled providers: {', '.join(enabled)}")
        print(f"Total providers: {len(self.providers)}")
        for p in self.providers:
            if p.enabled:
                print(f"  • {p.name.upper()} (priority: {p.priority})")
        print(f"Fallback to demo: {self.fallback_to_demo}")
        print(f"{'='*60}\n")
    
    def get_ad(self, ad_format='native', user_id=None, user_country='ZA', view_count=0):
        """
        Fetch ad from providers with fallback strategy
        
        Tries primary providers first, falls back to demo if needed
        """
        print(f"\n{'='*60}")
        print(f"🎬 Fetching ad from {len(self.providers)} provider(s)")
        print(f"{'='*60}")
        
        for provider in self.providers:
            if not provider.enabled:
                print(f"⊘ Provider '{provider.name}' is disabled, skipping")
                continue
            
            print(f"→ Trying provider: {provider.name}")
            
            try:
                ad = provider.fetch_ad(
                    ad_format=ad_format,
                    user_country=user_country,
                    view_count=view_count
                )
                
                if ad:
                    print(f"✓ Ad fetched from {provider.name}")
                    print(f"  Title: {ad.get('title', 'N/A')}")
                    print(f"  Reward: {ad.get('reward', 'N/A')} MIGP")
                    print(f"{'='*60}\n")
                    return ad
                else:
                    print(f"✗ {provider.name} returned no ad")
            
            except Exception as e:
                print(f"✗ Error from {provider.name}: {e}")
        
        # All providers failed
        print(f"\n✗ No ads available from any provider")
        print(f"{'='*60}\n")
        return None
    
    def add_provider(self, provider_instance):
        """Add a new provider at runtime"""
        self.providers.append(provider_instance)
        self.providers.sort(key=lambda p: p.priority, reverse=True)
        print(f"✓ Added provider: {provider_instance.name} (priority: {provider_instance.priority})")
    
    def disable_provider(self, provider_name):
        """Disable a provider"""
        for p in self.providers:
            if p.name == provider_name:
                p.enabled = False
                print(f"⊘ Disabled provider: {provider_name}")
                return
        print(f"✗ Provider '{provider_name}' not found")
    
    def enable_provider(self, provider_name):
        """Enable a provider"""
        for p in self.providers:
            if p.name == provider_name:
                p.enabled = True
                print(f"✓ Enabled provider: {provider_name}")
                return
        print(f"✗ Provider '{provider_name}' not found")
    
    def get_provider_status(self):
        """Get status of all providers"""
        return {
            'providers': [
                {
                    'name': p.name,
                    'enabled': p.enabled,
                    'priority': p.priority
                }
                for p in self.providers
            ],
            'total': len(self.providers),
            'active': len([p for p in self.providers if p.enabled])
        }
