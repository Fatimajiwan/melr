from flask import Blueprint, render_template, jsonify, request, send_file
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import csv
from io import BytesIO, StringIO
import json
import openpyxl
from app.models.project import Project
from app.models.indicator import Indicator
from app.models.report import Report, Export
from app import db

reports = Blueprint('reports', __name__)

@reports.route('/reports')
@login_required
def index():
    return render_template('reports/index.html')

@reports.route('/reports/program-summary')
@login_required
def program_summary():
    # Get all projects and their indicators
    projects = Project.query.all()
    return render_template('reports/program_summary.html', projects=projects)

@reports.route('/reports/kpi-analytics')
@login_required
def kpi_analytics():
    # Get projects and indicators for the filter dropdowns
    projects = Project.query.all()
    indicators = Indicator.query.all()
    
    # Get summary statistics
    summary_stats = get_summary_statistics()
    
    # Get chart data
    dates, progress_data, target_data = get_chart_data()
    
    return render_template('reports/kpi_analytics.html',
                         projects=projects,
                         indicators=indicators,
                         summary_stats=summary_stats,
                         dates=dates,
                         progress_data=progress_data,
                         target_data=target_data)

@reports.route('/reports/periodic')
@login_required
def periodic():
    projects = Project.query.all()
    recent_reports = Report.query.order_by(Report.created_at.desc()).limit(10).all()
    return render_template('reports/periodic.html',
                         projects=projects,
                         recent_reports=recent_reports)

@reports.route('/reports/export')
@login_required
def export():
    projects = Project.query.all()
    export_history = Export.query.order_by(Export.created_at.desc()).limit(10).all()
    return render_template('reports/export.html',
                         projects=projects,
                         export_history=export_history)

@reports.route('/api/upload-data', methods=['POST'])
@login_required
def upload_data():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Read the file based on its extension
            if file.filename.endswith('.xlsx'):
                # Use openpyxl for Excel files
                workbook = openpyxl.load_workbook(file)
                sheet = workbook.active
                data = []
                for row in sheet.iter_rows(values_only=True):
                    if any(cell is not None for cell in row):  # Skip empty rows
                        data.append(row)
            else:
                # Use csv module for CSV files
                content = file.read().decode('utf-8')
                csv_reader = csv.reader(StringIO(content))
                data = list(csv_reader)
            
            # Process the data
            process_uploaded_data(data)
            
            return jsonify({'message': 'File uploaded successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    return jsonify({'error': 'Invalid file type'}), 400

@reports.route('/api/generate-report', methods=['POST'])
@login_required
def reports_generate_report():
    report_type = request.json.get('type')
    format = request.json.get('format', 'pdf')
    
    try:
        if report_type == 'program-summary':
            output = generate_program_summary_report(format)
        elif report_type == 'kpi-analytics':
            output = generate_kpi_analytics_report(format)
        elif report_type == 'periodic':
            output = generate_periodic_report(format)
        else:
            return jsonify({'error': 'Invalid report type'}), 400
        
        return send_file(
            output,
            mimetype=get_mimetype(format),
            as_attachment=True,
            download_name=f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{format}'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports.route('/api/kpi-analytics', methods=['POST'])
@login_required
def get_kpi_analytics():
    project_id = request.form.get('project')
    indicator_id = request.form.get('indicator')
    date_range = request.form.get('dateRange')
    
    try:
        dates, progress_data, target_data = get_chart_data(
            project_id=project_id,
            indicator_id=indicator_id,
            date_range=date_range
        )
        
        return jsonify({
            'dates': dates,
            'progress_data': progress_data,
            'target_data': target_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports.route('/api/generate-periodic-report', methods=['POST'])
@login_required
def generate_periodic_report():
    report_type = request.form.get('reportType')
    start_date = request.form.get('startDate')
    end_date = request.form.get('endDate')
    project_id = request.form.get('project')
    format = request.form.get('format', 'pdf')
    
    try:
        output = generate_periodic_report(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            project_id=project_id,
            format=format
        )
        
        # Save report to database
        report = Report(
            name=f"{report_type.title()} Report",
            type=report_type,
            format=format,
            user_id=current_user.id,
            project_id=project_id,
            created_at=datetime.now()
        )
        db.session.add(report)
        db.session.commit()
        
        return send_file(
            output,
            mimetype=get_mimetype(format),
            as_attachment=True,
            download_name=f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{format}'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports.route('/api/export-data', methods=['POST'])
@login_required
def export_data():
    data_types = request.form.getlist('dataType')
    project_id = request.form.get('project')
    start_date = request.form.get('startDate')
    end_date = request.form.get('endDate')
    format = request.form.get('format', 'excel')
    
    try:
        output = generate_data_export(
            data_types=data_types,
            project_id=project_id,
            start_date=start_date,
            end_date=end_date,
            format=format
        )
        
        # Save export to database
        export = Export(
            data_types=','.join(data_types),
            format=format,
            file_size=len(output.getvalue()),
            created_at=datetime.now()
        )
        db.session.add(export)
        db.session.commit()
        
        return send_file(
            output,
            mimetype=get_mimetype(format),
            as_attachment=True,
            download_name=f'export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{format}'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports.route('/download-report/<int:report_id>')
@login_required
def download_report(report_id):
    report = Report.query.get_or_404(report_id)
    return send_file(
        report.file_path,
        mimetype=get_mimetype(report.format),
        as_attachment=True,
        download_name=f'report_{report.created_at.strftime("%Y%m%d_%H%M%S")}.{report.format}'
    )

@reports.route('/download-export/<int:export_id>')
@login_required
def download_export(export_id):
    export = Export.query.get_or_404(export_id)
    return send_file(
        export.file_path,
        mimetype=get_mimetype(export.format),
        as_attachment=True,
        download_name=f'export_{export.created_at.strftime("%Y%m%d_%H%M%S")}.{export.format}'
    )

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx', 'xls'}

def get_mimetype(format):
    mimetypes = {
        'pdf': 'application/pdf',
        'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'csv': 'text/csv',
        'json': 'application/json'
    }
    return mimetypes.get(format, 'application/octet-stream')

def get_summary_statistics():
    # Implement summary statistics calculation
    pass

def get_chart_data(project_id=None, indicator_id=None, date_range=None):
    # Implement chart data generation
    pass

def process_uploaded_data(data):
    # Implement data processing logic
    pass

def generate_program_summary_report(format):
    # Implement program summary report generation
    pass

def generate_kpi_analytics_report(format):
    # Implement KPI analytics report generation
    pass

def generate_periodic_report(report_type, start_date, end_date, project_id, format):
    # Implement periodic report generation
    pass

def generate_data_export(data_types, project_id, start_date, end_date, format):
    # Implement data export generation
    pass 