sample_data_script = '''#!/usr/bin/env python
from app import create_app, db
from app.models.project import Project
from app.models.indicator import Indicator
from app.models.monitoring import LogFrame, TheoryOfChange, ResultsFramework, Measurement, Output, Activity, ChangePathway, Result
from datetime import datetime, timedelta
import random

app = create_app()

def create_sample_data():
    with app.app_context():
        # Check if sample project already exists
        existing_project = Project.query.filter_by(name="Educational Access Initiative").first()
        if existing_project:
            print("Sample project already exists. Skipping creation.")
            return
        
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
        
        # Create LogFrame
        logframe = LogFrame(
            project_id=project.id,
            goal="Improved educational outcomes and equitable access to quality education in target communities",
            purpose="Enhanced educational infrastructure, teacher capacity, and student support systems"
        )
        db.session.add(logframe)
        
        # Create Theory of Change
        toc = TheoryOfChange(
            project_id=project.id,
            vision="Equitable access to quality education for all children",
            primary_outcome="Improved educational attainment and reduced dropout rates",
            assumptions="Community support, government cooperation, stable funding"
        )
        db.session.add(toc)
        
        # Create Results Framework
        results_framework = ResultsFramework(
            project_id=project.id,
            goal="Improved educational outcomes in target communities",
            impact_statement="Increased literacy rates and educational attainment"
        )
        db.session.add(results_framework)
        db.session.commit()
        
        # Create Outputs
        output1 = Output(
            logframe_id=logframe.id,
            description="Improved school infrastructure",
            indicators="Number of schools renovated, Number of new facilities built"
        )
        
        output2 = Output(
            logframe_id=logframe.id,
            description="Enhanced teacher capacity",
            indicators="Number of teachers trained, Improvement in teaching quality assessments"
        )
        
        output3 = Output(
            logframe_id=logframe.id,
            description="Increased student support services",
            indicators="Number of tutoring programs established, Number of students receiving support"
        )
        
        db.session.add_all([output1, output2, output3])
        db.session.commit()
        
        # Create Activities
        activities = [
            Activity(output_id=output1.id, description="Renovate classroom buildings", status="in_progress"),
            Activity(output_id=output1.id, description="Install computer labs", status="planned"),
            Activity(output_id=output1.id, description="Upgrade library facilities", status="completed"),
            Activity(output_id=output2.id, description="Conduct teacher training workshops", status="in_progress"),
            Activity(output_id=output2.id, description="Develop teaching resources", status="completed"),
            Activity(output_id=output3.id, description="Establish after-school tutoring program", status="in_progress"),
            Activity(output_id=output3.id, description="Create scholarship program", status="planned")
        ]
        db.session.add_all(activities)
        
        # Create Change Pathways for Theory of Change
        pathways = [
            ChangePathway(toc_id=toc.id, description="Improved school infrastructure leads to better learning environment", position=1),
            ChangePathway(toc_id=toc.id, description="Enhanced teacher capacity results in higher quality instruction", position=2),
            ChangePathway(toc_id=toc.id, description="Increased student support services reduce dropout rates", position=3)
        ]
        db.session.add_all(pathways)
        
        # Create Results for Results Framework
        results = [
            Result(framework_id=results_framework.id, description="Increased enrollment rates", level="output"),
            Result(framework_id=results_framework.id, description="Improved test scores", level="outcome"),
            Result(framework_id=results_framework.id, description="Reduced dropout rates", level="outcome"),
            Result(framework_id=results_framework.id, description="Increased graduation rates", level="impact")
        ]
        db.session.add_all(results)
        db.session.commit()
        
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
        
        # Create Measurements (historical data for the past 12 months)
        measurements = []
        
        for indicator in indicators:
            # Calculate a realistic progression from baseline to current value
            baseline = indicator.baseline if indicator.baseline is not None else 0
            current = indicator.current_value
            target = indicator.target_value
            
            # Generate data points for the past 12 months
            for i in range(12):
                # Calculate expected value with some randomness
                # Earlier months closer to baseline, recent months closer to current value
                progress_factor = i / 12.0  # 0 to 1 progression factor
                expected_value = baseline + (current - baseline) * progress_factor
                
                # Add some random variation (±10%)
                variation = expected_value * 0.1
                value = expected_value + random.uniform(-variation, variation)
                
                # Ensure the value makes sense (e.g., counts can't be negative)
                if indicator.unit == "count" and value < 0:
                    value = 0
                
                # Create the measurement
                measurement_date = datetime.now() - timedelta(days=(12-i)*30)
                
                measurement = Measurement(
                    indicator_id=indicator.id,
                    value=round(value, 2),
                    date=measurement_date,
                    notes=f"Monthly measurement for {indicator.name}"
                )
                measurements.append(measurement)
        
        db.session.add_all(measurements)
        db.session.commit()
        
        print(f"Created {len(indicators)} indicators with {len(measurements)} data points")
        print("Sample data creation complete!")

if __name__ == "__main__":
    create_sample_data()
'''

with open('create_sample_data.py', 'w') as f:
    f.write(sample_data_script)

print("Sample data script created successfully.") 