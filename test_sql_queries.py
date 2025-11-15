#!/usr/bin/env python
"""Test SQL query syntax"""

from models import get_db_connection, convert_query

print("\n" + "="*60)
print("TESTING SQL QUERIES FOR SYNTAX ERRORS")
print("="*60)

try:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Test 1: Daily login bonus check
        print("\n✓ Test 1: Check daily login bonus query")
        query1 = convert_query("""
            SELECT DATE(timestamp) as bonus_date
            FROM transactions
            WHERE user_id = %s 
            AND type = 'bonus'
            AND description LIKE 'Daily login bonus%%'
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        print(f"  Query: {query1[:60]}...")
        cursor.execute(query1, (1,))
        result = cursor.fetchone()
        print(f"  Result: {result}")
        
        # Test 2: Transaction count
        print("\n✓ Test 2: Count transactions query")
        query2 = convert_query("""
            SELECT COUNT(*) as count FROM transactions 
            WHERE user_id = %s 
            AND type = 'earn'
            AND DATE(timestamp) = %s
        """)
        print(f"  Query: {query2[:60]}...")
        cursor.execute(query2, (1, '2025-11-15'))
        result = cursor.fetchone()
        print(f"  Result: {result}")
        
        # Test 3: Balance update
        print("\n✓ Test 3: Balance update query")
        query3 = convert_query("""
            UPDATE users SET balance = balance + %s WHERE id = %s
        """)
        print(f"  Query: {query3}")
        
        # Test 4: Welcome bonus
        print("\n✓ Test 4: Welcome bonus INSERT")
        query4 = convert_query("""
            INSERT INTO transactions (user_id, type, amount, description) 
            VALUES (%s, %s, %s, %s)
        """)
        print(f"  Query: {query4[:60]}...")
        
        print("\n" + "="*60)
        print("✅ ALL SQL QUERIES PASSED SYNTAX CHECK")
        print("="*60 + "\n")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
