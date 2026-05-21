# ============================================================
# models/strand.py — Strand Model
# Academic tracks (e.g. STEM, ABM, HUMSS)
# ============================================================

from app import db


class Strand(db.Model):
    __tablename__ = 'strands'

    id          = db.Column(db.Integer, primary_key=True)
    code        = db.Column(db.String(10), unique=True, nullable=False)   # Short code e.g. 'STEM'
    full_name   = db.Column(db.String(150), nullable=False)               # e.g. 'Science, Technology, Engineering, and Mathematics'
    description = db.Column(db.Text)
    is_active   = db.Column(db.Boolean, default=True)

    sections    = db.relationship('Section', backref='strand', lazy=True)
    # back_populates matches the strand relationship in Enrollment model
    enrollments = db.relationship('Enrollment', back_populates='strand', lazy=True)

    def __repr__(self):
        return f'<Strand {self.code}>'