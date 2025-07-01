from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User, Project, Report
from app.utils import admin_required
import os
import subprocess
from datetime import datetime
import psycopg2
import mysql.connector
from sqlalchemy import text

admin = Blueprint('admin', __name__)

@admin.route('/admin')
@login_required
@admin_required
def index():
    """Admin dashboard"""
    return render_template('admin/index.html')

@admin.route('/admin/database', methods=['GET', 'POST'])
@login_required
@admin_required
def database():
    """Database management interface"""
    if request.method == 'POST':
        # Handle database connection update
        db_type = request.form.get('db_type')
        db_host = request.form.get('db_host')
        db_port = request.form.get('db_port')
        db_name = request.form.get('db_name')
        db_user = request.form.get('db_user')
        db_password = request.form.get('db_password')

        # Construct database URI
        if db_type == 'sqlite':
            db_uri = f'sqlite:///{db_name}'
        elif db_type == 'postgresql':
            db_uri = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        elif db_type == 'mysql':
            db_uri = f'mysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        else:
            flash('Invalid database type', 'error')
            return redirect(url_for('admin.database'))

        # Update configuration
        current_app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        
        try:
            # Test connection
            db.engine.connect()
            flash('Database connection updated successfully', 'success')
        except Exception as e:
            flash(f'Failed to connect to database: {str(e)}', 'error')
            return redirect(url_for('admin.database'))

    # Get database statistics
    stats = {
        'users': User.query.count(),
        'projects': Project.query.count(),
        'reports': Report.query.count(),
        'db_size': get_db_size()
    }

    return render_template('admin/database.html', config=current_app.config, stats=stats)

@admin.route('/admin/database/backup', methods=['POST'])
@login_required
@admin_required
def backup_database():
    """Create database backup"""
    try:
        backup_dir = os.path.join(current_app.root_path, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'backup_{timestamp}.sql')
        
        db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
        
        if db_uri.startswith('sqlite'):
            # SQLite backup
            subprocess.run(['sqlite3', db_uri.replace('sqlite:///', ''), f'.backup {backup_file}'])
        elif db_uri.startswith('postgresql'):
            # PostgreSQL backup
            conn_params = parse_postgresql_uri(db_uri)
            subprocess.run([
                'pg_dump',
                f'--host={conn_params["host"]}',
                f'--port={conn_params["port"]}',
                f'--username={conn_params["user"]}',
                f'--dbname={conn_params["dbname"]}',
                f'--file={backup_file}'
            ], env={'PGPASSWORD': conn_params['password']})
        elif db_uri.startswith('mysql'):
            # MySQL backup
            conn_params = parse_mysql_uri(db_uri)
            subprocess.run([
                'mysqldump',
                f'--host={conn_params["host"]}',
                f'--port={conn_params["port"]}',
                f'--user={conn_params["user"]}',
                f'--password={conn_params["password"]}',
                conn_params['dbname'],
                f'--result-file={backup_file}'
            ])
        
        flash('Database backup created successfully', 'success')
    except Exception as e:
        flash(f'Failed to create backup: {str(e)}', 'error')
    
    return redirect(url_for('admin.database'))

@admin.route('/admin/database/restore', methods=['POST'])
@login_required
@admin_required
def restore_database():
    """Restore database from backup"""
    if 'backup_file' not in request.files:
        flash('No backup file selected', 'error')
        return redirect(url_for('admin.database'))
    
    backup_file = request.files['backup_file']
    if backup_file.filename == '':
        flash('No backup file selected', 'error')
        return redirect(url_for('admin.database'))
    
    try:
        # Save uploaded file
        temp_path = os.path.join(current_app.root_path, 'temp', backup_file.filename)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        backup_file.save(temp_path)
        
        db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
        
        if db_uri.startswith('sqlite'):
            # SQLite restore
            subprocess.run(['sqlite3', db_uri.replace('sqlite:///', ''), f'.restore {temp_path}'])
        elif db_uri.startswith('postgresql'):
            # PostgreSQL restore
            conn_params = parse_postgresql_uri(db_uri)
            subprocess.run([
                'psql',
                f'--host={conn_params["host"]}',
                f'--port={conn_params["port"]}',
                f'--username={conn_params["user"]}',
                f'--dbname={conn_params["dbname"]}',
                f'--file={temp_path}'
            ], env={'PGPASSWORD': conn_params['password']})
        elif db_uri.startswith('mysql'):
            # MySQL restore
            conn_params = parse_mysql_uri(db_uri)
            subprocess.run([
                'mysql',
                f'--host={conn_params["host"]}',
                f'--port={conn_params["port"]}',
                f'--user={conn_params["user"]}',
                f'--password={conn_params["password"]}',
                conn_params['dbname'],
                f'< {temp_path}'
            ], shell=True)
        
        # Clean up
        os.remove(temp_path)
        flash('Database restored successfully', 'success')
    except Exception as e:
        flash(f'Failed to restore database: {str(e)}', 'error')
    
    return redirect(url_for('admin.database'))

def get_db_size():
    """Get database size"""
    try:
        db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
        
        if db_uri.startswith('sqlite'):
            # SQLite size
            db_path = db_uri.replace('sqlite:///', '')
            return f"{os.path.getsize(db_path) / 1024 / 1024:.2f} MB"
        elif db_uri.startswith('postgresql'):
            # PostgreSQL size
            result = db.session.execute(text("SELECT pg_size_pretty(pg_database_size(current_database()))")).scalar()
            return result
        elif db_uri.startswith('mysql'):
            # MySQL size
            result = db.session.execute(text("SELECT pg_size_pretty(pg_database_size(current_database()))")).scalar()
            return result
    except Exception:
        return "Unknown"

def parse_postgresql_uri(uri):
    """Parse PostgreSQL connection URI"""
    # Remove 'postgresql://' prefix
    uri = uri.replace('postgresql://', '')
    
    # Split user:pass and host:port/dbname
    auth, rest = uri.split('@')
    user, password = auth.split(':')
    
    # Split host:port and dbname
    host_port, dbname = rest.split('/')
    host, port = host_port.split(':')
    
    return {
        'user': user,
        'password': password,
        'host': host,
        'port': port,
        'dbname': dbname
    }

def parse_mysql_uri(uri):
    """Parse MySQL connection URI"""
    # Remove 'mysql://' prefix
    uri = uri.replace('mysql://', '')
    
    # Split user:pass and host:port/dbname
    auth, rest = uri.split('@')
    user, password = auth.split(':')
    
    # Split host:port and dbname
    host_port, dbname = rest.split('/')
    host, port = host_port.split(':')
    
    return {
        'user': user,
        'password': password,
        'host': host,
        'port': port,
        'dbname': dbname
    } 