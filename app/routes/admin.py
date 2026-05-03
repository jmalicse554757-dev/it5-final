from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

admin = Blueprint('admin_bp', __name__)

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

@admin.route('/admin/users')
@login_required
@admin_required
def users():
    from app.models.user import User
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)

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

    if not full_name or not username or not password or not role:
        flash('Please fill in all fields.', 'error')
        return redirect(url_for('admin_bp.users'))

    if len(password) < 6:
        flash('Password must be at least 6 characters.', 'error')
        return redirect(url_for('admin_bp.users'))

    if User.query.filter_by(username=username).first():
        flash('That username is already taken.', 'error')
        return redirect(url_for('admin_bp.users'))

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(
        full_name=full_name,
        username=username,
        password_hash=hashed_pw,
        role=role,
        is_active=True
    )
    db.session.add(new_user)
    db.session.commit()

    flash(f'{role.capitalize()} account for {full_name} created successfully.', 'success')
    return redirect(url_for('admin_bp.users'))

@admin.route('/admin/users/<int:user_id>/toggle', methods=['POST'])
@login_required
def toggle_user(user_id):
    if current_user.role != 'admin':
        flash('Only admins can do this.', 'error')
        return redirect(url_for('admin_bp.users'))

    from app import db
    from app.models.user import User

    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('admin_bp.users'))

    user.active = not user.active
    db.session.commit()

    status = 'activated' if user.active else 'deactivated'
    flash(f'{user.full_name} has been {status}.', 'success')
    return redirect(url_for('admin_bp.users'))

# ---- STRANDS ----

@admin.route('/admin/strands')
@login_required
@admin_required
def strands():
    from app.models.strand import Strand
    all_strands = Strand.query.order_by(Strand.code).all()
    return render_template('admin/strands.html', strands=all_strands)

@admin.route('/admin/strands/create', methods=['POST'])
@login_required
@admin_required
def create_strand():
    from app import db
    from app.models.strand import Strand

    code      = request.form.get('code', '').strip().upper()
    full_name = request.form.get('full_name', '').strip()
    description = request.form.get('description', '').strip()

    if not code or not full_name:
        flash('Code and full name are required.', 'error')
        return redirect(url_for('admin_bp.strands'))

    if Strand.query.filter_by(code=code).first():
        flash(f'Strand {code} already exists.', 'error')
        return redirect(url_for('admin_bp.strands'))

    strand = Strand(code=code, full_name=full_name, description=description, is_active=True)
    db.session.add(strand)
    db.session.commit()

    flash(f'Strand {code} added successfully.', 'success')
    return redirect(url_for('admin_bp.strands'))

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

@admin.route('/admin/sections')
@login_required
@admin_required
def sections():
    from app.models.section import Section
    from app.models.strand import Strand
    all_sections = Section.query.order_by(Section.grade_level, Section.name).all()
    all_strands  = Strand.query.filter_by(is_active=True).all()
    return render_template('admin/sections.html', sections=all_sections, strands=all_strands)

@admin.route('/admin/sections/create', methods=['POST'])
@login_required
@admin_required
def create_section():
    from app import db
    from app.models.section import Section

    name        = request.form.get('name', '').strip()
    strand_id   = request.form.get('strand_id', '')
    grade_level = request.form.get('grade_level', '')
    capacity    = request.form.get('capacity', 40)

    if not name or not strand_id or not grade_level:
        flash('All fields are required.', 'error')
        return redirect(url_for('admin_bp.sections'))

    section = Section(
        name=name,
        strand_id=int(strand_id),
        grade_level=int(grade_level),
        capacity=int(capacity)
    )
    db.session.add(section)
    db.session.commit()

    flash(f'Section {name} added successfully.', 'success')
    return redirect(url_for('admin_bp.sections'))

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