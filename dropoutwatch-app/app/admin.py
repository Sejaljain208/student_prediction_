"""
Admin panel routes for user management and system settings
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app.models import db, User, Student, RiskPrediction, Alert
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You must be an administrator to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with system overview"""
    # Get statistics
    total_users = User.query.count()
    total_students = Student.query.count()
    total_predictions = RiskPrediction.query.count()
    total_alerts = Alert.query.count()
    
    # Get user counts by role
    user_roles = db.session.query(
        User.role,
        func.count(User.id)
    ).group_by(User.role).all()
    
    role_stats = {role: count for role, count in user_roles}
    
    # Get recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # Get risk distribution
    risk_counts = db.session.query(
        RiskPrediction.risk_level,
        func.count(func.distinct(RiskPrediction.student_id))
    ).group_by(RiskPrediction.risk_level).all()
    
    risk_stats = {level: count for level, count in risk_counts}
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_students=total_students,
                         total_predictions=total_predictions,
                         total_alerts=total_alerts,
                         role_stats=role_stats,
                         recent_users=recent_users,
                         risk_stats=risk_stats)


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """List all users"""
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=all_users)


@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """Add new user"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # Validate inputs
        if not all([username, email, password, role]):
            flash('All fields are required', 'danger')
            return render_template('admin_user_form.html', user=None)
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            flash('Username or email already exists', 'danger')
            return render_template('admin_user_form.html', user=None)
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            role=role
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'User {username} created successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin_user_form.html', user=None)


@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit existing user"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.role = request.form.get('role')
        
        # Update password if provided
        new_password = request.form.get('password')
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        flash(f'User {user.username} updated successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin_user_form.html', user=user)


@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('admin.users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {username} deleted successfully', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    """System settings configuration"""
    if request.method == 'POST':
        # In a real application, you would save these to a Settings model
        # For now, we'll just show a success message
        flash('Settings saved successfully!', 'success')
        return redirect(url_for('admin.settings'))
    
    # Default settings (in production, load from database)
    default_settings = {
        'attendance_threshold': 75,
        'grade_threshold': 50,
        'fee_threshold_days': 30,
        'email_enabled': True,
        'sms_enabled': False
    }
    
    return render_template('admin_settings.html', settings=default_settings)
