"""
quick_start.py - One-command setup for Adsterra integration
Run this to get started quickly
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def check_requirements():
    """Check if all requirements are met"""
    print("\n" + "="*60)
    print("🔍 CHECKING REQUIREMENTS")
    print("="*60 + "\n")
    
    checks = []
    
    # Check Python version
    py_version = sys.version_info
    if py_version >= (3, 9):
        print(f"✓ Python {py_version.major}.{py_version.minor} (OK)")
        checks.append(True)
    else:
        print(f"✗ Python {py_version.major}.{py_version.minor} (Need 3.12+)")
        checks.append(False)
    
    # Check .env file
    if Path('.env').exists():
        print("✓ .env file exists")
        checks.append(True)
    else:
        print("✗ .env file not found")
        print("  → Copy .env.example to .env")
        checks.append(False)
    
    # Check required files
    required_files = [
        'config_adsterra.py',
        'adsterra_provider.py',
        'setup_adsterra.py',
        'models.py',
        'app.py'
    ]
    
    for file in required_files:
        if Path(file).exists():
            print(f"✓ {file}")
            checks.append(True)
        else:
            print(f"✗ {file} missing")
            checks.append(False)
    
    # Check environment variables
    if Path('.env').exists():
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = [
            'AIVEN_HOST',
            'AIVEN_DB',
            'AIVEN_USER',
            'AIVEN_PASSWORD'
        ]
        
        print("\nEnvironment variables:")
        for var in required_vars:
            if os.getenv(var):
                display = os.getenv(var) if var != 'AIVEN_PASSWORD' else '***'
                print(f"✓ {var}: {display}")
                checks.append(True)
            else:
                print(f"✗ {var}: NOT SET")
                checks.append(False)
        
        # Check Adsterra credentials
        adsterra_key = os.getenv('ADSTERRA_API_KEY','30893ff2c5bf97a2ae0ffbea44a32698')
        adsterra_pub = os.getenv('ADSTERRA_PUBLISHER_ID','27950195')
        
        if adsterra_key and adsterra_key != 'your_adsterra_api_key_here':
            print(f"✓ ADSTERRA_API_KEY: {adsterra_key[:10]}...")
            checks.append(True)
        else:
            print("⚠ ADSTERRA_API_KEY: Not configured (demo mode will be used)")
            checks.append(True)  # Not critical for initial testing
        
        if adsterra_pub and adsterra_pub != 'your_adsterra_publisher_id_here':
            print(f"✓ ADSTERRA_PUBLISHER_ID: {adsterra_pub}")
            checks.append(True)
        else:
            print("⚠ ADSTERRA_PUBLISHER_ID: Not configured (demo mode will be used)")
            checks.append(True)
    
    return all(checks)


def run_setup():
    """Run database setup"""
    print("\n" + "="*60)
    print("🗄️  SETTING UP DATABASE")
    print("="*60 + "\n")
    
    try:
        # Test connection first
        print("Testing database connection...")
        from models import get_db_connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT version()')
            version = cursor.fetchone()
            if version:
                version_str = version[0] if isinstance(version, tuple) else version.get('version', 'Unknown')
                print(f"✓ Connected: {str(version_str).split(',')[0]}")
            else:
                print("✓ Connected but no version info")
        
        # Run setup
        print("\nRunning Adsterra setup...")
        from setup_adsterra import setup_adsterra_integration
        setup_adsterra_integration()
        
        return True
        
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Check your database credentials in .env")
        print("  2. Ensure database is accessible")
        print("  3. Run: python testc.py")
        return False


def show_next_steps():
    """Show what to do next"""
    print("\n" + "="*60)
    print("🎯 NEXT STEPS")
    print("="*60 + "\n")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    adsterra_key = os.getenv('ADSTERRA_API_KEY')
    has_adsterra = adsterra_key and adsterra_key != 'your_adsterra_api_key_here'
    
    if has_adsterra:
        print("✓ Adsterra configured - You're ready to earn real revenue!")
        print("\n1. Start the app:")
        print("   python app.py")
        print("\n2. Open browser:")
        print("   http://localhost:5000")
        print("\n3. Log in with demo user:")
        print("   Phone: 0821234567")
        print("   Password: demo123")
        print("\n4. Watch ads and verify:")
        print("   - Ads load correctly")
        print("   - Rewards credited (2.1 MIGP per ad)")
        print("   - Cooldown works (5 minutes)")
    else:
        print("⚠ Adsterra not configured - Running in DEMO MODE")
        print("\nTo enable real ads:")
        print("1. Sign up at: https://publishers.adsterra.com/")
        print("2. Get your API Key and Publisher ID")
        print("3. Add to .env file:")
        print("   ADSTERRA_API_KEY=your_key_here")
        print("   ADSTERRA_PUBLISHER_ID=your_id_here")
        print("\nFor now, test with demo ads:")
        print("1. python app.py")
        print("2. Open: http://localhost:5000")
        print("3. Login: 0821234567 / demo123")
    
    print("\n" + "="*60)
    print("📚 DOCUMENTATION")
    print("="*60)
    print("\nSee ADSTERRA_GUIDE.md for complete instructions")
    print("="*60 + "\n")


def main():
    """Main setup routine"""
    print("\n" + "="*60)
    print("🚀 MIG POINTS - QUICK START")
    print("="*60)
    print("\nThis script will:")
    print("  1. Check requirements")
    print("  2. Set up database")
    print("  3. Configure Adsterra integration")
    print("  4. Show next steps")
    print("\n" + "="*60)
    
    input("\nPress ENTER to continue...")
    
    # Step 1: Check requirements
    if not check_requirements():
        print("\n" + "="*60)
        print("❌ REQUIREMENTS CHECK FAILED")
        print("="*60)
        print("\nPlease fix the issues above and run again.")
        print("="*60 + "\n")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ ALL REQUIREMENTS MET")
    print("="*60)
    
    # Step 2: Set up database
    setup_ok = run_setup()
    
    if not setup_ok:
        print("\n" + "="*60)
        print("❌ SETUP FAILED")
        print("="*60 + "\n")
        sys.exit(1)
    
    # Step 3: Show next steps
    show_next_steps()


if __name__ == '__main__':
    main()