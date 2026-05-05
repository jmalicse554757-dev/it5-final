from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

auth = Blueprint('auth', __name__)

@auth.route('/')
def index():
    return render_template('landing.html')

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

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

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

        full_name        = request.form.get('full_name', '').strip()
        username         = request.form.get('username', '').strip()
        password         = request.form.get('password', '')
        confirm          = request.form.get('confirm_password', '')
        lrn              = request.form.get('lrn', '').strip()
        first_name       = request.form.get('first_name', '').strip()
        last_name        = request.form.get('last_name', '').strip()
        middle_name      = request.form.get('middle_name', '').strip()
        contact_number   = request.form.get('contact_number', '').strip()

        # Basic validation
        if not all([full_name, username, password, lrn, first_name, last_name]):
            flash('Please fill in all required fields.', 'error')
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

        # Create user account
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
        full_name=full_name,
        username=username,
        password_hash=hashed_pw,
        role='student',
        active=True  
)
        db.session.add(new_user)
        db.session.flush()

        # Auto-create student record
        new_student = Student(
            lrn=lrn,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name or None,
            contact_number=contact_number or None,
            user_id=new_user.id
        )
        db.session.add(new_student)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/signup.html')