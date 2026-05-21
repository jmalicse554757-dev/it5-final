# ============================================================
# models/section.py — Section Model
# Class sections tied to a strand and grade level
# ============================================================

from app import db


class Section(db.Model):
    __tablename__ = 'sections'

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(80), nullable=False)
    strand_id    = db.Column(db.Integer, db.ForeignKey('strands.id'), nullable=False)
    grade_level  = db.Column(db.Enum('11', '12'), nullable=False)
    max_capacity = db.Column(db.Integer, default=40)
    school_year  = db.Column(db.String(20), default='2024-2025')
    is_active    = db.Column(db.Boolean, default=True)

    # back_populates matches the section relationship in Enrollment model
    enrollments  = db.relationship('Enrollment', back_populates='section', lazy=True)

    def current_count(self):
        # Counts enrolled students using already-loaded relationship — avoids extra DB queries
        return sum(1 for e in self.enrollments if e.status == 'enrolled')

    def is_full(self):
        # Returns True if section has hit max capacity
        return self.current_count() >= self.max_capacity

    def __repr__(self):
        return f'<Section {self.name}>'