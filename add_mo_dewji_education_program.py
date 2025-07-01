from app import create_app, db
from app.models import User, Project, Indicator

def add_mo_dewji_education_program():
    app = create_app()
    with app.app_context():
        # Get or create admin user
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(name='admin', email='admin@example.com', role='admin')
            admin.set_password('Admin123!')
            db.session.add(admin)
            db.session.commit()

        # Check if the project already exists
        project = Project.query.filter_by(name='Mo Dewji Foundation Education Program').first()
        if not project:
            project = Project(
                name='Mo Dewji Foundation Education Program',
                description='A comprehensive education program by the Mo Dewji Foundation.',
                status='active',
                created_by=admin
            )
            db.session.add(project)
            db.session.commit()
            print('Created Mo Dewji Foundation Education Program')
        else:
            print('Mo Dewji Foundation Education Program already exists')

        # Add sample indicators
        indicators = [
            ('Enrollment Rate', 'Percentage of eligible students enrolled', 95, 'percentage'),
            ('Graduation Rate', 'Percentage of students who graduate', 90, 'percentage'),
            ('Average Test Score', 'Average score of standardized tests', 75, 'score'),
        ]
        for name, desc, target, typ in indicators:
            if not Indicator.query.filter_by(name=name, project_id=project.id).first():
                indicator = Indicator(
                    name=name,
                    description=desc,
                    target_value=target,
                    unit=typ,
                    project=project
                )
                db.session.add(indicator)
        db.session.commit()
        print('Added indicators to Mo Dewji Foundation Education Program')

if __name__ == '__main__':
    add_mo_dewji_education_program() 