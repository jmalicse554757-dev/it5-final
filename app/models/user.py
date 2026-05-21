# ============================================================
# models/user.py — User Model
# Represents admin, staff, and student login accounts
# ============================================================

from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.Enum('admin', 'staff', 'student'), default='staff')
    full_name     = db.Column(db.String(150))
    # Plain column — Flask-Login reads this directly via UserMixin, no @property needed
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'


# Tells Flask-Login how to reload a user from the session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))