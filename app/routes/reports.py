from flask import Blueprint, render_template, request, Response
from flask_login import login_required
from app.models.enrollment import Enrollment
from app.models.strand import Strand
from app.models.section import Section
import csv
import io

reports = Blueprint('reports', __name__)

@reports.route('/reports')
@login_required
def index():
    strands = Strand.query.filter_by(is_active=True).all()

    selected_strand = request.args.get('strand', '')
    selected_status = request.args.get('status', '')
    selected_grade  = request.args.get('grade', '')

    query = Enrollment.query

    if selected_strand:
        query = query.filter_by(strand_id=selected_strand)
    if selected_status:
        query = query.filter_by(status=selected_status)
    if selected_grade:
        query = query.join(Section).filter(Section.grade_level == selected_grade)

    results = query.all()

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

@reports.route('/reports/export/csv')
@login_required
def export_csv():
    selected_strand = request.args.get('strand', '')
    selected_status = request.args.get('status', '')
    selected_grade  = request.args.get('grade', '')

    query = Enrollment.query

    if selected_strand:
        query = query.filter_by(strand_id=selected_strand)
    if selected_status:
        query = query.filter_by(status=selected_status)
    if selected_grade:
        query = query.join(Section).filter(Section.grade_level == selected_grade)

    results = query.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['LRN', 'Last Name', 'First Name', 'Middle Name',
                     'Sex', 'Strand', 'Section', 'Grade Level',
                     'Status', 'Date Applied'])

    for e in results:
        writer.writerow([
            e.student.lrn,
            e.student.last_name,
            e.student.first_name,
            e.student.middle_name or '',
            e.student.sex or '',
            e.strand.code if e.strand else '',
            e.section.name if e.section else '',
            e.section.grade_level if e.section else '',
            e.status,
            e.date_applied.strftime('%Y-%m-%d')
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=enrollease_report.csv'}
    )