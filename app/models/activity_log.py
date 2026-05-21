# ============================================================
# models/activity_log.py — Activity Log Model
# Tracks key actions by admin and staff for audit purposes
# Logged actions: login, logout, approve, reject, add, delete
# ============================================================

from app import db
from datetime import datetime

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action     = db.Column(db.String(100), nullable=False)   # Short action label
    detail     = db.Column(db.String(255))                   # Extra context
    ip_address = db.Column(db.String(45))                    # IPv4 or IPv6
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', lazy=True)

    def __repr__(self):
        return f'<ActivityLog {self.action} by user {self.user_id}>'