import os
from app import create_app, db
from config import Config
# Import all models to ensure they're registered with SQLAlchemy
from app.models import User, Project, Indicator, LogFrame, TheoryOfChange, ResultsFramework, Measurement, Output, Activity, ChangePathway, Result, CalendarEvent

app = create_app()

def create_admin():
    email = "admin@example.com"
    name = "admin"
    password = "Admin123!"  # Changed password to be more secure
    if not User.query.filter_by(email=email).first():
        user = User(name=name, email=email, role='admin')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Admin user created: {email} / {password}")
    else:
        # Update existing admin password
        user = User.query.filter_by(email=email).first()
        user.set_password(password)
        db.session.commit()
        print(f"Admin password updated: {email} / {password}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables first
        create_admin()   # Then create admin user
    
    # Use environment variables for production settings
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port) 