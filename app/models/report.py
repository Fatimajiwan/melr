from datetime import datetime
from app import db

class Report(db.Model):
    """Model for storing generated reports"""
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g., 'kpi', 'quarterly', 'scholar'
    format = db.Column(db.String(20), default='PDF')
    content = db.Column(db.Text)  # Store report content or file path
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    file_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', back_populates='reports')
    project = db.relationship('Project', back_populates='reports')

    def __init__(self, **kwargs):
        """Initialize with validation"""
        print(f"Creating Report with kwargs: {kwargs}")
        
        # Validate required fields
        for field in ['name', 'type', 'user_id']:
            if field not in kwargs:
                raise ValueError(f"Required field '{field}' is missing")
        
        # Ensure format is valid
        if 'format' in kwargs:
            kwargs['format'] = self.ensure_format(kwargs['format'])
        else:
            kwargs['format'] = 'PDF'
            
        # Set defaults for status
        if 'status' not in kwargs:
            kwargs['status'] = 'pending'
            
        # Set generated_at if not provided
        if 'generated_at' not in kwargs:
            kwargs['generated_at'] = datetime.utcnow()
            
        # Set timestamps
        if 'created_at' not in kwargs:
            kwargs['created_at'] = datetime.utcnow()
        if 'updated_at' not in kwargs:
            kwargs['updated_at'] = datetime.utcnow()
            
        # Validate project_id and user_id
        if 'project_id' in kwargs and kwargs['project_id'] is not None:
            from app.models.project import Project
            project = Project.query.get(kwargs['project_id'])
            if not project:
                print(f"Warning: Project with id {kwargs['project_id']} not found")
                
        if 'user_id' in kwargs:
            from app.models.user import User
            user = User.query.get(kwargs['user_id'])
            if not user:
                raise ValueError(f"User with id {kwargs['user_id']} not found")
            
        print(f"Report initialization: Final kwargs: {kwargs}")
        super(Report, self).__init__(**kwargs)
    
    def ensure_format(self, format_value):
        """Ensure format is a valid value"""
        valid_formats = ['PDF', 'EXCEL', 'CSV', 'PPTX']
        format_value = format_value.upper()
        return format_value if format_value in valid_formats else 'PDF'

    @property
    def status_color(self):
        status_colors = {
            'pending': 'warning',
            'processing': 'info',
            'completed': 'success',
            'failed': 'danger'
        }
        return status_colors.get(self.status, 'secondary')

    def __repr__(self):
        return f'<Report {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'format': self.format,
            'generated_at': self.generated_at.isoformat(),
            'project_id': self.project_id,
            'created_by': self.user.username if self.user else None
        }

class Export(db.Model):
    __tablename__ = 'exports'
    
    id = db.Column(db.Integer, primary_key=True)
    data_types = db.Column(db.String(255), nullable=False)
    format = db.Column(db.String(10), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    creator = db.relationship('User', backref=db.backref('exports', lazy=True))
    
    def __repr__(self):
        return f'<Export {self.id}>' 