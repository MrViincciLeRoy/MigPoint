from flask import Flask, render_template_string
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Your Clickadu Zone IDs - Get these from your Clickadu dashboard
# Go to: Sites & Zones -> Add New Zone
ZONE_IDS = {
    'top_banner': os.getenv('ZONE_TOP_BANNER', 'YOUR_ZONE_ID_HERE'),
    'content_ad': os.getenv('ZONE_CONTENT', 'YOUR_ZONE_ID_HERE'),
    'bottom_banner': os.getenv('ZONE_BOTTOM', 'YOUR_ZONE_ID_HERE'),
    'popunder': os.getenv('ZONE_POPUNDER', 'YOUR_ZONE_ID_HERE'),
}

# Main page template with ads
HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }
        
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .content {
            padding: 30px;
        }
        
        .ad-container {
            margin: 30px 0;
            min-height: 100px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
        }
        
        .article {
            line-height: 1.8;
            color: #333;
            margin: 30px 0;
        }
        
        .article h2 {
            color: #667eea;
            margin: 25px 0 15px;
            font-size: 1.8em;
        }
        
        .article p {
            margin-bottom: 15px;
            font-size: 1.1em;
        }
        
        footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #dee2e6;
        }
        
        .setup-note {
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .setup-note h3 {
            color: #856404;
            margin-bottom: 10px;
        }
        
        .setup-note ol {
            margin-left: 20px;
            color: #856404;
        }.
        
        .setup-note li {
            margin: 8px 0;
        }
        
        .setup-note a {
            color: #856404;
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 {{ title }}</h1>
            <p>Your Ad-Powered Website</p>
        </header>
        
        <div class="content">
            {% if show_setup %}
            <div class="setup-note">
                <h3>⚠️ Setup Required</h3>
                <ol>
                    <li>Log in to <a href="https://publishers.clickadu.com" target="_blank">Clickadu Publishers</a></li>
                    <li>Go to <strong>Sites & Zones</strong> → <strong>Add New Zone</strong></li>
                    <li>Create zones for: Banner Ads, Popunder, etc.</li>
                    <li>Copy your Zone IDs (numbers like 123456)</li>
                    <li>Add them to your <code>.env</code> file or replace in the code</li>
                    <li>Restart the Flask app</li>
                </ol>
            </div>
            {% endif %}
            
            <!-- Top Banner Ad (728x90 or Responsive) -->
            <div class="ad-container">
                <script data-cfasync="false" type="text/javascript" 
                    src="//uugniwosinost.com/{{ zones.top_banner }}/invoke.js"></script>
                <div id="container-{{ zones.top_banner }}"></div>
            </div>
            
            <div class="article">
                <h2>Welcome to Your Website</h2>
                <p>
                    This is your ad-powered website using Clickadu. The ad spaces above and below 
                    will display real ads once you configure your zone IDs.
                </p>
                
                <p>
                    Start earning money from your website traffic by displaying relevant ads to your visitors.
                    Clickadu offers various ad formats including banners, popunders, push notifications, and more.
                </p>
                
                <h2>Why Clickadu?</h2>
                <p>
                    ✅ High CPM rates<br>
                    ✅ Global coverage<br>
                    ✅ Multiple ad formats<br>
                    ✅ Fast payments<br>
                    ✅ Real-time statistics
                </p>
            </div>
            
            <!-- Content Ad (300x250 or Responsive) -->
            <div class="ad-container">
                <script data-cfasync="false" type="text/javascript" 
                    src="//uugniwosinost.com/{{ zones.content_ad }}/invoke.js"></script>
                <div id="container-{{ zones.content_ad }}"></div>
            </div>
            
            <div class="article">
                <h2>Start Monetizing Today</h2>
                <p>
                    With Clickadu, you can start earning from your website traffic immediately. 
                    Simply add your zone IDs and watch your earnings grow.
                </p>
                
                <p>
                    The platform supports multiple payment methods and offers detailed analytics 
                    to help you optimize your ad placements for maximum revenue.
                </p>
            </div>
            
            <!-- Bottom Banner Ad -->
            <div class="ad-container">
                <script data-cfasync="false" type="text/javascript" 
                    src="//uugniwosinost.com/{{ zones.bottom_banner }}/invoke.js"></script>
                <div id="container-{{ zones.bottom_banner }}"></div>
            </div>
        </div>
        
        <footer>
            <p>&copy; 2025 Your Website | Powered by Clickadu</p>
        </footer>
    </div>
    
    <!-- Popunder Ad (Optional - triggers once per session) -->
    <script data-cfasync="false" type="text/javascript" 
        src="//uugniwosinost.com/{{ zones.popunder }}/invoke.js"></script>
</body>
</html>
"""


@app.route('/')
def home():
    """Homepage with Clickadu ads"""
    # Check if zones are configured
    show_setup = all(zone == 'YOUR_ZONE_ID_HERE' for zone in ZONE_IDS.values())
    
    return render_template_string(
        HOME_TEMPLATE,
        title="My Ad Website",
        zones=ZONE_IDS,
        show_setup=show_setup
    )


@app.route('/page/<int:page_num>')
def dynamic_page(page_num):
    """Dynamic pages with ads"""
    return render_template_string(
        HOME_TEMPLATE,
        title=f"Page {page_num}",
        zones=ZONE_IDS,
        show_setup=False
    )


@app.route('/debug')
def debug():
    """Debug endpoint to check configuration"""
    return {
        "status": "running",
        "zones_configured": {
            name: "✅ SET" if zone != 'YOUR_ZONE_ID_HERE' else "❌ NOT SET"
            for name, zone in ZONE_IDS.items()
        },
        "zones": ZONE_IDS,
        "clickadu_token_present": bool(os.getenv('clickadu_token')),
        "env_file_path": ".env in workspace root"
    }


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Clickadu Ad Server Starting...")
    print("=" * 60)
    print(f"\n📍 Visit: http://127.0.0.1:5000")
    print(f"\n⚙️  Current Zone IDs:")
    for name, zone_id in ZONE_IDS.items():
        status = "❌ NOT SET" if zone_id == 'YOUR_ZONE_ID_HERE' else f"✅ {zone_id}"
        print(f"   {name}: {status}")
    print("\n" + "=" * 60)
    
    app.run(debug=True)