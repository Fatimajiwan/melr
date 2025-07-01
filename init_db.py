from app import create_app, db
from app.models.user import User
from app.models.project import Project
import os

app = create_app()

# Make sure app context is pushed so we can use the models
with app.app_context():
    # Drop all tables first
    db.drop_all()
    
    # Create all tables with new names
    db.create_all()
    
    # Create a test admin user
    admin = User(
        email='admin@example.com',
        name='Administrator',
        role='admin'
    )
    admin.set_password('password')
    
    # Create a regular user
    user = User(
        email='user@example.com',
        name='Regular User',
        role='user'
    )
    user.set_password('password')
    
    # Add users to the database
    db.session.add(admin)
    db.session.add(user)
    db.session.commit()  # Commit now to get IDs
    
    # Create a sample project
    project = Project(
        name='Sample Project',
        description='This is a sample project for testing the application',
        status='active',
        created_by_id=admin.id,  # Admin created this project
        project_type='education'
    )
    db.session.add(project)
    
    # Commit the changes
    db.session.commit()
    
    print("Database initialized with admin user (email: admin@example.com, password: password)")
    print("Regular user created (email: user@example.com, password: password)")
    print("Sample project created") 