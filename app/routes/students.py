# ============================================================
# students.py — Students Blueprint
# Handles: CRUD for student records, search, portal, enrollment
# ============================================================

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

students = Blueprint('students', __name__)


# ─────────────────────────────────────────────
# READ — Records page
# Lists all students with pagination (20 per page)
# ─────────────────────────────────────────────
@students.route('/students')
@login_required
def records():
    from app.models.student import Student
    from app.models.strand import Strand

    page = request.args.get('page', 1, type=int)
    students_list = Student.query.paginate(page=page, per_page=20)
    strands = Strand.query.filter_by(is_active=True).all()

    return render_template('students/records.html',
        students=students_list,
        strands=strands
    )


# ─────────────────────────────────────────────
# CREATE — Add student
# Admin/staff only — adds student + creates enrollment record
# ─────────────────────────────────────────────
@students.route('/students/add', methods=['GET', 'POST'])
@login_required
def add():
    from app import db
    from app.models.student import Student
    from app.models.enrollment import Enrollment
    from app.models.strand import Strand
    from app.models.section import Section

    if current_user.role not in ['admin', 'staff']:
        abort(403)

    strands  = Strand.query.filter_by(is_active=True).all()
    sections = Section.query.filter_by(is_active=True).all()

    if request.method == 'POST':
        # Block duplicate LRN
        existing = Student.query.filter_by(lrn=request.form.get('lrn')).first()
        if existing:
            flash('LRN already exists!', 'error')
            return render_template('students/add.html', strands=strands, sections=sections)

        # Create student record
        student = Student(
            lrn=request.form.get('lrn'),
            last_name=request.form.get('last_name'),
            first_name=request.form.get('first_name'),
            middle_name=request.form.get('middle_name'),
            suffix=request.form.get('suffix'),
            date_of_birth=request.form.get('date_of_birth') or None,
            sex=request.form.get('sex'),
            contact_number=request.form.get('contact_number'),
            email=request.form.get('email'),
            address=request.form.get('address'),
            guardian_name=request.form.get('guardian_name'),
            guardian_relationship=request.form.get('guardian_relationship'),
            guardian_contact=request.form.get('guardian_contact'),
            guardian_occupation=request.form.get('guardian_occupation')
        )
        db.session.add(student)
        db.session.flush()  # Get student.id before committing

        # Create linked enrollment record
        strand_id  = request.form.get('strand_id')
        section_id = request.form.get('section_id')
        enrollment = Enrollment(
            student_id=student.id,
            strand_id=int(strand_id) if strand_id else None,
            section_id=int(section_id) if section_id else None,
            school_year='2024-2025',
            status='pending'
        )
        db.session.add(enrollment)
        db.session.commit()

        flash('Student enrolled successfully!', 'success')
        return redirect(url_for('students.records'))

    return render_template('students/add.html', strands=strands, sections=sections)


# ─────────────────────────────────────────────
# UPDATE — Edit student
# Admin/staff only — updates student info and enrollment
# ─────────────────────────────────────────────
@students.route('/students/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    from app import db
    from app.models.student import Student
    from app.models.enrollment import Enrollment
    from app.models.strand import Strand
    from app.models.section import Section

    if current_user.role not in ['admin', 'staff']:
        abort(403)

    student    = Student.query.get_or_404(id)
    enrollment = Enrollment.query.filter_by(
        student_id=id
    ).order_by(Enrollment.date_applied.desc()).first()
    strands    = Strand.query.filter_by(is_active=True).all()
    sections   = Section.query.filter_by(is_active=True).all()

    if request.method == 'POST':
        # Update student fields
        student.last_name             = request.form.get('last_name')
        student.first_name            = request.form.get('first_name')
        student.middle_name           = request.form.get('middle_name')
        student.suffix                = request.form.get('suffix')
        student.date_of_birth         = request.form.get('date_of_birth') or None
        student.sex                   = request.form.get('sex')
        student.contact_number        = request.form.get('contact_number')
        student.email                 = request.form.get('email')
        student.address               = request.form.get('address')
        student.guardian_name         = request.form.get('guardian_name')
        student.guardian_relationship = request.form.get('guardian_relationship')
        student.guardian_contact      = request.form.get('guardian_contact')
        student.guardian_occupation   = request.form.get('guardian_occupation')

        # Update strand/section if enrollment exists
        if enrollment:
            strand_id  = request.form.get('strand_id')
            section_id = request.form.get('section_id')
            if strand_id:
                enrollment.strand_id  = int(strand_id)
            if section_id:
                enrollment.section_id = int(section_id)
        else:
            flash('No enrollment record found — strand/section not updated.', 'error')

        db.session.commit()
        flash(f"{student.first_name}'s record updated successfully!", 'success')
        return redirect(url_for('students.records'))

    return render_template('students/edit.html',
        student=student,
        enrollment=enrollment,
        strands=strands,
        sections=sections
    )


# ─────────────────────────────────────────────
# DELETE — Remove student
# Admin/staff only — deletes student and all their enrollments
# ─────────────────────────────────────────────
@students.route('/students/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    from app import db
    from app.models.student import Student
    from app.models.enrollment import Enrollment

    if current_user.role not in ['admin', 'staff']:
        abort(403)

    student = Student.query.get_or_404(id)
    Enrollment.query.filter_by(student_id=id).delete()  # Remove enrollments first
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted!', 'success')
    return redirect(url_for('students.records'))


# ─────────────────────────────────────────────
# SEARCH — Search students
# Filter by name/LRN, strand, and enrollment status
# ─────────────────────────────────────────────
@students.route('/students/search')
@login_required
def search():
    from app import db
    from app.models.strand import Strand
    from app.models.student import Student
    from app.models.enrollment import Enrollment

    strands = Strand.query.filter_by(is_active=True).all()

    q               = request.args.get('q', '').strip()
    selected_strand = request.args.get('strand', '')
    selected_status = request.args.get('status', '')

    results = None

    if q or selected_strand or selected_status:
        query = Student.query

        # Search by name or LRN
        if q:
            query = query.filter(
                db.or_(
                    Student.first_name.ilike(f'%{q}%'),
                    Student.last_name.ilike(f'%{q}%'),
                    Student.lrn.ilike(f'%{q}%')
                )
            )

        # Filter by strand or status (joins enrollment table)
        if selected_strand or selected_status:
            query = query.join(Enrollment, Enrollment.student_id == Student.id)
            if selected_strand:
                query = query.filter(Enrollment.strand_id == selected_strand)
            if selected_status:
                query = query.filter(Enrollment.status == selected_status)

        results = query.all()

    return render_template('students/search.html',
        strands=strands,
        results=results,
        query=q,
        selected_strand=selected_strand,
        selected_status=selected_status
    )


# ─────────────────────────────────────────────
# MY PROFILE — Student views their own profile
# ─────────────────────────────────────────────
@students.route('/students/my-profile')
@login_required
def my_profile():
    return render_template('students/profile.html')


# ─────────────────────────────────────────────
# PORTAL — Student homepage after login
# Shows student info and their latest enrollment status
# ─────────────────────────────────────────────
@students.route('/portal')
@login_required
def portal():
    from app.models.student import Student
    from app.models.enrollment import Enrollment

    # Only students can access the portal
    if current_user.role != 'student':
        return redirect(url_for('dashboard.index'))

    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash('No student record linked to your account.', 'error')
        return redirect(url_for('auth.login'))

    # Get the most recent enrollment record
    enrollment = Enrollment.query.filter_by(
        student_id=student.id
    ).order_by(Enrollment.date_applied.desc()).first()

    return render_template('students/portal.html',
        student=student,
        enrollment=enrollment
    )


# ─────────────────────────────────────────────
# ENROLL — Student self-enrollment form
# Students pick their strand and section
# ─────────────────────────────────────────────
@students.route('/enroll', methods=['GET', 'POST'])
@login_required
def enroll():
    from app import db
    from app.models.student import Student
    from app.models.strand import Strand
    from app.models.section import Section
    from app.models.enrollment import Enrollment

    # Only students can enroll themselves
    if current_user.role != 'student':
        return redirect(url_for('dashboard.index'))

    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash('No student record linked to your account.', 'error')
        return redirect(url_for('auth.login'))

    # Block duplicate enrollment
    existing = Enrollment.query.filter_by(student_id=student.id).first()
    if existing:
        flash('You already have an enrollment record.', 'error')
        return redirect(url_for('students.portal'))

    strands  = Strand.query.filter_by(is_active=True).all()
    sections = Section.query.filter_by(is_active=True).all()

    if request.method == 'POST':
        strand_id  = request.form.get('strand_id')
        section_id = request.form.get('section_id')

        # Both strand and section are required
        if not strand_id or not section_id:
            flash('Please select both a strand and section.', 'error')
            return render_template('students/enroll.html',
                strands=strands, sections=sections, student=student)

        # Check if the section is already full
        section = Section.query.get(section_id)
        if section and section.is_full():
            flash('That section is already full. Please choose another.', 'error')
            return render_template('students/enroll.html',
                strands=strands, sections=sections, student=student)

        # Submit enrollment as pending
        enrollment = Enrollment(
            student_id=student.id,
            strand_id=int(strand_id) if strand_id else None,
            section_id=int(section_id) if section_id else None,
            school_year='2024-2025',
            status='pending'
        )
        db.session.add(enrollment)
        db.session.commit()

        flash('Enrollment submitted! Please wait for staff confirmation.', 'success')
        return redirect(url_for('students.portal'))

    return render_template('students/enroll.html',
        strands=strands, sections=sections, student=student)