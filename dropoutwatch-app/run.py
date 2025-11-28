"""
Application entry point
Run this file to start the Flask application
"""
from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5001)
