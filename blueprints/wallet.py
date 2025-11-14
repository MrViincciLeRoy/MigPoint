from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import get_db, return_db

wallet_bp = Blueprint('wallet', __name__, url_prefix='/wallet')

# Conversion rates
AIRTIME_PACKAGES = [
    {'amount': 10, 'points': 100, 'type': 'airtime'},
    {'amount': 20, 'points': 200, 'type': 'airtime'},
    {'amount': 30, 'points': 300, 'type': 'airtime'},
    {'amount': 50, 'points': 500, 'type': 'airtime'},
    {'amount': 100, 'points': 1000, 'type': 'airtime'},
]

DATA_PACKAGES = [
    {'amount': '250MB', 'points': 50, 'type': 'data'},
    {'amount': '500MB', 'points': 90, 'type': 'data'},
    {'amount': '1GB', 'points': 150, 'type': 'data'},
    {'amount': '2GB', 'points': 280, 'type': 'data'},
    {'amount': '5GB', 'points': 650, 'type': 'data'},
    {'amount': '10GB', 'points': 1200, 'type': 'data'},
]

@wallet_bp.route('/')
@login_required
def index():
    conn = get_db()
    try:
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute('SELECT * FROM users WHERE id = %s', (current_user.id,))
        user = cursor.fetchone()
        
        # Get transactions
        cursor.execute("""
            SELECT * FROM transactions 
            WHERE user_id = %s 
            ORDER BY timestamp DESC 
            LIMIT 20
        """, (current_user.id,))
        transactions = cursor.fetchall()
        
        cursor.close()
        
        return render_template('wallet/wallet.html', 
                             user=user, 
                             transactions=transactions,
                             airtime_packages=AIRTIME_PACKAGES,
                             data_packages=DATA_PACKAGES)
    finally:
        return_db(conn)

@wallet_bp.route('/convert/airtime', methods=['POST'])
@login_required
def convert_airtime():
    amount = int(request.form.get('amount', 0))
    points_needed = amount * 10
    
    conn = get_db()
    try:
        cursor = conn.cursor()
        
        # Get user balance
        cursor.execute('SELECT * FROM users WHERE id = %s', (current_user.id,))
        user = cursor.fetchone()
        
        if user['balance'] >= points_needed:
            # Insert transaction
            cursor.execute("""
                INSERT INTO transactions (user_id, type, amount, description) 
                VALUES (%s, %s, %s, %s)
            """, (current_user.id, 'spend', points_needed, f'Airtime: R{amount}'))
            
            # Update balance
            cursor.execute("""
                UPDATE users SET balance = balance - %s WHERE id = %s
            """, (points_needed, current_user.id))
            
            conn.commit()
            flash(f'✅ R{amount} airtime sent to {user["phone"]}!', 'success')
        else:
            flash(f'❌ Insufficient balance. You need {points_needed} MIGP but only have {user["balance"]} MIGP', 'danger')
        
        cursor.close()
    except Exception as e:
        conn.rollback()
        print(f"Error in convert_airtime: {e}")
        flash('❌ Transaction failed. Please try again.', 'danger')
    finally:
        return_db(conn)
    
    return redirect(url_for('wallet.index'))

@wallet_bp.route('/convert/data', methods=['POST'])
@login_required
def convert_data():
    data_amount = request.form.get('data_amount', '')
    points_needed = int(request.form.get('points', 0))
    
    conn = get_db()
    try:
        cursor = conn.cursor()
        
        # Get user balance
        cursor.execute('SELECT * FROM users WHERE id = %s', (current_user.id,))
        user = cursor.fetchone()
        
        if user['balance'] >= points_needed:
            # Insert transaction
            cursor.execute("""
                INSERT INTO transactions (user_id, type, amount, description) 
                VALUES (%s, %s, %s, %s)
            """, (current_user.id, 'spend', points_needed, f'Data: {data_amount}'))
            
            # Update balance
            cursor.execute("""
                UPDATE users SET balance = balance - %s WHERE id = %s
            """, (points_needed, current_user.id))
            
            conn.commit()
            flash(f'✅ {data_amount} data sent to {user["phone"]}!', 'success')
        else:
            flash(f'❌ Insufficient balance. You need {points_needed} MIGP but only have {user["balance"]} MIGP', 'danger')
        
        cursor.close()
    except Exception as e:
        conn.rollback()
        print(f"Error in convert_data: {e}")
        flash('❌ Transaction failed. Please try again.', 'danger')
    finally:
        return_db(conn)
    
    return redirect(url_for('wallet.index'))
