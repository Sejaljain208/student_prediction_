"""
Flask application factory and initialization
"""
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from config import Config
from app.models import db, bcrypt, User

login_manager = LoginManager()
mail = Mail()


def create_app(config_class=Config):
    """Create and configure Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.auth import auth_bp
    from app.dashboard import dashboard_bp
    from app.api import api_bp
    from app.main import main as main_bp
    from app.admin import admin_bp
    from app.analytics import analytics_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp)  # Admin blueprint has its own prefix
    app.register_blueprint(analytics_bp)  # Analytics blueprint has its own prefix
    app.register_blueprint(main_bp)
    
    return app
