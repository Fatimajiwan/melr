from app import db
from app.models.base import BaseModel
from sqlalchemy.orm import relationship
from app.models.project import Project
from app.models.indicator import Indicator
from datetime import datetime

class LogFrame(BaseModel):
    __tablename__ = 'logframes'
    
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    goal = db.Column(db.Text, nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    
    project = relationship('Project', back_populates='logframe')
    outputs = relationship('Output', back_populates='logframe')
    activities = relationship('Activity', back_populates='logframe')

class TheoryOfChange(BaseModel):
    __tablename__ = 'theory_of_change'
    
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    description = db.Column(db.Text)
    
    project = relationship('Project', back_populates='toc')
    pathways = relationship('ChangePathway', back_populates='toc')

class ResultsFramework(BaseModel):
    __tablename__ = 'results_frameworks'
    
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    project = relationship('Project', back_populates='results_framework')
    results = relationship('Result', back_populates='framework')

class Measurement(BaseModel):
    __tablename__ = 'measurements'
    
    indicator_id = db.Column(db.Integer, db.ForeignKey('indicator.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    
    indicator = relationship('Indicator', back_populates='measurements')

class Output(BaseModel):
    __tablename__ = 'outputs'
    
    logframe_id = db.Column(db.Integer, db.ForeignKey('logframes.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    logframe = relationship('LogFrame', back_populates='outputs')
    activities = relationship('Activity', back_populates='output')

class Activity(BaseModel):
    __tablename__ = 'activities'
    
    logframe_id = db.Column(db.Integer, db.ForeignKey('logframes.id'), nullable=False)
    output_id = db.Column(db.Integer, db.ForeignKey('outputs.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50))  # e.g., 'planned', 'in_progress', 'completed'
    
    logframe = relationship('LogFrame', back_populates='activities')
    output = relationship('Output', back_populates='activities')

class ChangePathway(BaseModel):
    __tablename__ = 'change_pathways'
    
    toc_id = db.Column(db.Integer, db.ForeignKey('theory_of_change.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    sequence = db.Column(db.Integer)
    
    toc = relationship('TheoryOfChange', back_populates='pathways')

class Result(BaseModel):
    __tablename__ = 'results'
    
    framework_id = db.Column(db.Integer, db.ForeignKey('results_frameworks.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    level = db.Column(db.String(50))  # e.g., 'output', 'outcome', 'impact'
    
    framework = relationship('ResultsFramework', back_populates='results')

# Education Program Specific Models
class KPICategory(BaseModel):
    __tablename__ = 'kpi_categories'
    
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    project = relationship('Project', back_populates='kpi_categories')
    kpis = relationship('KPI', back_populates='category')

class KPI(BaseModel):
    __tablename__ = 'kpis'
    
    category_id = db.Column(db.Integer, db.ForeignKey('kpi_categories.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    indicator_formula = db.Column(db.Text)
    current_value = db.Column(db.Float)
    target_value = db.Column(db.Float)
    frequency = db.Column(db.String(50))  # e.g., 'quarterly', 'annually'
    notes = db.Column(db.Text)
    
    category = relationship('KPICategory', back_populates='kpis')
    measurements = relationship('KPIMeasurement', back_populates='kpi')

class KPIMeasurement(BaseModel):
    __tablename__ = 'kpi_measurements'
    
    kpi_id = db.Column(db.Integer, db.ForeignKey('kpis.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    
    kpi = relationship('KPI', back_populates='measurements')

class ScholarSurvey(BaseModel):
    __tablename__ = 'scholar_surveys'
    
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    survey_type = db.Column(db.String(50))  # e.g., 'feedback', 'alumni_outcome', 'monthly_check_in'
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    project = relationship('Project', back_populates='scholar_surveys')
    questions = relationship('SurveyQuestion', back_populates='survey')
    responses = relationship('SurveyResponse', back_populates='survey')

class SurveyQuestion(BaseModel):
    __tablename__ = 'survey_questions'
    
    survey_id = db.Column(db.Integer, db.ForeignKey('scholar_surveys.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50))  # e.g., 'multiple_choice', 'text', 'rating'
    options = db.Column(db.Text)  # JSON string for choices if applicable
    required = db.Column(db.Boolean, default=False)
    sequence = db.Column(db.Integer)
    
    survey = relationship('ScholarSurvey', back_populates='questions')
    answers = relationship('SurveyAnswer', back_populates='question')

class SurveyResponse(BaseModel):
    __tablename__ = 'survey_responses'
    
    survey_id = db.Column(db.Integer, db.ForeignKey('scholar_surveys.id'), nullable=False)
    respondent_name = db.Column(db.String(100))
    respondent_email = db.Column(db.String(100))
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    survey = relationship('ScholarSurvey', back_populates='responses')
    answers = relationship('SurveyAnswer', back_populates='response')

class SurveyAnswer(BaseModel):
    __tablename__ = 'survey_answers'
    
    response_id = db.Column(db.Integer, db.ForeignKey('survey_responses.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('survey_questions.id'), nullable=False)
    answer_text = db.Column(db.Text)
    
    response = relationship('SurveyResponse', back_populates='answers')
    question = relationship('SurveyQuestion', back_populates='answers')

class ScholarProfile(BaseModel):
    __tablename__ = 'scholar_profiles'
    
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    gender = db.Column(db.String(20))
    university = db.Column(db.String(100))
    program = db.Column(db.String(100))
    enrollment_date = db.Column(db.Date)
    expected_graduation = db.Column(db.Date)
    current_gpa = db.Column(db.Float)
    is_first_generation = db.Column(db.Boolean)
    
    check_ins = relationship('ScholarCheckIn', back_populates='scholar')
    academic_records = relationship('AcademicRecord', back_populates='scholar')

class ScholarCheckIn(BaseModel):
    __tablename__ = 'scholar_check_ins'
    
    scholar_id = db.Column(db.Integer, db.ForeignKey('scholar_profiles.id'), nullable=False)
    check_in_date = db.Column(db.DateTime, default=datetime.utcnow)
    academic_status = db.Column(db.String(20))  # e.g., 'excellent', 'good', 'fair', 'struggling'
    attended_all_classes = db.Column(db.Boolean)
    needs_academic_support = db.Column(db.Boolean)
    emotional_status = db.Column(db.String(20))  # e.g., 'very_well', 'okay', 'stressed', 'struggling'
    mental_health_concerns = db.Column(db.Text)
    needs_followup = db.Column(db.Boolean)
    received_payments = db.Column(db.Boolean)
    financial_difficulty = db.Column(db.Boolean)
    needs_met = db.Column(db.String(20))  # e.g., 'yes', 'partially', 'no'
    biggest_challenge = db.Column(db.Text)
    support_needed = db.Column(db.Text)
    participated_activities = db.Column(db.Boolean)
    activity_description = db.Column(db.Text)
    upcoming_goals = db.Column(db.Text)
    follow_up_required = db.Column(db.Boolean)
    follow_up_action = db.Column(db.Text)
    
    scholar = relationship('ScholarProfile', back_populates='check_ins')

class AcademicRecord(BaseModel):
    __tablename__ = 'academic_records'
    
    scholar_id = db.Column(db.Integer, db.ForeignKey('scholar_profiles.id'), nullable=False)
    semester = db.Column(db.String(50))
    year = db.Column(db.Integer)
    gpa = db.Column(db.Float)
    courses_passed = db.Column(db.Integer)
    courses_failed = db.Column(db.Integer)
    notes = db.Column(db.Text)
    
    scholar = relationship('ScholarProfile', back_populates='academic_records')

class MentorshipSession(BaseModel):
    __tablename__ = 'mentorship_sessions'
    
    mentor_name = db.Column(db.String(100), nullable=False)
    mentee_id = db.Column(db.Integer, db.ForeignKey('scholar_profiles.id'), nullable=False)
    session_date = db.Column(db.DateTime, nullable=False)
    topics_discussed = db.Column(db.Text)
    action_points = db.Column(db.Text)
    mentor_comments = db.Column(db.Text)
    
    mentee = relationship('ScholarProfile') 