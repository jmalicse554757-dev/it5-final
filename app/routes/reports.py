# ============================================================
# reports.py — Reports Blueprint
# Handles: viewing filtered enrollment reports and CSV export
# ============================================================

from flask import Blueprint, render_template, request, Response
from flask_login import login_required
from app.models.enrollment import Enrollment
from app.models.strand import Strand
from app.models.section import Section
import csv
import io

reports = Blueprint('reports', __name__)


# --- Query Builder Helper ---
# Builds a filtered Enrollment query based on strand, status, and grade level
# Used by both the report view and CSV export so filters stay consistent
def build_query(selected_strand, selected_status, selected_grade):
    query = Enrollment.query

    # Filter by strand if selected
    if selected_strand:
        query = query.filter(Enrollment.strand_id == int(selected_strand))

    # Filter by enrollment status (pending, enrolled, rejected)
    if selected_status:
        query = query.filter(Enrollment.status == selected_status)

    # Filter by grade level — finds matching section IDs first, then filters
    if selected_grade:
        section_ids = [
            s.id for s in Section.query.filter_by(grade_level=selected_grade).all()
        ]
        query = query.filter(Enrollment.section_id.in_(section_ids))

    return query


# --- Reports Page ---
# Displays filtered enrollment list with summary counts
# Filters: strand, status, grade level (passed as URL query params)
@reports.route('/reports')
@login_required
def index():
    strands = Strand.query.filter_by(is_active=True).all()

    # Read filter values from URL (e.g. /reports?strand=1&status=enrolled)
    selected_strand = request.args.get('strand', '')
    selected_status = request.args.get('status', '')
    selected_grade  = request.args.get('grade', '')

    # Run the filtered query
    results = build_query(selected_strand, selected_status, selected_grade).all()

    # Count totals per status for the summary cards
    total          = len(results)
    count_enrolled = sum(1 for e in results if e.status == 'enrolled')
    count_pending  = sum(1 for e in results if e.status == 'pending')
    count_rejected = sum(1 for e in results if e.status == 'rejected')

    return render_template('reports/index.html',
        strands=strands,
        results=results,
        total=total,
        count_enrolled=count_enrolled,
        count_pending=count_pending,
        count_rejected=count_rejected,
        selected_strand=selected_strand,
        selected_status=selected_status,
        selected_grade=selected_grade
    )


# --- Export to CSV ---
# Downloads the current filtered report as a .csv file
# Uses the same filters as the reports page so what you see is what you download
@reports.route('/reports/export/csv')
@login_required
def export_csv():
    # Read the same filter params as the reports page
    selected_strand = request.args.get('strand', '')
    selected_status = request.args.get('status', '')
    selected_grade  = request.args.get('grade', '')

    results = build_query(selected_strand, selected_status, selected_grade).all()

    # Build CSV in memory (no temp file needed)
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header row
    writer.writerow(['LRN', 'Last Name', 'First Name', 'Middle Name',
                     'Sex', 'Strand', 'Section', 'Grade Level',
                     'Status', 'Date Applied'])

    # Write one row per enrollment result
    for e in results:
        writer.writerow([
            e.student.lrn,
            e.student.last_name,
            e.student.first_name,
            e.student.middle_name or '',
            e.student.sex or '',
            e.strand.code if e.strand else '',        # Safe — strand may be unassigned
            e.section.name if e.section else '',      # Safe — section may be unassigned
            e.section.grade_level if e.section else '',
            e.status,
            e.date_applied.strftime('%Y-%m-%d')
        ])

    # Send as downloadable CSV file
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=enrollease_report.csv'}
    )