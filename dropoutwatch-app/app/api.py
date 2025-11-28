"""
API endpoints for data management and predictions
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import db, Student, RiskPrediction
from app.ml_model import predictor
from app.alerts import send_risk_alert
from datetime import datetime

api_bp = Blueprint('api', __name__)


@api_bp.route('/predict/<int:student_id>', methods=['GET'])
@login_required
def predict_student(student_id):
    """Get risk prediction for a specific student"""
    student = Student.query.get_or_404(student_id)
    
    # Get prediction
    result = predictor.predict_risk(student_id)
    
    if not result:
        return jsonify({'error': 'Unable to generate prediction'}), 400
    
    # Save prediction to database
    prediction = RiskPrediction(
        student_id=student_id,
        risk_level=result['risk_level'],
        risk_score=result['risk_score'],
        contributing_factors=result['contributing_factors'],
        model_version='1.0'
    )
    db.session.add(prediction)
    db.session.commit()
    
    # Send alert if medium or high risk
    if result['risk_level'] in ['medium', 'high']:
        send_risk_alert(student, result)
    
    return jsonify({
        'student_id': student_id,
        'student_name': student.name,
        'risk_level': result['risk_level'],
        'risk_score': result['risk_score'],
        'contributing_factors': result['contributing_factors'],
        'ml_probabilities': result['ml_probabilities']
    })


@api_bp.route('/predict/batch', methods=['POST'])
@login_required
def predict_batch():
    """Batch predict for all students"""
    students = Student.query.all()
    results = []
    
    for student in students:
        result = predictor.predict_risk(student.id)
        if result:
            # Save prediction
            prediction = RiskPrediction(
                student_id=student.id,
                risk_level=result['risk_level'],
                risk_score=result['risk_score'],
                contributing_factors=result['contributing_factors'],
                model_version='1.0'
            )
            db.session.add(prediction)
            
            # Send alert if needed
            if result['risk_level'] in ['medium', 'high']:
                send_risk_alert(student, result)
            
            results.append({
                'student_id': student.id,
                'student_name': student.name,
                'risk_level': result['risk_level']
            })
    
    db.session.commit()
    
    return jsonify({
        'total_students': len(students),
        'predictions': results
    })


@api_bp.route('/students', methods=['GET'])
@login_required
def get_students():
    """Get all students with optional filters"""
    grade = request.args.get('grade', type=int)
    risk_level = request.args.get('risk_level')
    
    query = Student.query
    
    if grade:
        query = query.filter_by(grade=grade)
    
    students = query.all()
    
    student_list = []
    for student in students:
        latest_prediction = RiskPrediction.query.filter_by(
            student_id=student.id
        ).order_by(RiskPrediction.prediction_date.desc()).first()
        
        if risk_level and (not latest_prediction or latest_prediction.risk_level != risk_level):
            continue
        
        student_list.append({
            'id': student.id,
            'student_id': student.student_id,
            'name': student.name,
            'grade': student.grade,
            'section': student.section,
            'risk_level': latest_prediction.risk_level if latest_prediction else 'unknown',
            'risk_score': latest_prediction.risk_score if latest_prediction else 0.0
        })
    
    return jsonify({'students': student_list})


@api_bp.route('/risk-summary', methods=['GET'])
@login_required
def risk_summary():
    """Get risk statistics summary"""
    from sqlalchemy import func
    
    # Count students by risk level
    risk_counts = db.session.query(
        RiskPrediction.risk_level,
        func.count(func.distinct(RiskPrediction.student_id))
    ).group_by(RiskPrediction.risk_level).all()
    
    summary = {
        'low': 0,
        'medium': 0,
        'high': 0,
        'total': Student.query.count()
    }
    
    for level, count in risk_counts:
        summary[level] = count
    
    return jsonify(summary)


@api_bp.route('/alerts', methods=['GET'])
@login_required
def get_alerts():
    """Get alert history"""
    student_id = request.args.get('student_id', type=int)
    
    from app.models import Alert
    
    query = Alert.query
    if student_id:
        query = query.filter_by(student_id=student_id)
    
    alerts = query.order_by(Alert.sent_at.desc()).limit(50).all()
    
    alert_list = [{
        'id': alert.id,
        'student_id': alert.student_id,
        'alert_type': alert.alert_type,
        'recipient': alert.recipient,
        'status': alert.status,
        'sent_at': alert.sent_at.isoformat()
    } for alert in alerts]
    
    return jsonify({'alerts': alert_list})
