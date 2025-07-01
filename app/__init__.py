from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['DEBUG'] = True  # Enable debug mode

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        # Import models
        from app.models import User, Project, Report, Indicator
        
        # Import blueprints
        from app.routes import main, auth, admin, reports
        app.register_blueprint(main.main)
        app.register_blueprint(auth.auth)
        app.register_blueprint(admin.admin)
        app.register_blueprint(reports.reports)

        @login_manager.user_loader
        def load_user(id):
            return User.query.get(int(id))

        return app 