"""
test_connection.py - Test Aiven PostgreSQL connection
Run this to verify your .env configuration is correct
"""

from dotenv import load_dotenv
import os
import psycopg2

print("\n" + "="*60)
print("🔧 TESTING AIVEN POSTGRESQL CONNECTION")
print("="*60 + "\n")

# Load .env
load_dotenv()
print("1. Loading .env file...")

# Check if .env exists
if not os.path.exists('.env'):
    print("   ❌ .env file not found!")
    print("   Create .env from .env.example and add your Aiven credentials")
    exit(1)
print("   ✓ .env file found")

# Check environment variables
print("\n2. Checking environment variables...")
required_vars = ['AIVEN_HOST', 'AIVEN_PORT', 'AIVEN_DB', 'AIVEN_USER', 'AIVEN_PASSWORD']
missing = []

for var in required_vars:
    value = os.getenv(var)
    if value:
        # Mask password
        display = value if var != 'AIVEN_PASSWORD' else '*' * len(value)
        print(f"   ✓ {var}: {display}")
    else:
        print(f"   ❌ {var}: NOT SET")
        missing.append(var)

if missing:
    print(f"\n❌ Missing variables: {', '.join(missing)}")
    print("\nAdd them to your .env file:")
    for var in missing:
        print(f"{var}=your-value-here")
    exit(1)

# Test connection
print("\n3. Testing database connection...")
try:
    conn = psycopg2.connect(
        host=os.getenv('AIVEN_HOST'),
        port=int(os.getenv('AIVEN_PORT', 5432)),
        database=os.getenv('AIVEN_DB'),
        user=os.getenv('AIVEN_USER'),
        password=os.getenv('AIVEN_PASSWORD'),
        sslmode='require',
        connect_timeout=10
    )
    print("   ✓ Connected successfully!")
    
    # Test query
    cursor = conn.cursor()
    cursor.execute('SELECT version();')
    version = cursor.fetchone()[0]
    print(f"   ✓ PostgreSQL version: {version.split(',')[0]}")
    
    # Check existing tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    
    if tables:
        print(f"\n   📊 Existing tables ({len(tables)}):")
        for table in tables:
            print(f"      - {table[0]}")
    else:
        print("\n   ℹ️  No tables yet (run init_db() to create them)")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*60)
    print("✅ CONNECTION TEST PASSED!")
    print("="*60)
    print("\nYou can now run: python app.py")
    print("="*60 + "\n")

except psycopg2.OperationalError as e:
    print(f"   ❌ Connection failed: {e}\n")
    print("Troubleshooting:")
    print("  1. Check your Aiven credentials are correct")
    print("  2. Verify your IP is whitelisted in Aiven console:")
    print("     → Go to your service → Overview → Allowed IP Addresses")
    print("     → Add your IP or use 0.0.0.0/0 (not recommended for production)")
    print("  3. Ensure SSL is enabled (Aiven requires it)")
    print("  4. Test with: psql -h HOST -p PORT -U USER -d DATABASE\n")
    print("="*60 + "\n")
    exit(1)

except Exception as e:
    print(f"   ❌ Unexpected error: {e}\n")
    exit(1)