"""
Dashboard routes for different user roles
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app.models import db, Student, RiskPrediction, Alert
from app.ml_model import predictor
from sqlalchemy import func
import pandas as pd
import os
from werkzeug.utils import secure_filename

dashboard_bp = Blueprint('dashboard', __name__)


def role_required(role):
    """Decorator to require specific user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@dashboard_bp.route('/teacher')
@login_required
@role_required('teacher')
def teacher():
    """Teacher dashboard - view all students and risk levels"""
    # Get all students sorted alphabetically by name
    students = Student.query.order_by(Student.name).all()
    
    # Get latest risk predictions for each student
    student_data = []
    for student in students:
        latest_prediction = RiskPrediction.query.filter_by(
            student_id=student.id
        ).order_by(RiskPrediction.prediction_date.desc()).first()
        
        # Get attendance data
        from app.models import Attendance, Grade
        latest_attendance = Attendance.query.filter_by(
            student_id=student.id
        ).order_by(Attendance.date.desc()).first()
        
        # Calculate attendance statistics
        all_attendance = Attendance.query.filter_by(student_id=student.id).all()
        if all_attendance:
            total_records = len(all_attendance)
            present_count = sum(1 for a in all_attendance if a.status == 'present')
            attendance_percentage = (present_count / total_records * 100) if total_records > 0 else 0
        else:
            attendance_percentage = 0
            total_records = 0
            present_count = 0
        
        # Get recent attendance records (last 10)
        recent_attendance = Attendance.query.filter_by(
            student_id=student.id
        ).order_by(Attendance.date.desc()).limit(10).all()
        
        # Get grades data
        all_grades = Grade.query.filter_by(student_id=student.id).all()
        
        # Calculate grade statistics by subject
        grade_stats = {}
        if all_grades:
            subjects = set(g.subject for g in all_grades)
            for subject in subjects:
                subject_grades = [g for g in all_grades if g.subject == subject]
                avg_score = sum(g.percentage for g in subject_grades) / len(subject_grades)
                grade_stats[subject] = {
                    'average': round(avg_score, 2),
                    'count': len(subject_grades)
                }
            
            # Overall average
            overall_avg = sum(g.percentage for g in all_grades) / len(all_grades)
        else:
            overall_avg = 0
        
        # Get recent grades (last 5)
        recent_grades = Grade.query.filter_by(
            student_id=student.id
        ).order_by(Grade.date.desc()).limit(5).all()
        
        student_data.append({
            'student': student,
            'prediction': latest_prediction,
            'attendance': {
                'percentage': round(attendance_percentage, 2),
                'total_days': total_records,
                'present_days': present_count,
                'recent_records': recent_attendance
            },
            'grades': {
                'overall_average': round(overall_avg, 2),
                'by_subject': grade_stats,
                'recent_grades': recent_grades
            }
        })
    
    # Calculate statistics
    total_students = len(students)
    
    # Get risk counts from latest predictions only (one per student)
    risk_stats = {
        'low': 0,
        'medium': 0,
        'high': 0
    }
    
    for item in student_data:
        if item['prediction']:
            risk_level = item['prediction'].risk_level
            if risk_level in risk_stats:
                risk_stats[risk_level] += 1
    
    return render_template('teacher_dashboard.html',
                         student_data=student_data,
                         total_students=total_students,
                         risk_stats=risk_stats)


@dashboard_bp.route('/student/<int:student_id>')
@login_required
def student_detail(student_id):
    """Student detail view with all data and risk factors"""
    student = Student.query.get_or_404(student_id)
    
    # Check permissions
    if current_user.role == 'parent' and student.parent_id != current_user.id:
        flash('You can only view your own child\'s data.', 'danger')
        return redirect(url_for('dashboard.parent'))
    
    # Get latest prediction
    prediction = RiskPrediction.query.filter_by(
        student_id=student_id
    ).order_by(RiskPrediction.prediction_date.desc()).first()
    
    # Get all related data
    attendance_records = student.attendance_records
    grades = student.grades
    activities = student.activities
    fees = student.fees
    counseling_notes = student.counseling_notes
    alerts = student.alerts
    
    return render_template('student_detail.html',
                         student=student,
                         prediction=prediction,
                         attendance_records=attendance_records,
                         grades=grades,
                         activities=activities,
                         fees=fees,
                         counseling_notes=counseling_notes,
                         alerts=alerts)


@dashboard_bp.route('/parent')
@login_required
@role_required('parent')
def parent():
    """Parent dashboard - view their children's data"""
    children = Student.query.filter_by(parent_id=current_user.id).all()
    
    children_data = []
    for child in children:
        latest_prediction = RiskPrediction.query.filter_by(
            student_id=child.id
        ).order_by(RiskPrediction.prediction_date.desc()).first()
        
        children_data.append({
            'student': child,
            'prediction': latest_prediction
        })
    
    return render_template('parent_dashboard.html', children_data=children_data)


@dashboard_bp.route('/counselor')
@login_required
@role_required('counselor')
def counselor():
    """Counselor dashboard - focus on high-risk students"""
    # Get high-risk students
    high_risk_predictions = RiskPrediction.query.filter_by(
        risk_level='high'
    ).order_by(RiskPrediction.risk_score.desc()).all()
    
    high_risk_students = []
    for pred in high_risk_predictions:
        high_risk_students.append({
            'student': pred.student,
            'prediction': pred
        })
    
    # Get medium-risk students
    medium_risk_predictions = RiskPrediction.query.filter_by(
        risk_level='medium'
    ).order_by(RiskPrediction.risk_score.desc()).all()
    
    medium_risk_students = []
    for pred in medium_risk_predictions:
        medium_risk_students.append({
            'student': pred.student,
            'prediction': pred
        })
    
    return render_template('counselor_dashboard.html',
                         high_risk_students=high_risk_students,
                         medium_risk_students=medium_risk_students)


@dashboard_bp.route('/teacher/upload-csv')
@login_required
@role_required('teacher')
def upload_csv_form():
    """Display CSV upload form"""
    return render_template('upload_students.html')


@dashboard_bp.route('/teacher/upload-csv', methods=['POST'])
@login_required
@role_required('teacher')
def upload_csv():
    """Process CSV file upload and create students"""
    if 'file' not in request.files:
        flash('No file uploaded', 'danger')
        return redirect(url_for('dashboard.upload_csv_form'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('dashboard.upload_csv_form'))
    
    if not file.filename.endswith('.csv'):
        flash('Please upload a CSV file', 'danger')
        return redirect(url_for('dashboard.upload_csv_form'))
    
    try:
        # Read CSV file
        df = pd.read_csv(file)
        
        # Validate required columns
        required_columns = [
            'student_id', 'name', 'grade', 'section', 'email', 'phone',
            'age', 'gender', 'attendance_rate', 'gpa', 'parent_education',
            'family_income', 'study_hours_per_week', 'extracurricular_activities',
            'previous_failures'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            flash(f'Missing required columns: {", ".join(missing_columns)}', 'danger')
            return redirect(url_for('dashboard.upload_csv_form'))
        
        # Process each row
        students_created = 0
        students_skipped = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Check if student already exists
                existing_student = Student.query.filter_by(student_id=row['student_id']).first()
                if existing_student:
                    students_skipped += 1
                    continue
                
                # Create new student
                student = Student(
                    student_id=row['student_id'],
                    name=row['name'],
                    grade=int(row['grade']),
                    section=row['section'],
                    email=row['email'] if pd.notna(row['email']) else None,
                    phone=row['phone'] if pd.notna(row['phone']) else None
                )
                
                db.session.add(student)
                db.session.flush()  # Get student ID
                
                # Create attendance record
                from app.models import Attendance
                from datetime import date
                
                attendance = Attendance(
                    student_id=student.id,
                    date=date.today(),
                    status='present',
                    attendance_percentage=float(row['attendance_rate']) * 100
                )
                db.session.add(attendance)
                
                # Create grade records (sample data)
                from app.models import Grade
                
                # Create a few sample grades based on GPA
                gpa = float(row['gpa'])
                avg_score = (gpa / 4.0) * 100  # Convert GPA to percentage
                
                for subject in ['Math', 'Science', 'English']:
                    grade = Grade(
                        student_id=student.id,
                        subject=subject,
                        grade_type='exam',
                        score=avg_score,
                        max_score=100,
                        date=date.today()
                    )
                    db.session.add(grade)
                
                # Create activity record if applicable
                if int(row['extracurricular_activities']) > 0:
                    from app.models import Activity
                    activity = Activity(
                        student_id=student.id,
                        activity_name='Sports/Clubs',
                        participation_level='active',
                        hours_per_week=float(row['extracurricular_activities']) * 2
                    )
                    db.session.add(activity)
                
                # Create fee record (sample data)
                from app.models import Fee
                from datetime import timedelta
                
                fee = Fee(
                    student_id=student.id,
                    total_fees=5000.0,
                    paid_amount=5000.0,  # Assume paid for now
                    due_date=date.today() + timedelta(days=30)
                )
                db.session.add(fee)
                
                students_created += 1
                
            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")
                continue
        
        # Commit all changes
        db.session.commit()
        
        # Run batch prediction for new students
        if students_created > 0:
            try:
                # Get all students and run predictions
                all_students = Student.query.all()
                for student in all_students:
                    # Check if prediction already exists
                    existing_pred = RiskPrediction.query.filter_by(student_id=student.id).first()
                    if not existing_pred:
                        result = predictor.predict_risk(student.id)
                        if result:
                            prediction = RiskPrediction(
                                student_id=student.id,
                                risk_level=result['risk_level'],
                                risk_score=result['risk_score'],
                                contributing_factors=result['contributing_factors'],
                                model_version='1.0'
                            )
                            db.session.add(prediction)
                
                db.session.commit()
            except Exception as e:
                flash(f'Students created but prediction failed: {str(e)}', 'warning')
        
        # Show results
        if students_created > 0:
            flash(f'Successfully imported {students_created} students!', 'success')
        if students_skipped > 0:
            flash(f'{students_skipped} students skipped (already exist)', 'info')
        if errors:
            flash(f'Errors encountered: {"; ".join(errors[:5])}', 'warning')
        
        return redirect(url_for('dashboard.teacher'))
        
    except Exception as e:
        flash(f'Error processing CSV file: {str(e)}', 'danger')
        return redirect(url_for('dashboard.upload_csv_form'))
