from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import get_db

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
    user = conn.execute('SELECT * FROM users WHERE id = ?', (current_user.id,)).fetchone()
    transactions = conn.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY timestamp DESC LIMIT 20", (current_user.id,)).fetchall()
    conn.close()
    return render_template('wallet/wallet.html', 
                         user=user, 
                         transactions=transactions,
                         airtime_packages=AIRTIME_PACKAGES,
                         data_packages=DATA_PACKAGES)

@wallet_bp.route('/convert/airtime', methods=['POST'])
@login_required
def convert_airtime():
    amount = int(request.form.get('amount', 0))
    points_needed = amount * 10
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (current_user.id,)).fetchone()
    
    if user['balance'] >= points_needed:
        conn.execute('INSERT INTO transactions (user_id, type, amount, description) VALUES (?, ?, ?, ?)',
                    (current_user.id, 'spend', points_needed, f'Airtime: R{amount}'))
        conn.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (points_needed, current_user.id))
        conn.commit()
        flash(f'✅ R{amount} airtime sent to {user["phone"]}!', 'success')
    else:
        flash(f'❌ Insufficient balance. You need {points_needed} MIGP but only have {user["balance"]} MIGP', 'danger')
    
    conn.close()
    return redirect(url_for('wallet.index'))

@wallet_bp.route('/convert/data', methods=['POST'])
@login_required
def convert_data():
    data_amount = request.form.get('data_amount', '')
    points_needed = int(request.form.get('points', 0))
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (current_user.id,)).fetchone()
    
    if user['balance'] >= points_needed:
        conn.execute('INSERT INTO transactions (user_id, type, amount, description) VALUES (?, ?, ?, ?)',
                    (current_user.id, 'spend', points_needed, f'Data: {data_amount}'))
        conn.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (points_needed, current_user.id))
        conn.commit()
        flash(f'✅ {data_amount} data sent to {user["phone"]}!', 'success')
    else:
        flash(f'❌ Insufficient balance. You need {points_needed} MIGP but only have {user["balance"]} MIGP', 'danger')
    
    conn.close()
    return redirect(url_for('wallet.index'))