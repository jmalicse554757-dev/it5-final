# ============================================================
# app/__init__.py — Application Factory
# Sets up Flask app, extensions, models, and blueprints
# ============================================================

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(basedir, '.env'))

# --- Extensions (initialized without app, bound in create_app) ---
db           = SQLAlchemy()
bcrypt       = Bcrypt()
login_manager = LoginManager()
migrate      = Migrate()


def create_app():
    app = Flask(__name__)

    # --- App Configuration ---
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- Bind extensions to app ---
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # --- Login manager settings ---
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'error'

    with app.app_context():
        # Import models (required for migrations to detect them)
        from app.models.user import User
        from app.models.student import Student
        from app.models.strand import Strand
        from app.models.section import Section
        from app.models.enrollment import Enrollment

        # Register all blueprints
        from app.routes.auth import auth
        from app.routes.dashboard import dashboard
        from app.routes.students import students
        from app.routes.enrollment import enrollment
        from app.routes.reports import reports
        from app.routes.admin import admin

        app.register_blueprint(auth)
        app.register_blueprint(dashboard)
        app.register_blueprint(students)
        app.register_blueprint(enrollment)
        app.register_blueprint(reports)
        app.register_blueprint(admin)

    return app