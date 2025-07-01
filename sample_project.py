from app import create_app, db
from app.models.project import Project
from datetime import datetime, timedelta

app = create_app()

def create_sample_project():
    with app.app_context():
        # Check if sample project already exists
        existing_project = Project.query.filter_by(name="Educational Access Initiative").first()
        if existing_project:
            print("Sample project already exists.")
            return existing_project
        
        # Create a new project
        project = Project(
            name="Educational Access Initiative",
            description="A comprehensive program to improve educational outcomes and access to quality education in underserved communities through teacher training, infrastructure development, and student support services.",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=730),  # 2 years
            status="active"
        )
        db.session.add(project)
        db.session.commit()
        print(f"Created project: {project.name} (ID: {project.id})")
        return project

if __name__ == "__main__":
    create_sample_project() 