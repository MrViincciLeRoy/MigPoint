from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import User, get_db_connection, convert_query, safe_row_access
from forms import LoginForm, RegisterForm
from datetime import datetime, date

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def check_daily_login_bonus(user_id, conn):
    """
    Check if user should get daily login bonus.
    Returns (should_award: bool, bonus_amount: int)
    """
    cursor = conn.cursor()
    
    # Get user's last login bonus
    cursor.execute(convert_query("""
        SELECT DATE(timestamp) as bonus_date
        FROM transactions
        WHERE user_id = %s 
        AND type = 'bonus'
        AND description LIKE 'Daily login bonus%%'
        ORDER BY timestamp DESC
        LIMIT 1
    """), (user_id,))
    
    last_bonus = cursor.fetchone()
    cursor.close()
    
    today = date.today()
    
    # No bonus record = first time login, give bonus
    if not last_bonus:
        return True, 10
    
    # Check if last bonus was today
    last_bonus_date = last_bonus['bonus_date']
    
    if last_bonus_date == today:
        # Already got bonus today
        return False, 0
    else:
        # New day, give bonus
        return True, 10


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    # Get demo users for display
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(convert_query('SELECT * FROM users'))
        demo_users = cursor.fetchall()
        cursor.close()
    
    if form.validate_on_submit():
        user = User.verify_password(form.phone.data, form.password.data)
        if user:
            login_user(user)
            
            # Check if user should get daily login bonus
            with get_db_connection() as conn:
                should_award, bonus_amount = check_daily_login_bonus(user.id, conn)
                
                if should_award:
                    cursor = conn.cursor()
                    cursor.execute(convert_query(
                        'INSERT INTO transactions (user_id, type, amount, description) VALUES (%s, %s, %s, %s)'),
                        (user.id, 'bonus', bonus_amount, 'Daily login bonus')
                    )
                    cursor.execute(convert_query('UPDATE users SET balance = balance + %s WHERE id = %s'), (bonus_amount, user.id))
                    conn.commit()
                    cursor.close()
                    flash(f'Welcome back! +{bonus_amount} MIGP daily bonus', 'success')
                else:
                    flash('Welcome back!', 'success')
            
            return redirect(request.args.get('next') or url_for('main.dashboard'))
        flash('Invalid credentials', 'danger')
    
    return render_template('auth/login.html', form=form, demo_users=demo_users)


@auth_bp.route('/quick-login/<phone>')
def quick_login(phone):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(convert_query('SELECT * FROM users WHERE phone = %s'), (phone,))
        user_data = cursor.fetchone()
        cursor.close()
        
        if user_data:
            user = User(
                safe_row_access(user_data, 'id', 0),
                safe_row_access(user_data, 'phone', 1),
                safe_row_access(user_data, 'name', 3),
                safe_row_access(user_data, 'is_admin', 4),
                safe_row_access(user_data, 'balance', 5)
            )
            login_user(user)
            
            # Check if user should get daily login bonus
            should_award, bonus_amount = check_daily_login_bonus(user.id, conn)
            
            if should_award:
                cursor = conn.cursor()
                cursor.execute(convert_query(
                    'INSERT INTO transactions (user_id, type, amount, description) VALUES (%s, %s, %s, %s)'),
                    (user.id, 'bonus', bonus_amount, 'Daily login bonus')
                )
                cursor.execute(convert_query('UPDATE users SET balance = balance + %s WHERE id = %s'), (bonus_amount, user.id))
                conn.commit()
                cursor.close()
                flash(f'Welcome back! +{bonus_amount} MIGP daily bonus', 'success')
            else:
                flash('Welcome back!', 'success')
            
            return redirect(url_for('main.dashboard'))
    
    flash('User not found', 'danger')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.create(form.phone.data, form.password.data, form.name.data)
        if user:
            login_user(user)
            
            # Give welcome bonus (bigger than daily login)
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(convert_query(
                    'INSERT INTO transactions (user_id, type, amount, description) VALUES (%s, %s, %s, %s)'),
                    (user.id, 'bonus', 50, 'Welcome bonus')
                )
                cursor.execute(convert_query('UPDATE users SET balance = balance + %s WHERE id = %s'), (50, user.id))
                conn.commit()
                cursor.close()
            
            flash('Welcome! +50 MIGP welcome bonus', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Phone already registered', 'danger')
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'info')
    return redirect(url_for('auth.login'))
