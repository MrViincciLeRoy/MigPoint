# Clickadu Integration Guide

## Setup

1. **Get your Clickadu API Token:**
   - Go to Clickadu dashboard
   - Navigate to Settings → API
   - Copy your unique API token

2. **Configure in `config_clickadu.py`:**
   ```python
   API_TOKEN = 'your_actual_token_here'
   
   ZONES = {
       'dashboard_top': {
           'zone_id': 'your_zone_id',
           'name': 'Dashboard Top',
           'format': 'native',
           'ecpm': 0.008,
           'enabled': True
       }
   }
   ```

3. **Register blueprint in main app:**
   ```python
   from blueprints.clickadu_blueprint import clickadu_bp
   app.register_blueprint(clickadu_bp)
   ```

## Usage in Templates

### Display Clickadu Ad
```html
<div id="clickadu-zone-YOUR_ZONE_ID"></div>
<script src="https://bot.clickadu.com/display.js"></script>
<script>
    ClickaduDisplay.displayZone('YOUR_ZONE_ID');
</script>
```

### Get Ad Code via API
```javascript
fetch('/clickadu/ad/dashboard_top')
    .then(r => r.json())
    .then(data => {
        console.log('Clickadu ad ready', data);
    });
```

### Track Events
```javascript
// Track impression
fetch('/clickadu/track/impression', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        zone_id: 'YOUR_ZONE_ID',
        user_id: user.id
    })
});

// Track click
fetch('/clickadu/track/click', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        zone_id: 'YOUR_ZONE_ID',
        user_id: user.id
    })
});
```

## API Endpoints

- `GET /clickadu/ad/<placement>` - Get ad code
- `GET /clickadu/stats` - Get statistics
- `POST /clickadu/track/impression` - Track impression
- `POST /clickadu/track/click` - Track click
- `GET /clickadu/config` - Get configuration

## Ad Formats

- **Native Banner** - Responsive, high CTR
- **Banner 728x90** - Standard IAB format
- **Popunder** - Background window ads (if enabled)

## Supported Placements

- `dashboard_top` - Top of dashboard
- `dashboard_bottom` - Bottom of dashboard
- `watch_ad` - Watch ad page

## Stats Query Parameters

- `date_from` - Start date (YYYY-MM-DD)
- `date_to` - End date (YYYY-MM-DD)
- `group_by` - Group by: geo, day, hour, zone, site, platform, os_type, device_type
