# ============================================================
# enrollment.py — Enrollment Blueprint
# Handles: viewing pending enrollments, approve/reject, assign
# ============================================================

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required

enrollment = Blueprint('enrollment', __name__)


# --- Pending Enrollments ---
# Lists all enrollments with 'pending' status (paginated)
@enrollment.route('/pending')
@login_required
def pending():
    from app.models.enrollment import Enrollment
    page = request.args.get('page', 1, type=int)
    pending_list = Enrollment.query.filter_by(
        status='pending'
    ).paginate(page=page, per_page=20)
    return render_template('enrollment/pending.html', pending=pending_list)


# --- Approve Enrollment ---
# Sets enrollment status to 'enrolled' and records the date
@enrollment.route('/enrollment/<int:id>/approve', methods=['POST'])
@login_required
def approve(id):
    from app import db
    from app.models.enrollment import Enrollment
    from datetime import datetime

    enroll = Enrollment.query.get_or_404(id)
    enroll.status = 'enrolled'
    enroll.date_enrolled = datetime.utcnow()
    db.session.commit()
    flash('Student approved!', 'success')
    return redirect(url_for('enrollment.pending'))


# --- Reject Enrollment ---
# Sets enrollment status to 'rejected' and saves optional remarks
@enrollment.route('/enrollment/<int:id>/reject', methods=['POST'])
@login_required
def reject(id):
    from app import db
    from app.models.enrollment import Enrollment

    enroll = Enrollment.query.get_or_404(id)
    enroll.status = 'rejected'
    enroll.remarks = request.form.get('remarks', '')
    db.session.commit()
    flash('Student rejected.', 'error')
    return redirect(url_for('enrollment.pending'))


# --- Assign Strand & Section ---
# View for assigning strands and sections to enrollments
@enrollment.route('/assign')
@login_required
def assign():
    from app.models.strand import Strand
    from app.models.section import Section
    from app.models.enrollment import Enrollment

    strands     = Strand.query.filter_by(is_active=True).all()
    sections    = Section.query.filter_by(is_active=True).all()
    enrollments = Enrollment.query.all()

    return render_template('enrollment/assign.html',
        strands=strands,
        sections=sections,
        enrollments=enrollments
    )