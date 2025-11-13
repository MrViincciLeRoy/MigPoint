from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import User, get_db
from forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    conn = get_db()
    demo_users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    
    if form.validate_on_submit():
        user = User.verify_password(form.phone.data, form.password.data)
        if user:
            login_user(user)
            conn = get_db()
            conn.execute('INSERT INTO transactions (user_id, type, amount, description) VALUES (?, ?, ?, ?)',
                        (user.id, 'bonus', 10, 'Daily login bonus'))
            conn.execute('UPDATE users SET balance = balance + 10 WHERE id = ?', (user.id,))
            conn.commit()
            conn.close()
            flash('Welcome! +10 MIGP bonus', 'success')
            return redirect(request.args.get('next') or url_for('main.dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('auth/login.html', form=form, demo_users=demo_users)

@auth_bp.route('/quick-login/<phone>')
def quick_login(phone):
    conn = get_db()
    user_data = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()
    conn.close()
    if user_data:
        user = User(user_data['id'], user_data['phone'], user_data['name'], user_data['is_admin'], user_data['balance'])
        login_user(user)
        conn = get_db()
        conn.execute('INSERT INTO transactions (user_id, type, amount, description) VALUES (?, ?, ?, ?)',
                    (user.id, 'bonus', 10, 'Daily login bonus'))
        conn.execute('UPDATE users SET balance = balance + 10 WHERE id = ?', (user.id,))
        conn.commit()
        conn.close()
        flash('Welcome! +10 MIGP', 'success')
        return redirect(url_for('main.dashboard'))
    flash('User not found', 'danger')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.create(form.phone.data, form.password.data, form.name.data)
        if user:
            login_user(user)
            conn = get_db()
            conn.execute('INSERT INTO transactions (user_id, type, amount, description) VALUES (?, ?, ?, ?)',
                        (user.id, 'bonus', 50, 'Welcome bonus'))
            conn.execute('UPDATE users SET balance = balance + 50 WHERE id = ?', (user.id,))
            conn.commit()
            conn.close()
            flash('Welcome! +50 MIGP bonus', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Phone already registered', 'danger')
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'info')
    return redirect(url_for('auth.login'))