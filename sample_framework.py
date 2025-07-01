from app import create_app, db
from app.models.monitoring import LogFrame, TheoryOfChange, ResultsFramework, Output, Activity, ChangePathway, Result
from sample_project import create_sample_project

app = create_app()

def create_sample_frameworks():
    with app.app_context():
        # Get or create the sample project
        project = create_sample_project()
        
        # Check if frameworks already exist for this project
        existing_logframe = LogFrame.query.filter_by(project_id=project.id).first()
        existing_toc = TheoryOfChange.query.filter_by(project_id=project.id).first()
        existing_results = ResultsFramework.query.filter_by(project_id=project.id).first()
        
        if existing_logframe and existing_toc and existing_results:
            print("Frameworks already exist for this project.")
            return existing_logframe, existing_toc, existing_results
        
        # Create LogFrame if it doesn't exist
        if not existing_logframe:
            logframe = LogFrame(
                project_id=project.id,
                goal="Improved educational outcomes and equitable access to quality education in target communities",
                purpose="Enhanced educational infrastructure, teacher capacity, and student support systems"
            )
            db.session.add(logframe)
            db.session.commit()
            print(f"Created LogFrame for project {project.name}")
        else:
            logframe = existing_logframe
            print("Using existing LogFrame")
        
        # Create Theory of Change if it doesn't exist
        if not existing_toc:
            toc = TheoryOfChange(
                project_id=project.id,
                description="This theory of change focuses on improving educational outcomes through infrastructure, teacher training, and student support, leading to higher enrollment, improved test scores, and reduced dropout rates."
            )
            db.session.add(toc)
            db.session.commit()
            print(f"Created Theory of Change for project {project.name}")
        else:
            toc = existing_toc
            print("Using existing Theory of Change")
        
        # Create Results Framework if it doesn't exist
        if not existing_results:
            results_framework = ResultsFramework(
                project_id=project.id,
                name="Education Improvement Results Framework",
                description="Framework for tracking educational outcomes and impacts of the project"
            )
            db.session.add(results_framework)
            db.session.commit()
            print(f"Created Results Framework for project {project.name}")
        else:
            results_framework = existing_results
            print("Using existing Results Framework")
        
        # Create Outputs if they don't exist for LogFrame
        existing_outputs = Output.query.filter_by(logframe_id=logframe.id).first()
        if not existing_outputs:
            output1 = Output(
                logframe_id=logframe.id,
                description="Improved school infrastructure"
            )
            
            output2 = Output(
                logframe_id=logframe.id,
                description="Enhanced teacher capacity"
            )
            
            output3 = Output(
                logframe_id=logframe.id,
                description="Increased student support services"
            )
            
            db.session.add_all([output1, output2, output3])
            db.session.commit()
            print(f"Created 3 Outputs for LogFrame")
            
            # Create Activities for these outputs
            activities = [
                Activity(output_id=output1.id, logframe_id=logframe.id, description="Renovate classroom buildings", status="in_progress"),
                Activity(output_id=output1.id, logframe_id=logframe.id, description="Install computer labs", status="planned"),
                Activity(output_id=output1.id, logframe_id=logframe.id, description="Upgrade library facilities", status="completed"),
                Activity(output_id=output2.id, logframe_id=logframe.id, description="Conduct teacher training workshops", status="in_progress"),
                Activity(output_id=output2.id, logframe_id=logframe.id, description="Develop teaching resources", status="completed"),
                Activity(output_id=output3.id, logframe_id=logframe.id, description="Establish after-school tutoring program", status="in_progress"),
                Activity(output_id=output3.id, logframe_id=logframe.id, description="Create scholarship program", status="planned")
            ]
            db.session.add_all(activities)
            db.session.commit()
            print(f"Created 7 Activities for Outputs")
        else:
            print("Outputs already exist for LogFrame")
        
        # Create Change Pathways for Theory of Change
        existing_pathways = ChangePathway.query.filter_by(toc_id=toc.id).first()
        if not existing_pathways:
            pathways = [
                ChangePathway(toc_id=toc.id, description="Improved school infrastructure leads to better learning environment", sequence=1),
                ChangePathway(toc_id=toc.id, description="Enhanced teacher capacity results in higher quality instruction", sequence=2),
                ChangePathway(toc_id=toc.id, description="Increased student support services reduce dropout rates", sequence=3)
            ]
            db.session.add_all(pathways)
            db.session.commit()
            print(f"Created 3 Change Pathways for Theory of Change")
        else:
            print("Change Pathways already exist for Theory of Change")
        
        # Create Results for Results Framework
        existing_results_data = Result.query.filter_by(framework_id=results_framework.id).first()
        if not existing_results_data:
            results = [
                Result(framework_id=results_framework.id, description="Increased enrollment rates", level="output"),
                Result(framework_id=results_framework.id, description="Improved test scores", level="outcome"),
                Result(framework_id=results_framework.id, description="Reduced dropout rates", level="outcome"),
                Result(framework_id=results_framework.id, description="Increased graduation rates", level="impact")
            ]
            db.session.add_all(results)
            db.session.commit()
            print(f"Created 4 Results for Results Framework")
        else:
            print("Results already exist for Results Framework")
        
        return logframe, toc, results_framework

if __name__ == "__main__":
    create_sample_frameworks() 