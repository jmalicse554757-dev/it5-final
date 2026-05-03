from app import db

class Section(db.Model):
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    strand_id = db.Column(db.Integer, db.ForeignKey('strands.id'), nullable=False)
    grade_level = db.Column(db.Enum('11', '12'), nullable=False)
    max_capacity = db.Column(db.Integer, default=40)
    school_year = db.Column(db.String(20), default='2024-2025')
    is_active = db.Column(db.Boolean, default=True)

    enrollments = db.relationship('Enrollment', backref='section', lazy=True)

    def current_count(self):
        from app.models.enrollment import Enrollment
        return Enrollment.query.filter_by(
            section_id=self.id,
            status='enrolled'
        ).count()

    def is_full(self):
        return self.current_count() >= self.max_capacity

    def __repr__(self):
        return f'<Section {self.name}>'