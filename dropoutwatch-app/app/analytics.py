"""
Analytics routes for comprehensive data visualization
"""
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models import db, Student, RiskPrediction, Attendance, Grade, Fee
from sqlalchemy import func
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


@analytics_bp.route('/')
@login_required
def index():
    """Main analytics dashboard"""
    # Only teachers and admins can access analytics
    if current_user.role not in ['teacher', 'admin']:
        from flask import flash, redirect, url_for
        flash('You do not have permission to access analytics.', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('analytics.html')


@analytics_bp.route('/data/risk-distribution')
@login_required
def risk_distribution():
    """API endpoint for risk distribution data"""
    risk_counts = db.session.query(
        RiskPrediction.risk_level,
        func.count(func.distinct(RiskPrediction.student_id))
    ).group_by(RiskPrediction.risk_level).all()
    
    data = {
        'labels': [level.capitalize() for level, _ in risk_counts],
        'values': [count for _, count in risk_counts],
        'colors': {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#dc3545'
        }
    }
    
    return jsonify(data)


@analytics_bp.route('/data/risk-by-grade')
@login_required
def risk_by_grade():
    """API endpoint for risk distribution by grade level"""
    # Get students with their latest predictions
    results = db.session.query(
        Student.grade,
        RiskPrediction.risk_level,
        func.count(Student.id)
    ).join(
        RiskPrediction,
        Student.id == RiskPrediction.student_id
    ).group_by(
        Student.grade,
        RiskPrediction.risk_level
    ).all()
    
    # Organize data by grade
    grades = {}
    for grade, risk_level, count in results:
        if grade not in grades:
            grades[grade] = {'low': 0, 'medium': 0, 'high': 0}
        grades[grade][risk_level] = count
    
    data = {
        'labels': [f'Grade {g}' for g in sorted(grades.keys())],
        'datasets': [
            {
                'label': 'Low Risk',
                'data': [grades[g]['low'] for g in sorted(grades.keys())],
                'backgroundColor': '#28a745'
            },
            {
                'label': 'Medium Risk',
                'data': [grades[g]['medium'] for g in sorted(grades.keys())],
                'backgroundColor': '#ffc107'
            },
            {
                'label': 'High Risk',
                'data': [grades[g]['high'] for g in sorted(grades.keys())],
                'backgroundColor': '#dc3545'
            }
        ]
    }
    
    return jsonify(data)


@analytics_bp.route('/data/attendance-vs-risk')
@login_required
def attendance_vs_risk():
    """API endpoint for attendance vs risk scatter plot"""
    # Get students with attendance and risk data
    results = db.session.query(
        Attendance.attendance_percentage,
        RiskPrediction.risk_score,
        RiskPrediction.risk_level
    ).join(
        Student,
        Attendance.student_id == Student.id
    ).join(
        RiskPrediction,
        Student.id == RiskPrediction.student_id
    ).all()
    
    # Organize by risk level
    data_by_risk = {'low': [], 'medium': [], 'high': []}
    for attendance, risk_score, risk_level in results:
        data_by_risk[risk_level].append({
            'x': attendance,
            'y': risk_score * 100
        })
    
    data = {
        'datasets': [
            {
                'label': 'Low Risk',
                'data': data_by_risk['low'],
                'backgroundColor': 'rgba(40, 167, 69, 0.6)',
                'borderColor': '#28a745'
            },
            {
                'label': 'Medium Risk',
                'data': data_by_risk['medium'],
                'backgroundColor': 'rgba(255, 193, 7, 0.6)',
                'borderColor': '#ffc107'
            },
            {
                'label': 'High Risk',
                'data': data_by_risk['high'],
                'backgroundColor': 'rgba(220, 53, 69, 0.6)',
                'borderColor': '#dc3545'
            }
        ]
    }
    
    return jsonify(data)


@analytics_bp.route('/data/contributing-factors')
@login_required
def contributing_factors():
    """API endpoint for top contributing factors"""
    # Get all predictions with factors
    predictions = RiskPrediction.query.filter(
        RiskPrediction.risk_level.in_(['medium', 'high'])
    ).all()
    
    # Count factor occurrences
    factor_counts = {}
    for pred in predictions:
        if pred.contributing_factors:
            for factor in pred.contributing_factors:
                factor_counts[factor] = factor_counts.get(factor, 0) + 1
    
    # Sort by count and get top 10
    sorted_factors = sorted(factor_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    data = {
        'labels': [factor for factor, _ in sorted_factors],
        'values': [count for _, count in sorted_factors]
    }
    
    return jsonify(data)


@analytics_bp.route('/data/summary-stats')
@login_required
def summary_stats():
    """API endpoint for summary statistics"""
    total_students = Student.query.count()
    
    risk_counts = db.session.query(
        RiskPrediction.risk_level,
        func.count(func.distinct(RiskPrediction.student_id))
    ).group_by(RiskPrediction.risk_level).all()
    
    risk_stats = {level: count for level, count in risk_counts}
    
    # Calculate average attendance
    avg_attendance = db.session.query(
        func.avg(Attendance.attendance_percentage)
    ).scalar() or 0
    
    # Calculate average grade
    avg_grade = db.session.query(
        func.avg(Grade.score / Grade.max_score * 100)
    ).scalar() or 0
    
    data = {
        'total_students': total_students,
        'low_risk': risk_stats.get('low', 0),
        'medium_risk': risk_stats.get('medium', 0),
        'high_risk': risk_stats.get('high', 0),
        'avg_attendance': round(avg_attendance, 1),
        'avg_grade': round(avg_grade, 1)
    }
    
    return jsonify(data)
