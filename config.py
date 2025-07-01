import os
from datetime import timedelta

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Report generation settings
    REPORT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
    ALLOWED_REPORT_FORMATS = ['pdf', 'xlsx', 'pptx']
    
    # Email settings (if needed)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
    
    # Offline storage settings
    OFFLINE_STORAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'offline')
    
    # Report generation settings
    REPORT_TEMPLATES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'templates', 'reports')
    
    # Ensure required directories exist
    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.OFFLINE_STORAGE_PATH, exist_ok=True)
        os.makedirs(Config.REPORT_TEMPLATES_PATH, exist_ok=True) 