# ============================================================
# routes/auth.py — Authentication Blueprint
# Handles: login, logout, signup, landing page, forgot password
# ============================================================

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

auth = Blueprint('auth', __name__)


# --- Landing Page ---
# Redirects to the landing/home page
@auth.route('/')
def index():
    return render_template('landing.html')


# --- Login ---
# Shows login form and authenticates user
# Redirects students to portal, others to dashboard
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'student':
            return redirect(url_for('students.portal'))
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        from app import bcrypt
        from app.models.user import User

        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'Welcome back, {user.full_name}!', 'success')
            if current_user.role == 'student':
                return redirect(url_for('students.portal'))
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('auth/login.html')


# --- Logout ---
# Logs out the current user and redirects to login
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))


# --- Signup ---
# Handles new student self-registration
# Creates both a User account and a linked Student record
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        if current_user.role == 'student':
            return redirect(url_for('students.portal'))
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        from app import db, bcrypt
        from app.models.user import User
        from app.models.student import Student

        full_name      = request.form.get('full_name', '').strip()
        username       = request.form.get('username', '').strip()
        password       = request.form.get('password', '')
        confirm        = request.form.get('confirm_password', '')
        lrn            = request.form.get('lrn', '').strip()
        first_name     = request.form.get('first_name', '').strip()
        last_name      = request.form.get('last_name', '').strip()
        middle_name    = request.form.get('middle_name', '').strip()
        contact_number = request.form.get('contact_number', '').strip()

        if not all([full_name, username, password, lrn, first_name, last_name]):
            flash('Please fill in all required fields.', 'error')
            return render_template('auth/signup.html')

        if len(username) < 3:
            flash('Username must be at least 3 characters.', 'error')
            return render_template('auth/signup.html')

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('auth/signup.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('auth/signup.html')

        if len(lrn) != 12 or not lrn.isdigit():
            flash('LRN must be exactly 12 digits.', 'error')
            return render_template('auth/signup.html')

        if User.query.filter_by(username=username).first():
            flash('That username is already taken.', 'error')
            return render_template('auth/signup.html')

        if Student.query.filter_by(lrn=lrn).first():
            flash('An account with that LRN already exists.', 'error')
            return render_template('auth/signup.html')

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            full_name=full_name,
            username=username,
            password_hash=hashed_pw,
            role='student',
            is_active=True
        )
        db.session.add(new_user)
        db.session.flush()

        new_student = Student(
            lrn=lrn,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name or None,
            contact_number=contact_number or None,
            user_id=new_user.id
        )
        db.session.add(new_student)

        try:
            db.session.commit()
            flash('Account created successfully. You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception:
            db.session.rollback()
            flash('Something went wrong. Please try again.', 'error')

    return render_template('auth/signup.html')


# --- Forgot Password ---
# Lets a student reset their password using their LRN as verification
# No email needed — LRN acts as the identity check since this is a school system
@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        from app import db, bcrypt
        from app.models.user import User
        from app.models.student import Student

        username     = request.form.get('username', '').strip()
        lrn          = request.form.get('lrn', '').strip()
        new_password = request.form.get('new_password', '')
        confirm      = request.form.get('confirm_password', '')

        # Validate inputs
        if not username or not lrn or not new_password:
            flash('Please fill in all fields.', 'error')
            return render_template('auth/forgot_password.html')

        if len(lrn) != 12 or not lrn.isdigit():
            flash('LRN must be exactly 12 digits.', 'error')
            return render_template('auth/forgot_password.html')

        if new_password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('auth/forgot_password.html')

        if len(new_password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('auth/forgot_password.html')

        # Find the user by username
        user = User.query.filter_by(username=username).first()
        if not user:
            # Intentionally vague — do not reveal if username exists
            flash('No matching account found. Check your username and LRN.', 'error')
            return render_template('auth/forgot_password.html')

        # Verify that the LRN matches the linked student record
        student = Student.query.filter_by(user_id=user.id, lrn=lrn).first()
        if not student:
            flash('No matching account found. Check your username and LRN.', 'error')
            return render_template('auth/forgot_password.html')

        # Update the password
        user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()

        flash('Password updated successfully. You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')