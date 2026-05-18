from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

students = Blueprint('students', __name__)


# ─────────────────────────────────────────────
# READ — Records page
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

    strands = Strand.query.filter_by(is_active=True).all()
    sections = Section.query.filter_by(is_active=True).all()

    if request.method == 'POST':
        existing = Student.query.filter_by(
            lrn=request.form.get('lrn')
        ).first()

        if existing:
            flash('LRN already exists!', 'error')
            return render_template('students/add.html',
                strands=strands,
                sections=sections
            )

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
        db.session.flush()

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

    return render_template('students/add.html',
        strands=strands,
        sections=sections
    )


# ─────────────────────────────────────────────
# UPDATE — Edit student
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

    student = Student.query.get_or_404(id)
    enrollment = Enrollment.query.filter_by(
        student_id=id
    ).order_by(Enrollment.date_applied.desc()).first()
    strands = Strand.query.filter_by(is_active=True).all()
    sections = Section.query.filter_by(is_active=True).all()

    if request.method == 'POST':
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
    Enrollment.query.filter_by(student_id=id).delete()
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted!', 'success')
    return redirect(url_for('students.records'))


# ─────────────────────────────────────────────
# SEARCH — Search students
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

        if q:
            query = query.filter(
                db.or_(
                    Student.first_name.ilike(f'%{q}%'),
                    Student.last_name.ilike(f'%{q}%'),
                    Student.lrn.ilike(f'%{q}%')
                )
            )

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
# STUDENT PORTAL — Student views own profile
# ─────────────────────────────────────────────

@students.route('/students/my-profile')
@login_required
def my_profile():
    return render_template('students/profile.html')


@students.route('/portal')
@login_required
def portal():
    from app.models.student import Student
    from app.models.enrollment import Enrollment

    if current_user.role != 'student':
        return redirect(url_for('dashboard.index'))

    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash('No student record linked to your account.', 'error')
        return redirect(url_for('auth.login'))

    enrollment = Enrollment.query.filter_by(
        student_id=student.id
    ).order_by(Enrollment.date_applied.desc()).first()

    return render_template('students/portal.html',
        student=student,
        enrollment=enrollment
    )


# ─────────────────────────────────────────────
# ENROLL — Student self-enrollment
# ─────────────────────────────────────────────

@students.route('/enroll', methods=['GET', 'POST'])
@login_required
def enroll():
    from app import db
    from app.models.student import Student
    from app.models.strand import Strand
    from app.models.section import Section
    from app.models.enrollment import Enrollment

    if current_user.role != 'student':
        return redirect(url_for('dashboard.index'))

    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash('No student record linked to your account.', 'error')
        return redirect(url_for('auth.login'))

    existing = Enrollment.query.filter_by(student_id=student.id).first()
    if existing:
        flash('You already have an enrollment record.', 'error')
        return redirect(url_for('students.portal'))

    strands  = Strand.query.filter_by(is_active=True).all()
    sections = Section.query.filter_by(is_active=True).all()

    if request.method == 'POST':
        strand_id  = request.form.get('strand_id')
        section_id = request.form.get('section_id')

        if not strand_id or not section_id:
            flash('Please select both a strand and section.', 'error')
            return render_template('students/enroll.html',
                strands=strands,
                sections=sections,
                student=student
            )

        section = Section.query.get(section_id)
        if section and section.is_full():
            flash('That section is already full. Please choose another.', 'error')
            return render_template('students/enroll.html',
                strands=strands,
                sections=sections,
                student=student
            )

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
        strands=strands,
        sections=sections,
        student=student
    )
