from app import create_app, db
from app.models import Project

def list_projects():
    app = create_app()
    with app.app_context():
        projects = Project.query.all()
        print(f"Found {len(projects)} projects:")
        for p in projects:
            print(f"- {p.id}: {p.name} (status: {p.status})")

if __name__ == '__main__':
    list_projects() 