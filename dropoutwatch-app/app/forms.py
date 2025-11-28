"""
WTForms for user input validation
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, FloatField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, NumberRange, Length
from app.models import User


class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')


class RegisterForm(FlaskForm):
    """Registration form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
        ('counselor', 'Counselor')
    ], validators=[DataRequired()])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')


class StudentForm(FlaskForm):
    """Student data form"""
    student_id = StringField('Student ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    grade = SelectField('Grade', choices=[
        (9, 'Grade 9'),
        (10, 'Grade 10'),
        (11, 'Grade 11'),
        (12, 'Grade 12')
    ], coerce=int, validators=[DataRequired()])
    section = StringField('Section', validators=[DataRequired()])
    email = StringField('Email', validators=[Email()])
    phone = StringField('Phone')


class AttendanceForm(FlaskForm):
    """Attendance form"""
    date = DateField('Date', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late')
    ], validators=[DataRequired()])


class GradeForm(FlaskForm):
    """Grade entry form"""
    subject = StringField('Subject', validators=[DataRequired()])
    grade_type = SelectField('Type', choices=[
        ('assignment', 'Assignment'),
        ('exam', 'Exam'),
        ('project', 'Project'),
        ('quiz', 'Quiz')
    ], validators=[DataRequired()])
    score = FloatField('Score', validators=[DataRequired(), NumberRange(min=0)])
    max_score = FloatField('Max Score', validators=[DataRequired(), NumberRange(min=0)])
    date = DateField('Date', validators=[DataRequired()])


class CounselingNoteForm(FlaskForm):
    """Counseling note form"""
    note = TextAreaField('Note', validators=[DataRequired(), Length(min=10)])
    concern_level = SelectField('Concern Level', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], validators=[DataRequired()])
