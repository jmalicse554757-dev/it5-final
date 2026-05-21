# ============================================================
# dashboard.py — Dashboard Blueprint
# Handles: main dashboard with enrollment stats and summaries
# ============================================================

from flask import Blueprint, render_template
from flask_login import login_required

dashboard = Blueprint('dashboard', __name__)


# --- Main Dashboard ---
# Displays enrollment counts, capacity, strand breakdown,
# and the 5 most recently enrolled students
@dashboard.route('/dashboard')
@login_required
def index():
    from app.models.enrollment import Enrollment
    from app.models.strand import Strand
    from app.models.section import Section

    # Count enrolled and pending students
    total_enrolled = Enrollment.query.filter_by(status='enrolled').count()
    total_pending  = Enrollment.query.filter_by(status='pending').count()
    total_sections = Section.query.filter_by(is_active=True).count()

    # Calculate remaining slots across all active sections
    sections = Section.query.filter_by(is_active=True).all()
    total_capacity  = sum(s.max_capacity for s in sections)
    slots_remaining = total_capacity - total_enrolled

    # Build per-strand enrollment breakdown
    strands = Strand.query.filter_by(is_active=True).all()
    strand_data = []
    for strand in strands:
        count = Enrollment.query.filter_by(
            strand_id=strand.id,
            status='enrolled'
        ).count()
        strand_data.append({
            'code': strand.code,
            'full_name': strand.full_name,
            'count': count
        })

    # Get 5 most recently enrolled students
    recent = Enrollment.query.filter_by(
        status='enrolled'
    ).order_by(Enrollment.date_enrolled.desc()).limit(5).all()

    return render_template('dashboard/index.html',
        total_enrolled=total_enrolled,
        total_pending=total_pending,
        total_sections=total_sections,
        slots_remaining=slots_remaining,
        strand_data=strand_data,
        recent=recent
    )

# --- Pending Count API ---
# Called every 30s by dashboard JS to update the live badge
@dashboard.route('/api/pending-count')
@login_required
def pending_count():
    from flask import jsonify
    from app.models.enrollment import Enrollment
    count = Enrollment.query.filter_by(status='pending').count()
    return jsonify({'count': count})