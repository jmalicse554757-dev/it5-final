# ============================================================
# admin.py — Admin Blueprint
# Handles: user management, strands, sections, section students
# ============================================================

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

admin = Blueprint('admin_bp', __name__)


# --- Access Control Helper ---
# Blocks non-admin/staff users from accessing admin routes
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role not in ['admin', 'staff']:
            flash('You do not have permission to access that page.', 'error')
            if current_user.role == 'student':
                return redirect(url_for('students.portal'))
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated


# ---- USERS ----

# --- List Users ---
# Shows all users ordered by newest first
@admin.route('/admin/users')
@login_required
@admin_required
def users():
    from app.models.user import User
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


# --- Create User ---
# Admin only — creates a new staff/admin/student user account
@admin.route('/admin/users/create', methods=['POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        flash('Only admins can create users.', 'error')
        return redirect(url_for('admin_bp.users'))

    from app import db, bcrypt
    from app.models.user import User

    full_name = request.form.get('full_name', '').strip()
    username  = request.form.get('username', '').strip()
    password  = request.form.get('password', '')
    role      = request.form.get('role', '')

    # Validate all fields are filled
    if not full_name or not username or not password or not role:
        flash('Please fill in all fields.', 'error')
        return redirect(url_for('admin_bp.users'))

    if len(password) < 6:
        flash('Password must be at least 6 characters.', 'error')
        return redirect(url_for('admin_bp.users'))

    # Check for duplicate username
    if User.query.filter_by(username=username).first():
        flash('That username is already taken.', 'error')
        return redirect(url_for('admin_bp.users'))

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(
        full_name=full_name,
        username=username,
        password_hash=hashed_pw,
        role=role,
        active=True
    )
    db.session.add(new_user)
    db.session.commit()

    flash(f'{role.capitalize()} account for {full_name} created successfully.', 'success')
    return redirect(url_for('admin_bp.users'))


# --- Toggle User Active Status ---
# Admin only — activates or deactivates a user account
@admin.route('/admin/users/<int:user_id>/toggle', methods=['POST'])
@login_required
def toggle_user(user_id):
    if current_user.role != 'admin':
        flash('Only admins can do this.', 'error')
        return redirect(url_for('admin_bp.users'))

    from app import db
    from app.models.user import User

    user = User.query.get_or_404(user_id)

    # Prevent admin from deactivating their own account
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('admin_bp.users'))

    user.is_active = not user.is_active
    db.session.commit()

    status = 'activated' if user.is_active else 'deactivated'
    flash(f'{user.full_name} has been {status}.', 'success')
    return redirect(url_for('admin_bp.users'))


# ---- STRANDS ----

# --- List Strands ---
# Shows all strands ordered by code
@admin.route('/admin/strands')
@login_required
@admin_required
def strands():
    from app.models.strand import Strand
    all_strands = Strand.query.order_by(Strand.code).all()
    return render_template('admin/strands.html', strands=all_strands)


# --- Create Strand ---
# Adds a new academic strand (e.g. STEM, ABM, HUMSS)
@admin.route('/admin/strands/create', methods=['POST'])
@login_required
@admin_required
def create_strand():
    from app import db
    from app.models.strand import Strand

    code        = request.form.get('code', '').strip().upper()
    full_name   = request.form.get('full_name', '').strip()
    description = request.form.get('description', '').strip()

    if not code or not full_name:
        flash('Code and full name are required.', 'error')
        return redirect(url_for('admin_bp.strands'))

    # Block duplicate strand code
    if Strand.query.filter_by(code=code).first():
        flash(f'Strand {code} already exists.', 'error')
        return redirect(url_for('admin_bp.strands'))

    strand = Strand(code=code, full_name=full_name, description=description, is_active=True)
    db.session.add(strand)
    db.session.commit()

    flash(f'Strand {code} added successfully.', 'success')
    return redirect(url_for('admin_bp.strands'))


# --- Toggle Strand Active Status ---
# Activates or deactivates a strand
@admin.route('/admin/strands/<int:strand_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_strand(strand_id):
    from app import db
    from app.models.strand import Strand

    strand = Strand.query.get_or_404(strand_id)
    strand.is_active = not strand.is_active
    db.session.commit()

    status = 'activated' if strand.is_active else 'deactivated'
    flash(f'Strand {strand.code} has been {status}.', 'success')
    return redirect(url_for('admin_bp.strands'))


# ---- SECTIONS ----

# --- List Sections ---
# Shows all sections with their strands
@admin.route('/admin/sections')
@login_required
@admin_required
def sections():
    from app.models.section import Section
    from app.models.strand import Strand
    all_sections = Section.query.order_by(Section.grade_level, Section.name).all()
    all_strands  = Strand.query.filter_by(is_active=True).all()
    return render_template('admin/sections.html', sections=all_sections, strands=all_strands)


# --- Create Section ---
# Adds a new class section tied to a strand and grade level
@admin.route('/admin/sections/create', methods=['POST'])
@login_required
@admin_required
def create_section():
    from app import db
    from app.models.section import Section

    name        = request.form.get('name', '').strip()
    strand_id   = request.form.get('strand_id', '')
    grade_level = request.form.get('grade_level', '')
    school_year = request.form.get('school_year', '2024-2025')
    capacity    = request.form.get('capacity', 40)

    if not name or not strand_id or not grade_level:
        flash('All fields are required.', 'error')
        return redirect(url_for('admin_bp.sections'))

    section = Section(
        name=name,
        strand_id=int(strand_id),
        grade_level=grade_level,
        school_year=school_year,
        max_capacity=int(capacity),
        is_active=True
    )
    db.session.add(section)
    db.session.commit()

    flash(f'Section {name} added successfully.', 'success')
    return redirect(url_for('admin_bp.sections'))


# --- Delete Section ---
# Permanently removes a section
@admin.route('/admin/sections/<int:section_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_section(section_id):
    from app import db
    from app.models.section import Section

    section = Section.query.get_or_404(section_id)
    db.session.delete(section)
    db.session.commit()

    flash(f'Section {section.name} deleted.', 'success')
    return redirect(url_for('admin_bp.sections'))


# ---- SECTION STUDENTS VIEW ----

# --- Section Students ---
# Shows students grouped by section, with filters for strand/grade/year
@admin.route('/admin/section-students')
@login_required
@admin_required
def section_students():
    from app.models.section import Section
    from app.models.strand import Strand
    from app.models.enrollment import Enrollment
    from app.models.student import Student

    strands = Strand.query.filter_by(is_active=True).all()

    # Read filter params from URL
    selected_strand = request.args.get('strand_id', type=int)
    selected_grade  = request.args.get('grade_level', '')
    selected_year   = request.args.get('school_year', '')

    sections_query = Section.query

    # Apply filters if provided
    if selected_strand:
        sections_query = sections_query.filter_by(strand_id=selected_strand)
    if selected_grade:
        sections_query = sections_query.filter_by(grade_level=selected_grade)
    if selected_year:
        sections_query = sections_query.filter_by(school_year=selected_year)

    sections = sections_query.order_by(Section.grade_level, Section.name).all()

    # Build section data with enrollment counts
    section_data = []
    for section in sections:
        enrollments = Enrollment.query.filter_by(section_id=section.id).all()
        section_data.append({
            'section': section,
            'enrollments': enrollments,
            'count': len(enrollments)
        })

    return render_template(
        'admin/section_students.html',
        section_data=section_data,
        strands=strands,
        selected_strand=selected_strand,
        selected_grade=selected_grade,
        selected_year=selected_year
    )