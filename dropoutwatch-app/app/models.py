"""
Database models for DropoutWatch application
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # teacher, parent, counselor, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    counseling_notes = db.relationship('CounselingNote', backref='counselor', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if password matches hash"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Student(db.Model):
    """Student model"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.Integer, nullable=False)  # 9-12
    section = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    parent_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    parent = db.relationship('User', backref='children', foreign_keys=[parent_id])
    attendance_records = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')
    grades = db.relationship('Grade', backref='student', lazy=True, cascade='all, delete-orphan')
    activities = db.relationship('Activity', backref='student', lazy=True, cascade='all, delete-orphan')
    fees = db.relationship('Fee', backref='student', lazy=True, cascade='all, delete-orphan')
    counseling_notes = db.relationship('CounselingNote', backref='student', lazy=True, cascade='all, delete-orphan')
    risk_predictions = db.relationship('RiskPrediction', backref='student', lazy=True, cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Student {self.student_id}: {self.name}>'


class Attendance(db.Model):
    """Attendance records"""
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # present, absent, late
    total_days = db.Column(db.Integer, default=0)
    present_days = db.Column(db.Integer, default=0)
    attendance_percentage = db.Column(db.Float, default=0.0)
    
    def __repr__(self):
        return f'<Attendance {self.student_id} on {self.date}: {self.status}>'


class Grade(db.Model):
    """Grade records"""
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    grade_type = db.Column(db.String(20), nullable=False)  # assignment, exam, project, quiz
    score = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    @property
    def percentage(self):
        """Calculate percentage score"""
        return (self.score / self.max_score) * 100 if self.max_score > 0 else 0
    
    def __repr__(self):
        return f'<Grade {self.student_id} {self.subject} {self.grade_type}: {self.score}/{self.max_score}>'


class Activity(db.Model):
    """Extracurricular activities"""
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    activity_name = db.Column(db.String(100), nullable=False)
    participation_level = db.Column(db.String(20), nullable=False)  # active, moderate, low, none
    hours_per_week = db.Column(db.Float, default=0.0)
    
    def __repr__(self):
        return f'<Activity {self.student_id}: {self.activity_name}>'


class Fee(db.Model):
    """Fee records"""
    __tablename__ = 'fees'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    total_fees = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, default=0.0)
    due_date = db.Column(db.Date, nullable=False)
    
    @property
    def outstanding_amount(self):
        """Calculate outstanding fees"""
        return self.total_fees - self.paid_amount
    
    @property
    def is_overdue(self):
        """Check if fees are overdue"""
        return datetime.now().date() > self.due_date and self.outstanding_amount > 0
    
    @property
    def outstanding_ratio(self):
        """Calculate outstanding fees ratio"""
        return self.outstanding_amount / self.total_fees if self.total_fees > 0 else 0
    
    def __repr__(self):
        return f'<Fee {self.student_id}: {self.outstanding_amount}/{self.total_fees}>'


class CounselingNote(db.Model):
    """Counseling notes"""
    __tablename__ = 'counseling_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    counselor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    note = db.Column(db.Text, nullable=False)
    concern_level = db.Column(db.String(10), nullable=False)  # low, medium, high
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CounselingNote {self.student_id} by {self.counselor_id}>'


class RiskPrediction(db.Model):
    """Risk prediction records"""
    __tablename__ = 'risk_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    risk_level = db.Column(db.String(10), nullable=False)  # low, medium, high
    risk_score = db.Column(db.Float, nullable=False)  # 0.0 - 1.0
    contributing_factors = db.Column(db.JSON)  # List of reasons
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)
    model_version = db.Column(db.String(20), default='1.0')
    
    def __repr__(self):
        return f'<RiskPrediction {self.student_id}: {self.risk_level} ({self.risk_score:.2f})>'


class Alert(db.Model):
    """Alert notification records"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    alert_type = db.Column(db.String(10), nullable=False)  # email, sms
    recipient = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # sent, failed, pending
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Alert {self.alert_type} to {self.recipient}: {self.status}>'
