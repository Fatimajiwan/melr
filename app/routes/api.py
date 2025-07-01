from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.models.project import Project
from app.models.indicator import Indicator
from app.models.monitoring import (
    Measurement, KPI, KPIMeasurement, ScholarProfile, 
    ScholarCheckIn, ScholarSurvey, SurveyResponse
)
from app import db
from datetime import datetime

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/projects', methods=['GET'])
@login_required
def get_projects():
    projects = Project.query.all()
    return jsonify([project.to_dict() for project in projects])

@bp.route('/indicators', methods=['GET'])
@login_required
def get_indicators():
    indicators = Indicator.query.all()
    return jsonify([indicator.to_dict() for indicator in indicators])

@bp.route('/project/<int:project_id>/indicators', methods=['GET'])
@login_required
def get_project_indicators(project_id):
    project = Project.query.get_or_404(project_id)
    return jsonify([indicator.to_dict() for indicator in project.indicators])

@bp.route('/indicators', methods=['POST'])
def create_indicator():
    data = request.json
    indicator = Indicator(
        name=data['name'],
        description=data.get('description', ''),
        baseline=data.get('baseline', 0),
        target_value=data.get('target', 0),
        current_value=data.get('current_value', 0),
        unit=data.get('unit', ''),
        frequency=data.get('frequency', ''),
        project_id=data['project_id']
    )
    
    db.session.add(indicator)
    db.session.commit()
    
    return jsonify(indicator.to_dict()), 201

@bp.route('/indicator/<int:indicator_id>', methods=['GET'])
def get_indicator(indicator_id):
    indicator = Indicator.query.get_or_404(indicator_id)
    return jsonify(indicator.to_dict())

@bp.route('/indicator/<int:indicator_id>/measurements', methods=['GET'])
def get_measurements(indicator_id):
    measurements = Measurement.query.filter_by(indicator_id=indicator_id).all()
    return jsonify([{
        'id': m.id,
        'date': m.date.isoformat(),
        'value': m.value,
        'notes': m.notes
    } for m in measurements])

@bp.route('/indicator/<int:indicator_id>/measurements', methods=['POST'])
def add_measurement(indicator_id):
    data = request.json
    measurement = Measurement(
        indicator_id=indicator_id,
        value=data['value'],
        date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        notes=data.get('notes', '')
    )
    
    db.session.add(measurement)
    db.session.commit()
    
    return jsonify({
        'id': measurement.id,
        'date': measurement.date.isoformat(),
        'value': measurement.value,
        'notes': measurement.notes
    }), 201

@bp.route('/kpi/<int:kpi_id>/measurements', methods=['GET'])
def get_kpi_measurements(kpi_id):
    measurements = KPIMeasurement.query.filter_by(kpi_id=kpi_id).all()
    return jsonify([{
        'id': m.id,
        'date': m.date.isoformat(),
        'value': m.value,
        'notes': m.notes
    } for m in measurements])

@bp.route('/kpi/<int:kpi_id>/measurements', methods=['POST'])
def add_kpi_measurement(kpi_id):
    data = request.json
    measurement = KPIMeasurement(
        kpi_id=kpi_id,
        value=data['value'],
        date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        notes=data.get('notes', '')
    )
    
    db.session.add(measurement)
    db.session.commit()
    
    return jsonify({
        'id': measurement.id,
        'date': measurement.date.isoformat(),
        'value': measurement.value,
        'notes': measurement.notes
    }), 201

@bp.route('/scholars', methods=['GET'])
def get_scholars():
    scholars = ScholarProfile.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'email': s.email,
        'gender': s.gender,
        'university': s.university,
        'program': s.program,
        'enrollment_date': s.enrollment_date.isoformat() if s.enrollment_date else None,
        'expected_graduation': s.expected_graduation.isoformat() if s.expected_graduation else None,
        'current_gpa': s.current_gpa,
        'is_first_generation': s.is_first_generation
    } for s in scholars])

@bp.route('/scholars/<int:scholar_id>/check_ins', methods=['GET'])
def get_scholar_check_ins(scholar_id):
    check_ins = ScholarCheckIn.query.filter_by(scholar_id=scholar_id).all()
    return jsonify([{
        'id': c.id,
        'check_in_date': c.check_in_date.isoformat(),
        'academic_status': c.academic_status,
        'emotional_status': c.emotional_status,
        'biggest_challenge': c.biggest_challenge,
        'achievements': c.achievements,
        'needs_followup': c.needs_followup
    } for c in check_ins])

@bp.route('/surveys/<int:survey_id>/responses', methods=['GET'])
def get_survey_responses(survey_id):
    responses = SurveyResponse.query.filter_by(survey_id=survey_id).all()
    return jsonify([{
        'id': r.id,
        'respondent_name': r.respondent_name,
        'submission_date': r.submission_date.isoformat(),
        'answers': [{
            'question_id': a.question_id,
            'answer_text': a.answer_text
        } for a in r.answers]
    } for r in responses])

@bp.route('/surveys/<int:survey_id>/responses', methods=['POST'])
def add_survey_response(survey_id):
    data = request.json
    
    response = SurveyResponse(
        survey_id=survey_id,
        respondent_name=data.get('respondent_name', ''),
        respondent_email=data.get('respondent_email', '')
    )
    
    db.session.add(response)
    db.session.flush()  # Get the ID without committing
    
    # Add answers
    from app.models.monitoring import SurveyAnswer
    for answer_data in data.get('answers', []):
        answer = SurveyAnswer(
            response_id=response.id,
            question_id=answer_data['question_id'],
            answer_text=answer_data['answer_text']
        )
        db.session.add(answer)
    
    db.session.commit()
    
    return jsonify({
        'id': response.id,
        'message': 'Survey response recorded successfully'
    }), 201 