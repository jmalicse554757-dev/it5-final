# ============================================================
# models/student.py — Student Model
# Stores personal info, guardian details, and links to User
# ============================================================

from app import db
from datetime import datetime


class Student(db.Model):
    __tablename__ = 'students'

    id             = db.Column(db.Integer, primary_key=True)
    lrn            = db.Column(db.String(12), unique=True, nullable=False)  # 12-digit Learner Reference Number
    last_name      = db.Column(db.String(80), nullable=False)
    first_name     = db.Column(db.String(80), nullable=False)
    middle_name    = db.Column(db.String(80))
    suffix         = db.Column(db.String(10))
    date_of_birth  = db.Column(db.Date)
    sex            = db.Column(db.Enum('Male', 'Female'))
    contact_number = db.Column(db.String(20))
    email          = db.Column(db.String(120))
    address        = db.Column(db.Text)

    photo          = db.Column(db.String(255))                    # Stored filename, e.g. student_12.jpg
    # Guardian information
    guardian_name         = db.Column(db.String(150))
    guardian_relationship = db.Column(db.String(50))
    guardian_contact      = db.Column(db.String(20))
    guardian_occupation   = db.Column(db.String(100))

    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'))  # Linked login account
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    enrollments = db.relationship('Enrollment', backref='student', lazy=True)

    def get_full_name(self):
        # Fixed: no trailing space when middle name is empty
        first_middle = f"{self.first_name} {self.middle_name}".strip() if self.middle_name else self.first_name
        return f"{self.last_name}, {first_middle}"

    def __repr__(self):
        return f'<Student {self.lrn}>'