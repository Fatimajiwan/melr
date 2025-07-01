from app import db
from datetime import datetime

class CalendarEvent(db.Model):
    __tablename__ = 'calendar_event'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g., 'meeting', 'data_collection', 'report_due'
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    participants = db.Column(db.String(500))  # Comma-separated list of participants
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    project = db.relationship('Project', backref='calendar_events')
    
    def __repr__(self):
        return f'<CalendarEvent {self.title}>' 