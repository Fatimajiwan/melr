from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file, abort
from flask_login import login_required, current_user
from app.models.project import Project
from app.models.indicator import Indicator
from app.models.monitoring import Measurement
from app.models import CalendarEvent, Report
from app import db
from datetime import datetime
import json
from werkzeug.utils import secure_filename
import os
import pandas as pd
from io import BytesIO

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
@login_required
def index():
    # Get all projects
    projects = Project.query.all()
    
    # Get all indicators
    indicators = Indicator.query.all()
    
    # Calculate indicators at risk (less than 40% progress)
    indicators_at_risk = 0
    for indicator in indicators:
        if indicator.target_value and indicator.target_value > 0 and indicator.current_value is not None:
            progress = (indicator.current_value / indicator.target_value) * 100
            if progress < 40:
                indicators_at_risk += 1
    
    # Get recent reports
    recent_reports = Report.query.order_by(Report.created_at.desc()).limit(5).all()
    
    # Get upcoming events
    upcoming_events = CalendarEvent.query.filter(
        CalendarEvent.start_date >= datetime.now()
    ).order_by(CalendarEvent.start_date.asc()).limit(5).all()
    
    return render_template('index.html',
                         projects=projects,
                         indicators=indicators,
                         indicators_at_risk=indicators_at_risk,
                         recent_reports=recent_reports,
                         upcoming_events=upcoming_events)

@main.route('/projects')
@login_required
def projects():
    projects = Project.query.all()
    return render_template('main/projects.html', projects=projects)

@main.route('/projects/create', methods=['GET', 'POST'])
@login_required
def create_project():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        status = request.form.get('status')
        
        # Convert dates from string to datetime
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
        
        # Create new project
        project = Project(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            status=status
        )
        
        db.session.add(project)
        db.session.commit()
        
        flash('Project created successfully!', 'success')
        return redirect(url_for('main.projects'))
    
    return render_template('main/create_project.html')

@main.route('/indicators')
@login_required
def indicators():
    indicators = Indicator.query.all()
    return render_template('main/indicators.html', indicators=indicators)

@main.route('/project/<int:project_id>')
@login_required
def project_dashboard(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Calculate project duration in months
    duration_months = None
    if project.start_date and project.end_date:
        duration_months = int((project.end_date - project.start_date).days / 30)
    
    return render_template('project/dashboard.html', 
                         project=project,
                         duration_months=duration_months)

@main.route('/project/<int:project_id>/logframe')
def project_logframe(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project/logframe.html', project=project)

@main.route('/project/<int:project_id>/toc')
def project_toc(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project/toc.html', project=project)

@main.route('/project/<int:project_id>/results')
def project_results(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project/results.html', project=project)

@main.route('/projects/<int:project_id>/indicators')
@login_required
def project_indicators(project_id):
    project = Project.query.get_or_404(project_id)
    indicators = project.indicators
    
    # Calculate progress for each indicator
    for indicator in indicators:
        if indicator.target_value and indicator.target_value > 0 and indicator.current_value is not None:
            indicator.progress = int((indicator.current_value / indicator.target_value) * 100)
        else:
            indicator.progress = 0
    
    return render_template('project/indicators.html', project=project, indicators=indicators)

@main.route('/api/indicator/<int:indicator_id>/measurements')
def get_indicator_measurements(indicator_id):
    measurements = Measurement.query.filter_by(indicator_id=indicator_id).all()
    return jsonify([{
        'date': m.date.isoformat(),
        'value': m.value,
        'notes': m.notes
    } for m in measurements])

@main.route('/api/indicator/<int:indicator_id>/measurement', methods=['POST'])
def add_measurement(indicator_id):
    data = request.json
    measurement = Measurement(
        indicator_id=indicator_id,
        value=data['value'],
        date=data['date'],
        notes=data.get('notes', '')
    )
    db.session.add(measurement)
    db.session.commit()
    return jsonify({'status': 'success'})

@main.route('/projects/<int:project_id>/add_indicator', methods=['POST'])
@login_required
def add_indicator(project_id):
    project = Project.query.get_or_404(project_id)
    
    name = request.form.get('name')
    description = request.form.get('description')
    baseline = request.form.get('baseline')
    current_value = request.form.get('current_value')
    target_value = request.form.get('target_value')
    unit = request.form.get('unit')
    frequency = request.form.get('frequency')
    
    # Convert to appropriate types
    try:
        baseline = float(baseline) if baseline else 0
        current_value = float(current_value)
        target_value = float(target_value)
    except ValueError:
        flash('Invalid numeric values provided', 'danger')
        return redirect(url_for('main.project_indicators', project_id=project_id))
    
    indicator = Indicator(
        name=name,
        description=description,
        baseline=baseline,
        current_value=current_value,
        target_value=target_value,
        unit=unit,
        frequency=frequency,
        project_id=project_id
    )
    
    db.session.add(indicator)
    db.session.commit()
    
    flash('Indicator added successfully', 'success')
    return redirect(url_for('main.project_indicators', project_id=project_id))

@main.route('/projects/<int:project_id>/edit_indicator', methods=['POST'])
@login_required
def edit_indicator(project_id):
    project = Project.query.get_or_404(project_id)
    indicator_id = request.form.get('indicator_id')
    
    indicator = Indicator.query.get_or_404(indicator_id)
    
    # Check if indicator belongs to the project
    if indicator.project_id != project_id:
        flash('Invalid indicator', 'danger')
        return redirect(url_for('main.project_indicators', project_id=project_id))
    
    name = request.form.get('name')
    description = request.form.get('description')
    baseline = request.form.get('baseline')
    current_value = request.form.get('current_value')
    target_value = request.form.get('target_value')
    unit = request.form.get('unit')
    frequency = request.form.get('frequency')
    
    # Convert to appropriate types
    try:
        baseline = float(baseline) if baseline else 0
        current_value = float(current_value)
        target_value = float(target_value)
    except ValueError:
        flash('Invalid numeric values provided', 'danger')
        return redirect(url_for('main.project_indicators', project_id=project_id))
    
    indicator.name = name
    indicator.description = description
    indicator.baseline = baseline
    indicator.current_value = current_value
    indicator.target_value = target_value
    indicator.unit = unit
    indicator.frequency = frequency
    
    db.session.commit()
    
    flash('Indicator updated successfully', 'success')
    return redirect(url_for('main.project_indicators', project_id=project_id))

@main.route('/projects/<int:project_id>/delete_indicator', methods=['POST'])
@login_required
def delete_indicator(project_id):
    indicator_id = request.form.get('indicator_id')
    indicator = Indicator.query.get_or_404(indicator_id)
    
    # Check if indicator belongs to the project
    if indicator.project_id != project_id:
        flash('Invalid indicator', 'danger')
        return redirect(url_for('main.project_indicators', project_id=project_id))
    
    # Delete associated measurements first
    Measurement.query.filter_by(indicator_id=indicator_id).delete()
    
    db.session.delete(indicator)
    db.session.commit()
    
    flash('Indicator deleted successfully', 'success')
    return redirect(url_for('main.project_indicators', project_id=project_id))

@main.route('/projects/<int:project_id>/add_measurement', methods=['POST'])
@login_required
def add_indicator_measurement(project_id):
    indicator_id = request.form.get('indicator_id')
    indicator = Indicator.query.get_or_404(indicator_id)
    
    # Check if indicator belongs to the project
    if indicator.project_id != project_id:
        flash('Invalid indicator', 'danger')
        return redirect(url_for('main.project_indicators', project_id=project_id))
    
    value = request.form.get('value')
    date_str = request.form.get('date')
    notes = request.form.get('notes')
    
    # Convert to appropriate types
    try:
        value = float(value)
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        flash('Invalid data provided', 'danger')
        return redirect(url_for('main.project_indicators', project_id=project_id))
    
    measurement = Measurement(
        value=value,
        date=date,
        notes=notes,
        indicator_id=indicator_id
    )
    
    db.session.add(measurement)
    
    # Update current value of the indicator
    indicator.current_value = value
    
    db.session.commit()
    
    flash('Measurement added successfully', 'success')
    return redirect(url_for('main.project_indicators', project_id=project_id))

# API endpoints for AJAX calls
@main.route('/api/indicator/<int:indicator_id>', methods=['GET'])
@login_required
def get_indicator(indicator_id):
    indicator = Indicator.query.get_or_404(indicator_id)
    
    # Check if the indicator belongs to a project the user has access to
    project = Project.query.get(indicator.project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    return jsonify({
        'id': indicator.id,
        'name': indicator.name,
        'description': indicator.description,
        'baseline': indicator.baseline,
        'current_value': indicator.current_value,
        'target_value': indicator.target_value,
        'unit': indicator.unit,
        'frequency': indicator.frequency
    })

@main.route('/api/indicator/<int:indicator_id>/measurements', methods=['GET'])
@login_required
def get_measurements(indicator_id):
    indicator = Indicator.query.get_or_404(indicator_id)
    
    # Check if the indicator belongs to a project the user has access to
    project = Project.query.get(indicator.project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    measurements = Measurement.query.filter_by(indicator_id=indicator_id).all()
    result = []
    
    for m in measurements:
        result.append({
            'id': m.id,
            'value': m.value,
            'date': m.date.isoformat(),
            'notes': m.notes
        })
    
    return jsonify(result)

# Education Program Routes
@main.route('/project/<int:project_id>/education')
@login_required
def education_dashboard(project_id):
    project = Project.query.get_or_404(project_id)
    if project.project_type != 'education':
        flash('This is not an education program project', 'warning')
        return redirect(url_for('main.project_dashboard', project_id=project_id))
    
    # Get KPI categories and KPIs
    from app.models.monitoring import KPICategory, KPI
    kpi_categories = KPICategory.query.filter_by(project_id=project_id).all()
    
    return render_template('project/education/dashboard.html', 
                          project=project, 
                          kpi_categories=kpi_categories)

@main.route('/project/<int:project_id>/education/kpis')
@login_required
def education_kpis(project_id):
    project = Project.query.get_or_404(project_id)
    if project.project_type != 'education':
        flash('This is not an education program project', 'warning')
        return redirect(url_for('main.project_dashboard', project_id=project_id))
    
    # Get KPI categories and KPIs
    from app.models.monitoring import KPICategory, KPI
    kpi_categories = KPICategory.query.filter_by(project_id=project_id).all()
    
    return render_template('project/education/kpis.html', 
                          project=project, 
                          kpi_categories=kpi_categories)

@main.route('/project/<int:project_id>/education/kpis/add_category', methods=['POST'])
@login_required
def add_kpi_category(project_id):
    project = Project.query.get_or_404(project_id)
    if project.project_type != 'education':
        flash('This is not an education program project', 'warning')
        return redirect(url_for('main.project_dashboard', project_id=project_id))
    
    name = request.form.get('name')
    description = request.form.get('description')
    
    from app.models.monitoring import KPICategory
    category = KPICategory(
        project_id=project_id,
        name=name,
        description=description
    )
    
    db.session.add(category)
    db.session.commit()
    
    flash('KPI Category added successfully', 'success')
    return redirect(url_for('main.education_kpis', project_id=project_id))

@main.route('/project/<int:project_id>/education/kpis/add_kpi', methods=['POST'])
@login_required
def add_kpi(project_id):
    project = Project.query.get_or_404(project_id)
    if project.project_type != 'education':
        flash('This is not an education program project', 'warning')
        return redirect(url_for('main.project_dashboard', project_id=project_id))
    
    category_id = request.form.get('category_id')
    name = request.form.get('name')
    indicator_formula = request.form.get('indicator_formula')
    current_value = request.form.get('current_value')
    target_value = request.form.get('target_value')
    frequency = request.form.get('frequency')
    notes = request.form.get('notes')
    
    # Convert to appropriate types
    try:
        current_value = float(current_value) if current_value else 0
        target_value = float(target_value) if target_value else 0
    except ValueError:
        flash('Invalid numeric values provided', 'danger')
        return redirect(url_for('main.education_kpis', project_id=project_id))
    
    from app.models.monitoring import KPI
    kpi = KPI(
        category_id=category_id,
        name=name,
        indicator_formula=indicator_formula,
        current_value=current_value,
        target_value=target_value,
        frequency=frequency,
        notes=notes
    )
    
    db.session.add(kpi)
    db.session.commit()
    
    flash('KPI added successfully', 'success')
    return redirect(url_for('main.education_kpis', project_id=project_id))

@main.route('/project/<int:project_id>/education/kpis/add_measurement', methods=['POST'])
@login_required
def add_kpi_measurement(project_id):
    project = Project.query.get_or_404(project_id)
    if project.project_type != 'education':
        flash('This is not an education program project', 'warning')
        return redirect(url_for('main.project_dashboard', project_id=project_id))
    
    kpi_id = request.form.get('kpi_id')
    value = request.form.get('value')
    date_str = request.form.get('date')
    notes = request.form.get('notes')
    
    # Convert to appropriate types
    try:
        value = float(value)
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        flash('Invalid data provided', 'danger')
        return redirect(url_for('main.education_kpis', project_id=project_id))
    
    from app.models.monitoring import KPIMeasurement
    measurement = KPIMeasurement(
        kpi_id=kpi_id,
        value=value,
        date=date,
        notes=notes
    )
    
    db.session.add(measurement)
    db.session.commit()
    
    flash('KPI Measurement added successfully', 'success')
    return redirect(url_for('main.education_kpis', project_id=project_id))

@main.route('/project/<int:project_id>/education/scholars')
@login_required
def education_scholars(project_id):
    project = Project.query.get_or_404(project_id)
    if project.project_type != 'education':
        flash('This is not an education program project', 'warning')
        return redirect(url_for('main.project_dashboard', project_id=project_id))
    
    from app.models.monitoring import ScholarProfile
    scholars = ScholarProfile.query.all()
    
    return render_template('project/education/scholars.html', 
                          project=project, 
                          scholars=scholars)

@main.route('/project/<int:project_id>/education/scholars/add', methods=['GET', 'POST'])
@login_required
def add_scholar(project_id):
    project = Project.query.get_or_404(project_id)
    if project.project_type != 'education':
        flash('This is not an education program project', 'warning')
        return redirect(url_for('main.project_dashboard', project_id=project_id))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        gender = request.form.get('gender')
        university = request.form.get('university')
        program = request.form.get('program')
        enrollment_date_str = request.form.get('enrollment_date')
        expected_graduation_str = request.form.get('expected_graduation')
        current_gpa = request.form.get('current_gpa')
        is_first_generation = request.form.get('is_first_generation') == 'yes'
        
        # Convert dates and numeric values
        try:
            enrollment_date = datetime.strptime(enrollment_date_str, '%Y-%m-%d').date() if enrollment_date_str else None
            expected_graduation = datetime.strptime(expected_graduation_str, '%Y-%m-%d').date() if expected_graduation_str else None
            current_gpa = float(current_gpa) if current_gpa else None
        except ValueError:
            flash('Invalid data provided', 'danger')
            return redirect(url_for('main.education_scholars', project_id=project_id))
        
        from app.models.monitoring import ScholarProfile
        scholar = ScholarProfile(
            name=name,
            email=email,
            gender=gender,
            university=university,
            program=program,
            enrollment_date=enrollment_date,
            expected_graduation=expected_graduation,
            current_gpa=current_gpa,
            is_first_generation=is_first_generation
        )
        
        db.session.add(scholar)
        db.session.commit()
        
        flash('Scholar added successfully', 'success')
        return redirect(url_for('main.education_scholars', project_id=project_id))
    
    return render_template('project/education/add_scholar.html', project=project)

@main.route('/project/<int:project_id>/education/surveys')
@login_required
def education_surveys(project_id):
    project = Project.query.get_or_404(project_id)
    if project.project_type != 'education':
        flash('This is not an education program project', 'warning')
        return redirect(url_for('main.project_dashboard', project_id=project_id))
    
    from app.models.monitoring import ScholarSurvey
    surveys = ScholarSurvey.query.filter_by(project_id=project_id).all()
    
    return render_template('project/education/surveys.html', 
                          project=project, 
                          surveys=surveys)

@main.route('/project/<int:project_id>/education/surveys/add', methods=['GET', 'POST'])
@login_required
def add_survey(project_id):
    project = Project.query.get_or_404(project_id)
    if project.project_type != 'education':
        flash('This is not an education program project', 'warning')
        return redirect(url_for('main.project_dashboard', project_id=project_id))
    
    if request.method == 'POST':
        name = request.form.get('name')
        survey_type = request.form.get('survey_type')
        description = request.form.get('description')
        
        from app.models.monitoring import ScholarSurvey
        survey = ScholarSurvey(
            project_id=project_id,
            name=name,
            survey_type=survey_type,
            description=description
        )
        
        db.session.add(survey)
        db.session.commit()
        
        flash('Survey added successfully', 'success')
        return redirect(url_for('main.education_surveys', project_id=project_id))
    
    return render_template('project/education/add_survey.html', project=project)

@main.route('/project/<int:project_id>/education/surveys/<int:survey_id>/questions')
@login_required
def survey_questions(project_id, survey_id):
    project = Project.query.get_or_404(project_id)
    if project.project_type != 'education':
        flash('This is not an education program project', 'warning')
        return redirect(url_for('main.project_dashboard', project_id=project_id))
    
    from app.models.monitoring import ScholarSurvey, SurveyQuestion
    survey = ScholarSurvey.query.get_or_404(survey_id)
    questions = SurveyQuestion.query.filter_by(survey_id=survey_id).order_by(SurveyQuestion.sequence).all()
    
    return render_template('project/education/survey_questions.html', 
                          project=project, 
                          survey=survey,
                          questions=questions)

@main.route('/project/<int:project_id>/education/surveys/<int:survey_id>/questions/add', methods=['POST'])
@login_required
def add_survey_question(project_id, survey_id):
    project = Project.query.get_or_404(project_id)
    if project.project_type != 'education':
        flash('This is not an education program project', 'warning')
        return redirect(url_for('main.project_dashboard', project_id=project_id))
    
    question_text = request.form.get('question_text')
    question_type = request.form.get('question_type')
    options = request.form.get('options')
    required = request.form.get('required') == 'yes'
    
    from app.models.monitoring import SurveyQuestion
    
    # Get the next sequence number
    from sqlalchemy import func
    max_sequence = db.session.query(func.max(SurveyQuestion.sequence)).filter_by(survey_id=survey_id).scalar() or 0
    
    question = SurveyQuestion(
        survey_id=survey_id,
        question_text=question_text,
        question_type=question_type,
        options=options,
        required=required,
        sequence=max_sequence + 1
    )
    
    db.session.add(question)
    db.session.commit()
    
    flash('Question added successfully', 'success')
    return redirect(url_for('main.survey_questions', project_id=project_id, survey_id=survey_id))

@main.route('/project/<int:project_id>/education/check_ins')
@login_required
def scholar_check_ins(project_id):
    project = Project.query.get_or_404(project_id)
    if project.project_type != 'education':
        flash('This is not an education program project', 'warning')
        return redirect(url_for('main.project_dashboard', project_id=project_id))
    
    from app.models.monitoring import ScholarCheckIn, ScholarProfile
    check_ins = db.session.query(ScholarCheckIn, ScholarProfile) \
                .join(ScholarProfile, ScholarCheckIn.scholar_id == ScholarProfile.id) \
                .order_by(ScholarCheckIn.check_in_date.desc()) \
                .all()
    
    return render_template('project/education/check_ins.html', 
                          project=project, 
                          check_ins=check_ins)

@main.route('/project/<int:project_id>/education/check_ins/add', methods=['GET', 'POST'])
@login_required
def add_check_in(project_id):
    project = Project.query.get_or_404(project_id)
    if project.project_type != 'education':
        flash('This is not an education program project', 'warning')
        return redirect(url_for('main.project_dashboard', project_id=project_id))
    
    from app.models.monitoring import ScholarProfile
    scholars = ScholarProfile.query.all()
    
    if request.method == 'POST':
        scholar_id = request.form.get('scholar_id')
        academic_status = request.form.get('academic_status')
        attended_all_classes = request.form.get('attended_all_classes') == 'yes'
        needs_academic_support = request.form.get('needs_academic_support') == 'yes'
        emotional_status = request.form.get('emotional_status')
        mental_health_concerns = request.form.get('mental_health_concerns')
        needs_followup = request.form.get('needs_followup') == 'yes'
        received_payments = request.form.get('received_payments') == 'yes'
        financial_difficulty = request.form.get('financial_difficulty') == 'yes'
        needs_met = request.form.get('needs_met')
        biggest_challenge = request.form.get('biggest_challenge')
        support_needed = request.form.get('support_needed')
        participated_activities = request.form.get('participated_activities') == 'yes'
        activity_description = request.form.get('activity_description')
        achievements = request.form.get('achievements')
        upcoming_goals = request.form.get('upcoming_goals')
        follow_up_required = request.form.get('follow_up_required') == 'yes'
        follow_up_action = request.form.get('follow_up_action')
        
        from app.models.monitoring import ScholarCheckIn
        check_in = ScholarCheckIn(
            scholar_id=scholar_id,
            academic_status=academic_status,
            attended_all_classes=attended_all_classes,
            needs_academic_support=needs_academic_support,
            emotional_status=emotional_status,
            mental_health_concerns=mental_health_concerns,
            needs_followup=needs_followup,
            received_payments=received_payments,
            financial_difficulty=financial_difficulty,
            needs_met=needs_met,
            biggest_challenge=biggest_challenge,
            support_needed=support_needed,
            participated_activities=participated_activities,
            activity_description=activity_description,
            achievements=achievements,
            upcoming_goals=upcoming_goals,
            follow_up_required=follow_up_required,
            follow_up_action=follow_up_action
        )
        
        db.session.add(check_in)
        db.session.commit()
        
        flash('Check-in added successfully', 'success')
        return redirect(url_for('main.scholar_check_ins', project_id=project_id))
    
    return render_template('project/education/add_check_in.html', 
                          project=project, 
                          scholars=scholars)

@main.route('/project/<int:project_id>/education/mentorship')
@login_required
def mentorship_sessions(project_id):
    project = Project.query.get_or_404(project_id)
    if project.project_type != 'education':
        flash('This is not an education program project', 'warning')
        return redirect(url_for('main.project_dashboard', project_id=project_id))
    
    from app.models.monitoring import MentorshipSession, ScholarProfile
    sessions = db.session.query(MentorshipSession, ScholarProfile) \
               .join(ScholarProfile, MentorshipSession.mentee_id == ScholarProfile.id) \
               .order_by(MentorshipSession.session_date.desc()) \
               .all()
    
    return render_template('project/education/mentorship.html', 
                          project=project, 
                          sessions=sessions)

@main.route('/project/<int:project_id>/education/mentorship/add', methods=['GET', 'POST'])
@login_required
def add_mentorship_session(project_id):
    project = Project.query.get_or_404(project_id)
    if project.project_type != 'education':
        flash('This is not an education program project', 'warning')
        return redirect(url_for('main.project_dashboard', project_id=project_id))
    
    from app.models.monitoring import ScholarProfile
    scholars = ScholarProfile.query.all()
    
    if request.method == 'POST':
        mentor_name = request.form.get('mentor_name')
        mentee_id = request.form.get('mentee_id')
        session_date_str = request.form.get('session_date')
        topics_discussed = request.form.get('topics_discussed')
        action_points = request.form.get('action_points')
        mentor_comments = request.form.get('mentor_comments')
        
        # Convert date
        try:
            session_date = datetime.strptime(session_date_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format', 'danger')
            return redirect(url_for('main.mentorship_sessions', project_id=project_id))
        
        from app.models.monitoring import MentorshipSession
        session = MentorshipSession(
            mentor_name=mentor_name,
            mentee_id=mentee_id,
            session_date=session_date,
            topics_discussed=topics_discussed,
            action_points=action_points,
            mentor_comments=mentor_comments
        )
        
        db.session.add(session)
        db.session.commit()
        
        flash('Mentorship session added successfully', 'success')
        return redirect(url_for('main.mentorship_sessions', project_id=project_id))
    
    return render_template('project/education/add_mentorship.html', 
                          project=project, 
                          scholars=scholars)

@main.route('/api/kpi/<int:kpi_id>/measurements')
def get_kpi_measurements(kpi_id):
    from app.models.monitoring import KPIMeasurement
    measurements = KPIMeasurement.query.filter_by(kpi_id=kpi_id).all()
    return jsonify([{
        'date': m.date.isoformat(),
        'value': m.value,
        'notes': m.notes
    } for m in measurements])

@main.route('/reports')
@login_required
def reports():
    return render_template('reports/index.html')

@main.route('/reports/program-summary')
@login_required
def program_summary_report():
    # Get all projects and their indicators
    projects = Project.query.all()
    report_data = []
    
    for project in projects:
        project_data = {
            'name': project.name,
            'status': project.status,
            'indicators': []
        }
        
        for indicator in project.indicators:
            progress = 0
            if indicator.target_value and indicator.target_value > 0 and indicator.current_value is not None:
                progress = int((indicator.current_value / indicator.target_value) * 100)
            
            indicator_data = {
                'name': indicator.name,
                'baseline': indicator.baseline,
                'current_value': indicator.current_value,
                'target_value': indicator.target_value,
                'progress': progress
            }
            project_data['indicators'].append(indicator_data)
        
        report_data.append(project_data)
    
    return render_template('reports/program_summary.html', report_data=report_data)

@main.route('/reports/kpi-analytics')
@login_required
def kpi_analytics():
    # Get all indicators across all projects
    indicators = Indicator.query.all()
    return render_template('reports/kpi_analytics.html', indicators=indicators)

@main.route('/reports/periodic')
@login_required
def periodic_reports_view():
    return render_template('reports/periodic.html')

@main.route('/reports/export')
@login_required
def export_data_view():
    return render_template('reports/export.html')

@main.route('/api/upload-data', methods=['POST'])
@login_required
def upload_data():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process the file based on its type
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            return jsonify({'error': 'Unsupported file format'}), 400
        
        # Store the processed data in the session
        session['uploaded_data'] = df.to_json()
        
        return jsonify({'message': 'File uploaded successfully'}), 200
    
    return jsonify({'error': 'Invalid file type'}), 400

@main.route('/api/generate-report', methods=['POST'])
@login_required
def main_generate_report():
    report_type = request.json.get('type')
    format = request.json.get('format', 'pdf')
    
    if report_type == 'program-summary':
        # Generate program summary report
        projects = Project.query.all()
        report_data = []
        
        for project in projects:
            project_data = {
                'name': project.name,
                'status': project.status,
                'indicators': []
            }
            
            for indicator in project.indicators:
                progress = 0
                if indicator.target_value and indicator.target_value > 0 and indicator.current_value is not None:
                    progress = int((indicator.current_value / indicator.target_value) * 100)
                
                indicator_data = {
                    'name': indicator.name,
                    'baseline': indicator.baseline,
                    'current_value': indicator.current_value,
                    'target_value': indicator.target_value,
                    'progress': progress
                }
                project_data['indicators'].append(indicator_data)
            
            report_data.append(project_data)
        
        # Generate the report based on the requested format
        if format == 'pdf':
            # Generate PDF report
            output = BytesIO()
            # Add PDF generation code here
            output.seek(0)
            return send_file(output, mimetype='application/pdf', as_attachment=True, download_name='program_summary.pdf')
        elif format == 'excel':
            # Generate Excel report
            output = BytesIO()
            # Add Excel generation code here
            output.seek(0)
            return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='program_summary.xlsx')
        elif format == 'csv':
            # Generate CSV report
            output = BytesIO()
            # Add CSV generation code here
            output.seek(0)
            return send_file(output, mimetype='text/csv', as_attachment=True, download_name='program_summary.csv')
    
    return jsonify({'error': 'Invalid report type'}), 400

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/project/<int:project_id>/reports')
@login_required
def project_reports(project_id):
    """Project-specific reports and analytics"""
    try:
        # Explicitly check if project exists
        project = Project.query.get(project_id)
        if not project:
            print(f"Project with ID {project_id} not found in project_reports")
            flash(f"Project with ID {project_id} not found", "error")
            return redirect(url_for('main.projects'))
            
        reports = Report.query.filter_by(project_id=project_id).all()
        print(f"Found {len(reports)} reports for project {project_id}")
        return render_template('reports/project_reports.html', project=project, reports=reports)
    except Exception as e:
        import traceback
        print(f"Unexpected error in project_reports: {str(e)}")
        print(traceback.format_exc())
        flash(f'Unexpected error: {str(e)}', 'danger')
        return redirect(url_for('main.projects'))

@main.route('/project/<int:project_id>/reports/generate', methods=['POST'])
@login_required
def generate_project_report(project_id):
    """Generate a new report"""
    try:
        # Explicitly check if project exists
        project = Project.query.get(project_id)
        if not project:
            print(f"Project with ID {project_id} not found in generate_project_report")
            flash(f"Project with ID {project_id} not found", "error")
            return redirect(url_for('main.projects'))
            
        report_type = request.form.get('report_type')
        report_name = request.form.get('report_name')
        
        print(f"Generating report: {report_name} (type: {report_type}) for project {project_id}")
        
        # Create new report
        report_data = {
            'name': report_name,
            'type': report_type,
            'project_id': project_id,
            'user_id': current_user.id,
            'format': 'PDF'
        }
        
        # Create report object
        report = Report(**report_data)
        db.session.add(report)
        db.session.commit()
        
        flash('Report generation started. You will be notified when it is ready.', 'info')
        return redirect(url_for('main.project_reports', project_id=project_id))
    except Exception as e:
        import traceback
        print(f"Error in generate_project_report: {str(e)}")
        print(traceback.format_exc())
        flash(f'Error generating report: {str(e)}', 'danger')
        db.session.rollback()
        return redirect(url_for('main.projects'))

@main.route('/reports/summary')
@login_required
def summary_reports():
    """Generate comprehensive summary reports across all programs and projects"""
    reports = Report.query.filter_by(type='summary').order_by(Report.generated_at.desc()).all()
    return render_template('reports/summary_reports.html', reports=reports)

@main.route('/reports/periodic')
@login_required
def periodic_reports():
    """Generate periodic reports"""
    return render_template('reports/periodic_reports.html')

@main.route('/reports/export')
@login_required
def export_data():
    """Export data in various formats"""
    return render_template('reports/export_data.html')

@main.route('/reports/recent')
@login_required
def recent_reports():
    """View recently generated reports"""
    reports = Report.query.order_by(Report.generated_at.desc()).limit(10).all()
    return render_template('reports/recent_reports.html', reports=reports)

@main.route('/api/report/<int:report_id>/preview')
@login_required
def preview_report(report_id):
    report = Report.query.get_or_404(report_id)
    
    # Check if user has permission to view this report
    if not report.project.has_access(current_user):
        abort(403)
    
    # Generate preview data based on report type
    if report.format == 'pdf':
        # For PDF reports, generate a temporary preview URL
        preview_url = url_for('static', filename=f'reports/preview_{report_id}.pdf')
        return jsonify({
            'type': 'pdf',
            'preview_url': preview_url
        })
    elif report.format == 'excel':
        # For Excel reports, return a message that preview is not available
        return jsonify({
            'type': 'excel',
            'message': 'Excel files cannot be previewed directly'
        })
    else:
        # For other formats, return the data in a table format
        return jsonify({
            'type': 'table',
            'headers': report.get_headers(),
            'rows': report.get_data()
        })

@main.route('/api/report/<int:report_id>/download')
@login_required
def download_report(report_id):
    report = Report.query.get_or_404(report_id)
    format = request.args.get('format', report.format)
    
    # Check if user has permission to download this report
    if not report.project.has_access(current_user):
        abort(403)
    
    # Generate the report file
    file_path = report.generate_file(format)
    
    # Return the file
    return send_file(
        file_path,
        as_attachment=True,
        download_name=f'report_{report_id}.{format}',
        mimetype=f'application/{format}'
    )

@main.route('/project/<int:project_id>/calendar')
@login_required
def project_calendar(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project/calendar.html', project=project)

@main.route('/api/calendar/events')
@login_required
def get_calendar_events():
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'Project ID is required'}), 400
    
    events = CalendarEvent.query.filter_by(project_id=project_id).all()
    return jsonify([{
        'id': event.id,
        'title': event.title,
        'start': event.start_date.isoformat(),
        'end': event.end_date.isoformat(),
        'description': event.description,
        'type': event.type,
        'location': event.location,
        'status': event.status,
        'participants': event.participants
    } for event in events])

@main.route('/api/calendar/upcoming')
@login_required
def get_upcoming_events():
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'Project ID is required'}), 400
    
    events = CalendarEvent.query.filter(
        CalendarEvent.project_id == project_id,
        CalendarEvent.start_date >= db.func.current_timestamp()
    ).order_by(CalendarEvent.start_date).limit(5).all()
    
    return jsonify([{
        'id': event.id,
        'title': event.title,
        'start': event.start_date.isoformat(),
        'end': event.end_date.isoformat(),
        'description': event.description,
        'type': event.type,
        'location': event.location,
        'status': event.status,
        'participants': event.participants
    } for event in events])

@main.route('/api/calendar/event', methods=['POST'])
@login_required
def add_calendar_event():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        print(f"Adding calendar event: {data.get('title')} for project {data.get('project_id')}")
        
        # Validate project
        project_id = data.get('project_id')
        if not project_id:
            return jsonify({'error': 'Project ID is required'}), 400
            
        project = Project.query.get(project_id)
        if not project:
            print(f"Project with ID {project_id} not found in add_calendar_event")
            return jsonify({'error': f'Project with ID {project_id} not found'}), 404
        
        # Create event
        event = CalendarEvent(
            project_id=project_id,
            title=data['title'],
            type=data['type'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            description=data.get('description'),
            location=data.get('location'),
            participants=data.get('participants'),
            status='scheduled'
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            'id': event.id,
            'title': event.title,
            'start': event.start_date.isoformat(),
            'end': event.end_date.isoformat(),
            'description': event.description,
            'type': event.type,
            'location': event.location,
            'status': event.status,
            'participants': event.participants
        })
    except Exception as e:
        import traceback
        print(f"Error in add_calendar_event: {str(e)}")
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main.route('/api/calendar/event/<int:event_id>', methods=['PUT'])
@login_required
def update_calendar_event(event_id):
    event = CalendarEvent.query.get_or_404(event_id)
    data = request.get_json()
    
    if 'title' in data:
        event.title = data['title']
    if 'type' in data:
        event.type = data['type']
    if 'start_date' in data:
        event.start_date = data['start_date']
    if 'end_date' in data:
        event.end_date = data['end_date']
    if 'description' in data:
        event.description = data['description']
    if 'location' in data:
        event.location = data['location']
    if 'participants' in data:
        event.participants = data['participants']
    if 'status' in data:
        event.status = data['status']
    
    db.session.commit()
    
    return jsonify({
        'id': event.id,
        'title': event.title,
        'start': event.start_date.isoformat(),
        'end': event.end_date.isoformat(),
        'description': event.description,
        'type': event.type,
        'location': event.location,
        'status': event.status,
        'participants': event.participants
    })

@main.route('/api/calendar/event/<int:event_id>', methods=['DELETE'])
@login_required
def delete_calendar_event(event_id):
    event = CalendarEvent.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return '', 204

@main.route('/project/<int:project_id>/reports/basic', methods=['GET', 'POST'])
@login_required
def generate_basic_report(project_id):
    """Generate a basic report with selected KPIs"""
    print(f"Starting generate_basic_report for project {project_id}")
    try:
        # Explicitly check if project exists
        project = Project.query.get(project_id)
        if not project:
            print(f"Project with ID {project_id} not found")
            flash(f"Project with ID {project_id} not found", "error")
            return redirect(url_for('main.projects'))
        
        print(f"Found project: {project.name} (ID: {project.id})")
        
        if request.method == 'POST':
            try:
                print("Processing POST request for basic report")
                selected_kpis = request.form.getlist('kpis')
                time_period = request.form.get('time_period')
                report_format = request.form.get('format', 'pdf').upper()
                
                print(f"Report parameters: KPIs={selected_kpis}, time_period={time_period}, format={report_format}")
                
                if not selected_kpis:
                    flash('Please select at least one KPI for the report', 'warning')
                    kpis = Indicator.query.filter_by(project_id=project_id).all()
                    return render_template('reports/basic_report.html', project=project, kpis=kpis)
                
                print("Creating report object")
                # Create new report with defensive error checking
                report_data = {
                    'name': f"Basic Report - {project.name}",
                    'type': 'basic',
                    'project_id': project_id,
                    'user_id': current_user.id,
                    'format': report_format,
                    'content': json.dumps({
                        'kpis': selected_kpis,
                        'time_period': time_period
                    })
                }
                print(f"Report data: {report_data}")
                
                # Create report object
                report = Report(**report_data)
                print("Adding report to session")
                db.session.add(report)
                print("Committing session")
                db.session.commit()
                
                print("Basic report created successfully")
                flash('Basic report generation started. You will be notified when it is ready.', 'info')
                return redirect(url_for('main.project_reports', project_id=project_id))
            except Exception as e:
                import traceback
                print(f"Error generating basic report: {str(e)}")
                print(traceback.format_exc())
                flash(f'Error generating report: {str(e)}', 'danger')
                db.session.rollback()
        
        # Get project KPIs for selection
        kpis = Indicator.query.filter_by(project_id=project_id).all()
        print(f"Found {len(kpis)} KPIs for project")
        return render_template('reports/basic_report.html', project=project, kpis=kpis)
    except Exception as e:
        import traceback
        print(f"Unexpected error in generate_basic_report: {str(e)}")
        print(traceback.format_exc())
        flash(f'Unexpected error: {str(e)}', 'danger')
        return redirect(url_for('main.projects'))

@main.route('/project/<int:project_id>/reports/analytics', methods=['GET', 'POST'])
@login_required
def generate_analytics_report(project_id):
    """Generate an analytics report with trend analysis"""
    try:
        # Explicitly check if project exists
        project = Project.query.get(project_id)
        if not project:
            print(f"Project with ID {project_id} not found in analytics report")
            flash(f"Project with ID {project_id} not found", "error")
            return redirect(url_for('main.projects'))
            
        if request.method == 'POST':
            try:
                analysis_type = request.form.get('analysis_type')
                time_range = request.form.get('time_range')
                include_predictions = request.form.get('include_predictions') == 'true'
                report_format = request.form.get('format', 'pdf').upper()
                
                # Create new report with defensive error checking
                report_data = {
                    'name': f"Analytics Report - {project.name}",
                    'type': 'analytics',
                    'project_id': project_id,
                    'user_id': current_user.id,
                    'format': report_format,
                    'content': json.dumps({
                        'analysis_type': analysis_type,
                        'time_range': time_range,
                        'include_predictions': include_predictions
                    })
                }
                
                # Create report object
                report = Report(**report_data)
                db.session.add(report)
                db.session.commit()
                
                flash('Analytics report generation started. You will be notified when it is ready.', 'info')
                return redirect(url_for('main.project_reports', project_id=project_id))
            except Exception as e:
                import traceback
                print(f"Error generating analytics report: {str(e)}")
                print(traceback.format_exc())
                flash(f'Error generating report: {str(e)}', 'danger')
                db.session.rollback()
        
        return render_template('reports/analytics_report.html', project=project)
    except Exception as e:
        import traceback
        print(f"Unexpected error in generate_analytics_report: {str(e)}")
        print(traceback.format_exc())
        flash(f'Unexpected error: {str(e)}', 'danger')
        return redirect(url_for('main.projects'))

@main.route('/project/<int:project_id>/reports/presentation', methods=['GET', 'POST'])
@login_required
def generate_presentation(project_id):
    """Generate a PowerPoint presentation"""
    try:
        # Explicitly check if project exists
        project = Project.query.get(project_id)
        if not project:
            print(f"Project with ID {project_id} not found in presentation")
            flash(f"Project with ID {project_id} not found", "error")
            return redirect(url_for('main.projects'))
            
        if request.method == 'POST':
            try:
                template = request.form.get('template')
                include_sections = request.form.getlist('sections')
                report_format = request.form.get('format', 'pptx').upper()
                
                # Create new report with defensive error checking
                report_data = {
                    'name': f"Presentation - {project.name}",
                    'type': 'presentation',
                    'project_id': project_id,
                    'user_id': current_user.id,
                    'format': report_format,
                    'content': json.dumps({
                        'template': template,
                        'sections': include_sections
                    })
                }
                
                # Create report object
                report = Report(**report_data)
                db.session.add(report)
                db.session.commit()
                
                flash('Presentation generation started. You will be notified when it is ready.', 'info')
                return redirect(url_for('main.project_reports', project_id=project_id))
            except Exception as e:
                import traceback
                print(f"Error generating presentation: {str(e)}")
                print(traceback.format_exc())
                flash(f'Error generating presentation: {str(e)}', 'danger')
                db.session.rollback()
        
        return render_template('reports/presentation.html', project=project)
    except Exception as e:
        import traceback
        print(f"Unexpected error in generate_presentation: {str(e)}")
        print(traceback.format_exc())
        flash(f'Unexpected error: {str(e)}', 'danger')
        return redirect(url_for('main.projects'))

@main.route('/dashboard')
@login_required
def dashboard():
    # Get all projects
    projects = Project.query.all()
    
    # Get all indicators
    indicators = Indicator.query.all()
    
    # Calculate indicators at risk (less than 40% progress)
    indicators_at_risk = 0
    for indicator in indicators:
        if indicator.target_value and indicator.target_value > 0 and indicator.current_value is not None:
            progress = (indicator.current_value / indicator.target_value) * 100
            if progress < 40:
                indicators_at_risk += 1
    
    # Get recent reports
    recent_reports = Report.query.order_by(Report.created_at.desc()).limit(5).all()
    
    # Get upcoming events
    upcoming_events = CalendarEvent.query.filter(
        CalendarEvent.start_date >= datetime.now()
    ).order_by(CalendarEvent.start_date.asc()).limit(5).all()
    
    return render_template('dashboard.html',
                         projects=projects,
                         indicators=indicators,
                         indicators_at_risk=indicators_at_risk,
                         recent_reports=recent_reports,
                         upcoming_events=upcoming_events)

@main.route('/project/<int:project_id>/calendar/add-event', methods=['POST'])
@login_required
def add_project_calendar_event(project_id):
    """Add a calendar event via form submission"""
    try:
        title = request.form.get('title')
        event_type = request.form.get('type')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        description = request.form.get('description')
        location = request.form.get('location')
        participants = ','.join(request.form.getlist('participants'))
        
        event = CalendarEvent(
            project_id=project_id,
            title=title,
            type=event_type,
            start_date=start_date,
            end_date=end_date,
            description=description,
            location=location,
            participants=participants,
            status='scheduled'
        )
        
        db.session.add(event)
        db.session.commit()
        
        flash('Event added successfully', 'success')
        return redirect(url_for('main.project_calendar', project_id=project_id))
    except Exception as e:
        flash(f'Error adding event: {str(e)}', 'danger')
        return redirect(url_for('main.project_calendar', project_id=project_id)) 