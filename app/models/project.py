from datetime import datetime
from app import db

class Project(db.Model):
    __tablename__ = 'project'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Education program specific fields
    project_type = db.Column(db.String(50))  # e.g., 'education', 'health', 'general'
    problem_statement = db.Column(db.Text)
    theory_of_change_summary = db.Column(db.Text)
    monitoring_strategy = db.Column(db.Text)
    evaluation_plan = db.Column(db.Text)
    
    # Relationships
    created_by = db.relationship('User', back_populates='projects')
    indicators = db.relationship('Indicator', back_populates='project', lazy=True)
    reports = db.relationship('Report', back_populates='project', lazy=True)
    logframe = db.relationship('LogFrame', back_populates='project', uselist=False)
    toc = db.relationship('TheoryOfChange', back_populates='project', uselist=False)
    results_framework = db.relationship('ResultsFramework', back_populates='project', uselist=False)
    kpi_categories = db.relationship('KPICategory', back_populates='project', lazy=True)
    scholar_surveys = db.relationship('ScholarSurvey', back_populates='project', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'project_type': self.project_type,
            'problem_statement': self.problem_statement,
            'theory_of_change_summary': self.theory_of_change_summary,
            'monitoring_strategy': self.monitoring_strategy,
            'evaluation_plan': self.evaluation_plan,
            'indicators': [indicator.to_dict() for indicator in self.indicators]
        } 