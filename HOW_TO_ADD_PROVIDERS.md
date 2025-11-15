# How to Add New Ad Providers (One by One)

## Current Setup
- ✅ **Adsterra** - Active ($1.65 eCPM)
- ⏳ 9 other providers ready to add

## Provider List (By eCPM - Highest First)

| Rank | Provider | eCPM | Status | Notes |
|------|----------|------|--------|-------|
| 1 | AppLixir | $2.75 | ⏳ TODO | Premium, highest eCPM |
| 2 | AdMaven | $2.00 | ⏳ TODO | Works great with SA traffic |
| 3-6 | Adsterra, PropellerAds, Bidvertiser, Adcash, HilltopAds | $1.65 | ✅/$  | Same CPM, different SDKs |
| 7 | Clickadu | $1.60 | ⏳ TODO | No requirements |
| 8 | ExoClick | $1.25 | ⏳ TODO | Very flexible |
| 9 | Infolinks | $0.95 | ⏳ TODO | Modest traffic req |

---

## Step-by-Step: Add a New Provider

### Step 1: Get API Credentials
1. Sign up at provider website (e.g., PropellerAds)
2. Create account → Get Publisher ID and API Key
3. Create an ad unit in their dashboard
4. Copy the SDK/embed code

### Step 2: Add to `.env`
```bash
# For PropellerAds (example)
PROPELLERADS_ENABLED=True
PROPELLERADS_PUBLISHER_ID=your-publisher-id
PROPELLERADS_API_KEY=your-api-key
```

### Step 3: Create Provider Class
Create file: `providers/propellerads_provider.py`

```python
class PropellerAdsProvider:
    def __init__(self, enabled=True):
        self.name = 'propellerads'
        self.enabled = enabled
        self.publisher_id = os.getenv('PROPELLERADS_PUBLISHER_ID')
        self.api_key = os.getenv('PROPELLERADS_API_KEY')
    
    def fetch_ad(self, user_country='ZA'):
        """Return ad with embed script"""
        return {
            'provider': 'propellerads',
            'ad_id': f'propellerads_{self.publisher_id}',
            'title': 'PropellerAds',
            'reward': 0.165,  # $1.65 eCPM / 10
            'is_embed': True,
            'embed_script': f'<script ...></script>',
            # ... other fields
        }
```

### Step 4: Integrate into AdManager
Update `adsterra_provider.py` AdManager class:

```python
self.providers = [
    AdsterraProvider(...),
    PropellerAdsProvider(...),  # NEW
    DemoAdProvider(...)
]
```

### Step 5: Test
1. Restart app: `python app.py`
2. Check startup logs for provider status
3. Click ads and verify they render

---

## Provider Integration Templates

### Template 1: Native Banner (Like Adsterra)
Best for: Simple embed scripts
```python
'embed_script': f'<script async src="//cdn.provider.com/script.js"></script>',
'embed_container': f'<div id="container-{script_id}"></div>'
```

### Template 2: Popunder/Smartlink
Best for: High CPM, link-based ads
```python
'embed_script': f'<script src="//cdn.provider.com/{script_id}.js"></script>',
'embed_container': ''  # No container needed
```

### Template 3: API-Based
Best for: Programmatic ad serving
```python
# Fetch ad from API
response = requests.get(f'https://api.provider.com/ad?publisher_id={self.publisher_id}')
ad_data = response.json()
return {'ad_url': ad_data['url'], ...}
```

---

## Recommended Addition Order

### Phase 1 (This Week) - Get CPM to $2+
1. **AdMaven** ($2.00 eCPM) - Works great with SA traffic
2. **PropellerAds** ($1.65 eCPM) - Similar to Adsterra

### Phase 2 (Next Week) - Add 3-4 more
3. **AppLixir** ($2.75 eCPM) - Highest eCPM
4. **Bidvertiser** ($1.65 eCPM) - Good fallback
5. **Clickadu** ($1.60 eCPM) - Easy integration

### Phase 3 (Week 3+) - Fill gaps
6. Adcash, HilltopAds, ExoClick, Infolinks

---

## Expected Revenue Impact

| Providers | Blended eCPM | Per 1K Ads | Per 100K Ads |
|-----------|--------------|-----------|--------------|
| Adsterra only | $1.65 | $165 | $16,500 |
| + AdMaven | $1.825 | $183 | $18,250 |
| + PropellerAds | $1.77 | $177 | $17,700 |
| + AppLixir | $2.01 | $201 | $20,100 |
| All 5 top | $1.95 | $195 | $19,500 |

---

## Common Issues & Fixes

### "Ad not showing"
- ✅ Check provider is enabled in `.env`
- ✅ Verify API credentials are correct
- ✅ Test ad unit in provider's dashboard
- ✅ Check browser console for script errors

### "Script won't load"
- ✅ Verify HTTPS/HTTP URL correctness
- ✅ Check CORS settings
- ✅ Ensure embed script ID matches

### "Low CPM from new provider"
- ✅ Give it 24-48 hours to gather data
- ✅ Check traffic quality (mature vs new)
- ✅ Verify targeting settings in provider dashboard

---

## File Structure
```
migpoint/
├── adsterra_provider.py          # Current (Adsterra only)
├── ad_providers_config.py        # NEW: Provider registry
├── providers/                    # NEW: Provider implementations
│   ├── __init__.py
│   ├── adsterra_provider.py      # Move here eventually
│   ├── propellerads_provider.py  # Add next
│   ├── admaven_provider.py       # Add after
│   └── ...
└── .env                          # Provider credentials
```

---

## Next Action

**Ready to add PropellerAds or AdMaven next?** Just provide their API credentials and I'll integrate them!
