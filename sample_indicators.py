from app import create_app, db
from app.models.indicator import Indicator
from sample_project import create_sample_project

app = create_app()

def create_sample_indicators():
    with app.app_context():
        # Get or create the sample project
        project = create_sample_project()
        
        # Check if indicators already exist for this project
        existing_indicators = Indicator.query.filter_by(project_id=project.id).first()
        if existing_indicators:
            print("Indicators already exist for this project.")
            return
        
        # Create Indicators
        indicators = [
            Indicator(
                name="Enrollment Rate",
                description="Percentage of eligible children enrolled in school",
                target_value=95,
                current_value=78,
                unit="percent",
                baseline=75,
                frequency="quarterly",
                project_id=project.id
            ),
            Indicator(
                name="Teacher-Student Ratio",
                description="Average number of students per teacher",
                target_value=20,
                current_value=35,
                unit="ratio",
                baseline=40,
                frequency="annually",
                project_id=project.id
            ),
            Indicator(
                name="Standardized Test Scores",
                description="Average test scores on standardized assessments",
                target_value=75,
                current_value=65,
                unit="score",
                baseline=60,
                frequency="annually",
                project_id=project.id
            ),
            Indicator(
                name="Dropout Rate",
                description="Percentage of students who drop out before completing the school year",
                target_value=5,
                current_value=12,
                unit="percent",
                baseline=15,
                frequency="annually",
                project_id=project.id
            ),
            Indicator(
                name="Schools Renovated",
                description="Number of schools with renovated facilities",
                target_value=20,
                current_value=8,
                unit="count",
                baseline=0,
                frequency="monthly",
                project_id=project.id
            ),
            Indicator(
                name="Teachers Trained",
                description="Number of teachers who completed professional development training",
                target_value=200,
                current_value=95,
                unit="count",
                baseline=0,
                frequency="quarterly",
                project_id=project.id
            )
        ]
        
        db.session.add_all(indicators)
        db.session.commit()
        
        print(f"Created {len(indicators)} indicators for project {project.name}")
        return indicators

if __name__ == "__main__":
    create_sample_indicators() 