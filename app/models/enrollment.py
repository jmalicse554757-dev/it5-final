from app import db
from datetime import datetime

class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'))
    strand_id = db.Column(db.Integer, db.ForeignKey('strands.id'))
    status = db.Column(db.Enum('pending', 'enrolled', 'rejected'), default='pending')
    date_applied = db.Column(db.DateTime, default=datetime.utcnow)
    date_enrolled = db.Column(db.DateTime)
    school_year = db.Column(db.String(20), default='2024-2025')
    remarks = db.Column(db.Text)
    enrolled_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    strand = db.relationship('Strand', lazy=True, overlaps="enrollments")

    def __repr__(self):
        return f'<Enrollment {self.id} - {self.status}>'