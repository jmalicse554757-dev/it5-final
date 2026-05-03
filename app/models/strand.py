from app import db

class Strand(db.Model):
    __tablename__ = 'strands'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

    sections = db.relationship('Section', backref='strand', lazy=True)

    def __repr__(self):
        return f'<Strand {self.code}>'