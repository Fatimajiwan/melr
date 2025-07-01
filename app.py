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
    app.run(debug=True, port=5002)  # Use port 5002 instead of 5001 