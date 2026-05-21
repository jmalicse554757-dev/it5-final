# ============================================================
# app/utils.py — Shared Utility Functions
# ============================================================

def log_action(user_id, action, detail='', ip=None):
    """
    Writes a single activity log entry to the database.
    Call this after any significant action — approve, reject, add, delete.
    """
    from app import db
    from app.models.activity_log import ActivityLog

    entry = ActivityLog(
        user_id=user_id,
        action=action,
        detail=detail,
        ip_address=ip
    )
    db.session.add(entry)
    # No commit here — caller commits so the log is part of the same transaction