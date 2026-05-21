# ============================================================
# routes/enrollment.py — Enrollment Blueprint
# Handles: viewing pending enrollments, approve/reject, assign
# ============================================================

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

enrollment = Blueprint('enrollment', __name__)


# --- Pending Enrollments ---
# Lists all enrollments with 'pending' status (paginated)
# Admin/staff only
@enrollment.route('/pending')
@login_required
def pending():
    from app.models.enrollment import Enrollment

    if current_user.role not in ['admin', 'staff']:
        abort(403)

    page = request.args.get('page', 1, type=int)
    enrollments = Enrollment.query.filter_by(
        status='pending'
    ).paginate(page=page, per_page=20)
    return render_template('enrollment/pending.html', enrollments=enrollments)


# --- Approve Enrollment ---
# Sets status to 'enrolled', records date and which staff approved
# Logs the action to the activity log
@enrollment.route('/enrollment/<int:id>/approve', methods=['POST'])
@login_required
def approve(id):
    from app import db
    from app.models.enrollment import Enrollment
    from app.utils import log_action
    from datetime import datetime

    if current_user.role not in ['admin', 'staff']:
        abort(403)

    enroll = Enrollment.query.get_or_404(id)
    enroll.status        = 'enrolled'
    enroll.date_enrolled = datetime.utcnow()
    enroll.enrolled_by   = current_user.id

    # Log before commit so it's in the same transaction
    log_action(
        user_id=current_user.id,
        action='approved enrollment',
        detail=f'Student: {enroll.student.get_full_name()} (LRN: {enroll.student.lrn})',
        ip=request.remote_addr
    )

    db.session.commit()
    flash('Student approved!', 'success')
    return redirect(url_for('enrollment.pending'))


# --- Reject Enrollment ---
# Sets status to 'rejected', saves optional remarks
# Logs the action to the activity log
@enrollment.route('/enrollment/<int:id>/reject', methods=['POST'])
@login_required
def reject(id):
    from app import db
    from app.models.enrollment import Enrollment
    from app.utils import log_action

    if current_user.role not in ['admin', 'staff']:
        abort(403)

    enroll = Enrollment.query.get_or_404(id)
    enroll.status  = 'rejected'
    enroll.remarks = request.form.get('remarks', '')

    # Log the rejection with the reason if one was given
    log_action(
        user_id=current_user.id,
        action='rejected enrollment',
        detail=f'Student: {enroll.student.get_full_name()} (LRN: {enroll.student.lrn})',
        ip=request.remote_addr
    )

    db.session.commit()
    flash('Student rejected.', 'error')
    return redirect(url_for('enrollment.pending'))


# --- Assign Strand & Section (view) ---
# Shows the assignment page with all strands, sections, and enrollments
# Admin/staff only
@enrollment.route('/assign')
@login_required
def assign():
    from app.models.strand import Strand
    from app.models.section import Section
    from app.models.enrollment import Enrollment

    if current_user.role not in ['admin', 'staff']:
        abort(403)

    strands     = Strand.query.filter_by(is_active=True).all()
    sections    = Section.query.filter_by(is_active=True).all()
    enrollments = Enrollment.query.all()

    return render_template('enrollment/assign.html',
        strands=strands,
        sections=sections,
        enrollments=enrollments
    )


# --- Save Strand & Section Assignment (POST) ---
# Updates an enrollment's strand and section
# Logs the assignment to the activity log
@enrollment.route('/enrollment/assign/<int:id>', methods=['POST'])
@login_required
def save_assign(id):
    from app import db
    from app.models.enrollment import Enrollment
    from app.utils import log_action

    if current_user.role not in ['admin', 'staff']:
        abort(403)

    enroll = Enrollment.query.get_or_404(id)

    strand_id  = request.form.get('strand_id')
    section_id = request.form.get('section_id')

    if strand_id:
        enroll.strand_id  = int(strand_id)
    if section_id:
        enroll.section_id = int(section_id)

    log_action(
        user_id=current_user.id,
        action='assigned strand/section',
        detail=f'Enrollment ID: {enroll.id} — Student: {enroll.student.get_full_name()}',
        ip=request.remote_addr
    )

    db.session.commit()
    flash('Assignment saved!', 'success')
    return redirect(url_for('enrollment.assign'))


# --- Bulk Approve ---
# Approves multiple selected enrollments at once
# Logs a single summary entry covering all approved students
@enrollment.route('/enrollment/bulk-approve', methods=['POST'])
@login_required
def bulk_approve():
    from app import db
    from app.models.enrollment import Enrollment
    from app.utils import log_action
    from datetime import datetime

    if current_user.role not in ['admin', 'staff']:
        abort(403)

    ids = request.form.getlist('enrollment_ids')
    if not ids:
        flash('No students selected.', 'error')
        return redirect(url_for('enrollment.pending'))

    count = 0
    names = []
    for eid in ids:
        enroll = Enrollment.query.get(int(eid))
        if enroll and enroll.status == 'pending':
            enroll.status        = 'enrolled'
            enroll.date_enrolled = datetime.utcnow()
            enroll.enrolled_by   = current_user.id
            names.append(enroll.student.get_full_name())
            count += 1

    # Log one entry summarizing how many were bulk approved
    if count > 0:
        log_action(
            user_id=current_user.id,
            action='bulk approved enrollments',
            detail=f'{count} student(s) approved: {", ".join(names[:3])}{"..." if len(names) > 3 else ""}',
            ip=request.remote_addr
        )

    db.session.commit()
    flash(f'{count} student{"s" if count != 1 else ""} approved successfully!', 'success')
    return redirect(url_for('enrollment.pending'))