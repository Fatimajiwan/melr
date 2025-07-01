from app import db

class Indicator(db.Model):

    __tablename__ = 'indicator'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    target_value = db.Column(db.Float)
    current_value = db.Column(db.Float)
    unit = db.Column(db.String(20))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    
    # Additional fields
    baseline = db.Column(db.Float)
    frequency = db.Column(db.String(50))  # e.g., 'monthly', 'quarterly', 'annually'
    
    # Relationships
    project = db.relationship('Project', back_populates='indicators')
    measurements = db.relationship('Measurement', back_populates='indicator')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'target_value': self.target_value,
            'current_value': self.current_value,
            'unit': self.unit,
            'project_id': self.project_id,
            'baseline': self.baseline,
            'frequency': self.frequency
        } 
    