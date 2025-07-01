from app import create_app, db
from app.models.project import Project
from datetime import datetime, timedelta

app = create_app()

def create_sample_project():
    with app.app_context():
        # Check if project already exists
        if not Project.query.filter_by(name="Sample Education Project").first():
            # Create a new project
            project = Project(
                name="Sample Education Project",
                description="A project focused on improving educational outcomes in rural communities",
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=365),
                status="active"
            )
            db.session.add(project)
            db.session.commit()
            print(f"Project created: {project.name} (ID: {project.id})")
        else:
            print("Sample project already exists.")

if __name__ == "__main__":
    create_sample_project() 