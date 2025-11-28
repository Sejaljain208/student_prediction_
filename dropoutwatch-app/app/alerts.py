"""
Alert system for sending email and SMS notifications
"""
from flask import current_app
from flask_mail import Message
from app import mail
from app.models import db, Alert
from datetime import datetime
import os


def send_email_alert(student, risk_level, factors):
    """Send email alert to parent"""
    if not student.parent or not student.parent.email:
        print(f"No parent email found for student {student.name}")
        return False
    
    try:
        subject = f"Student Alert: {student.name} - {risk_level.upper()} Dropout Risk"
        
        body = f"""
Dear Parent,

This is an automated alert from DropoutWatch regarding your child, {student.name} (ID: {student.student_id}).

RISK LEVEL: {risk_level.upper()}

Contributing Factors:
{chr(10).join(f'• {factor}' for factor in factors)}

We recommend scheduling a meeting with the school counselor or teacher to discuss support strategies.

Action Steps:
1. Review your child's attendance and grades
2. Contact the school counselor for intervention options
3. Ensure regular communication with teachers
4. Monitor homework and assignment completion

For immediate assistance, please contact:
- School Counselor: counselor@school.edu
- Teacher: teacher@school.edu

Best regards,
DropoutWatch Team
Student Support Services
        """
        
        msg = Message(
            subject=subject,
            recipients=[student.parent.email],
            body=body
        )
        
        mail.send(msg)
        
        # Log alert
        alert = Alert(
            student_id=student.id,
            alert_type='email',
            recipient=student.parent.email,
            message=body,
            status='sent',
            sent_at=datetime.utcnow()
        )
        db.session.add(alert)
        db.session.commit()
        
        print(f"Email alert sent to {student.parent.email}")
        return True
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        
        # Log failed alert
        alert = Alert(
            student_id=student.id,
            alert_type='email',
            recipient=student.parent.email if student.parent else 'unknown',
            message=f"Failed to send: {str(e)}",
            status='failed',
            sent_at=datetime.utcnow()
        )
        db.session.add(alert)
        db.session.commit()
        
        return False


def send_sms_alert(student, risk_level):
    """Send SMS alert to parent via Twilio"""
    if not student.phone:
        print(f"No phone number found for student {student.name}")
        return False
    
    # Check if Twilio credentials are configured
    twilio_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
    twilio_token = current_app.config.get('TWILIO_AUTH_TOKEN')
    twilio_phone = current_app.config.get('TWILIO_PHONE_NUMBER')
    
    if not all([twilio_sid, twilio_token, twilio_phone]):
        print("Twilio credentials not configured. SMS alert will be logged only.")
        
        # Log mock SMS
        message_body = f"Alert: {student.name} is at {risk_level.upper()} dropout risk. Please contact school."
        
        alert = Alert(
            student_id=student.id,
            alert_type='sms',
            recipient=student.phone,
            message=message_body,
            status='pending',
            sent_at=datetime.utcnow()
        )
        db.session.add(alert)
        db.session.commit()
        
        print(f"[MOCK SMS] To: {student.phone} - {message_body}")
        return True
    
    try:
        from twilio.rest import Client
        
        client = Client(twilio_sid, twilio_token)
        
        message_body = f"Alert: {student.name} is at {risk_level.upper()} dropout risk. Please contact school counselor."
        
        message = client.messages.create(
            body=message_body,
            from_=twilio_phone,
            to=student.phone
        )
        
        # Log alert
        alert = Alert(
            student_id=student.id,
            alert_type='sms',
            recipient=student.phone,
            message=message_body,
            status='sent' if message.status != 'failed' else 'failed',
            sent_at=datetime.utcnow()
        )
        db.session.add(alert)
        db.session.commit()
        
        print(f"SMS alert sent to {student.phone}")
        return True
        
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        
        # Log failed alert
        alert = Alert(
            student_id=student.id,
            alert_type='sms',
            recipient=student.phone,
            message=f"Failed to send: {str(e)}",
            status='failed',
            sent_at=datetime.utcnow()
        )
        db.session.add(alert)
        db.session.commit()
        
        return False


def notify_counselor(student, prediction):
    """Notify counselor about high-risk student"""
    from app.models import User
    
    counselors = User.query.filter_by(role='counselor').all()
    
    for counselor in counselors:
        try:
            subject = f"High Risk Alert: {student.name}"
            
            body = f"""
Dear Counselor,

A student has been identified as HIGH RISK for dropout:

Student: {student.name} (ID: {student.student_id})
Grade: {student.grade}
Risk Score: {prediction.risk_score:.2f}

Contributing Factors:
{chr(10).join(f'• {factor}' for factor in prediction.contributing_factors)}

Please schedule an intervention meeting as soon as possible.

View full details in the DropoutWatch dashboard.

Best regards,
DropoutWatch System
            """
            
            msg = Message(
                subject=subject,
                recipients=[counselor.email],
                body=body
            )
            
            mail.send(msg)
            print(f"Counselor notification sent to {counselor.email}")
            
        except Exception as e:
            print(f"Error notifying counselor: {str(e)}")


def send_risk_alert(student, prediction_result):
    """Send appropriate alerts based on risk level"""
    risk_level = prediction_result['risk_level']
    factors = prediction_result['contributing_factors']
    
    if risk_level in ['medium', 'high']:
        # Send email to parent
        send_email_alert(student, risk_level, factors)
        
        # Send SMS to parent
        send_sms_alert(student, risk_level)
        
        # Notify counselor for high risk
        if risk_level == 'high':
            from app.models import RiskPrediction
            prediction = RiskPrediction.query.filter_by(
                student_id=student.id
            ).order_by(RiskPrediction.prediction_date.desc()).first()
            
            if prediction:
                notify_counselor(student, prediction)
