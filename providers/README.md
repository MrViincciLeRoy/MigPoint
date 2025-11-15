# Ad Providers System

Modular ad provider system for easy addition of multiple ad networks.

## Current Providers

### ✅ Adsterra (Active)
- **Status:** Primary provider
- **CPM:** $0.003 - $2.50+ (avg $1.65)
- **Setup:** Already configured
- **Features:** Multiple ad formats (Native Banner, Smartlink, Popunder, Social Bar, Banner)

### ✅ Demo Provider
- **Status:** Fallback provider
- **CPM:** N/A (fixed rewards)
- **Setup:** Always available for testing
- **Features:** Sample ads for development

## Adding New Providers

### Quick Start

1. **Copy template:**
   ```
   providers/PROVIDER_TEMPLATE.py → providers/[provider_name]_provider.py
   ```

2. **Customize:**
   - Update class name
   - Set publisher_id and api_key
   - Implement fetch_ad() method
   - Update priority (1-5, higher = better)

3. **Register in app.py:**
   ```python
   from providers import [ProviderName]Provider
   
   # In ad_manager initialization
   ad_manager = ProviderManager(
       adsterra_enabled=True,
       demo_enabled=True
   )
   ```

4. **Test:**
   - Restart app
   - Check logs for provider status
   - Load dashboard and click "Watch Ad"

## Providers to Add Next

### PropellerAds
- **CPM:** $0.80 - $2.50+ (avg $1.65)
- **Traffic Requirement:** None (free signup)
- **Status:** Ready to add
- **File:** `providers/propelleradds_provider.py`

### AdMaven
- **CPM:** $1.00 - $3.00+ (avg $2.00)
- **Traffic Requirement:** None
- **Status:** Ready to add
- **File:** `providers/admaven_provider.py`

### Bidvertiser
- **CPM:** $0.80 - $2.50+ (avg $1.65)
- **Traffic Requirement:** None
- **Status:** Ready to add
- **File:** `providers/bidvertiser_provider.py`

### AppLixir
- **CPM:** $1.00 - $4.50+ (avg $2.75)
- **Traffic Requirement:** None
- **Status:** Ready to add
- **File:** `providers/applixir_provider.py`

### Infolinks
- **CPM:** $0.40 - $1.50+ (avg $0.95)
- **Traffic Requirement:** Low pageview requirement
- **Status:** Ready to add
- **File:** `providers/infolinks_provider.py`

### Adcash
- **CPM:** $0.80 - $2.50+ (avg $1.65)
- **Traffic Requirement:** None
- **Status:** Ready to add
- **File:** `providers/adcash_provider.py`

### HilltopAds
- **CPM:** $0.80 - $2.50+ (avg $1.65)
- **Traffic Requirement:** None (low payout threshold)
- **Status:** Ready to add
- **File:** `providers/hilltopads_provider.py`

### Clickadu
- **CPM:** $0.70 - $2.50+ (avg $1.60)
- **Traffic Requirement:** None
- **Status:** Ready to add
- **File:** `providers/clickadu_provider.py`

### ExoClick
- **CPM:** $0.50 - $2.00+ (avg $1.25)
- **Traffic Requirement:** None (starting from 0.01 CPM)
- **Status:** Ready to add
- **File:** `providers/exoclick_provider.py`

## Provider Priority System

Higher priority = shown more frequently:
- **5:** Primary high-CPM providers (Adsterra, PropellerAds)
- **4:** Secondary providers (AdMaven, AppLixir)
- **3:** Medium-CPM providers (Bidvertiser, Adcash)
- **2:** Lower-CPM providers (Infolinks, ExoClick)
- **1:** Fallback (Demo)

## Rotation Strategy

The ProviderManager tries providers in order of priority:
1. Tries highest priority provider
2. If unavailable, tries next provider
3. Falls back to Demo if all fail

## Adding a Provider Step-by-Step

### Example: Adding PropellerAds

1. **Create file:** `providers/propelleradds_provider.py`

2. **Copy template and customize:**
   ```python
   class PropellerAdsProvider(BaseProvider):
       def __init__(self, enabled=True, publisher_id=None, api_key=None):
           super().__init__('propelleradds', enabled)
           self.priority = 4  # High priority
           self.publisher_id = publisher_id  # From PropellerAds account
           self.api_key = api_key
           self.base_ecpm = 1.65
       
       def fetch_ad(self, ad_format='native', user_country='ZA', view_count=0):
           # Implement PropellerAds API call
           pass
   ```

3. **Update `__init__.py`:**
   ```python
   from .propelleradds_provider import PropellerAdsProvider
   __all__ = [..., 'PropellerAdsProvider']
   ```

4. **Update `provider_manager.py`:**
   Add PropellerAds initialization in ProviderManager.__init__()

5. **Update `.env`:**
   ```
   PROPELLERADDS_ENABLED=True
   PROPELLERADDS_PUBLISHER_ID=your_id
   PROPELLERADDS_API_KEY=your_key
   ```

6. **Update `app.py`:**
   Load provider configuration from .env

## Testing Providers

```python
# Test in Python shell
from providers import ProviderManager

manager = ProviderManager()
ad = manager.get_ad(user_country='ZA')
print(f"Got ad: {ad['title']} ({ad['provider']})")
```

## Monitoring

Each provider logs:
- Initialization status
- Fetch attempts
- Success/failure for each ad request
- Errors or exceptions

Check logs for provider health and performance.

## Expected Revenue Impact

Current setup (Adsterra only):
- **CPM:** $0.003 (actual, very low)
- **1000 impressions:** $3

With 5 providers (balanced mix):
- **CPM:** $1.50+ (average)
- **1000 impressions:** $1500+

**That's a 500x increase!** 🚀
