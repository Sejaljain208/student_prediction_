"""
Initialize database with demo users and sample data
"""
from app import create_app
from app.models import db, User, Student, RiskPrediction
from datetime import datetime

def init_demo_data():
    """Initialize database with demo users and sample students"""
    app = create_app()
    
    with app.app_context():
        # Create tables
        db.create_all()
        print("✓ Database tables created")
        
        # Check if users already exist
        if User.query.first():
            print("⚠ Users already exist in database")
            return
        
        # Create demo users
        users = [
            User(
                username='teacher@school.edu',
                email='teacher@school.edu',
                role='teacher',
                password='teacher123'  # Will be hashed by the model
            ),
            User(
                username='admin@school.edu',
                email='admin@school.edu',
                role='admin',
                password='admin123'
            ),
            User(
                username='parent@school.edu',
                email='parent@school.edu',
                role='parent',
                password='parent123'
            )
        ]
        
        for user in users:
            db.session.add(user)
        
        db.session.commit()
        print("✓ Demo users created:")
        print("  - teacher@school.edu / teacher123")
        print("  - admin@school.edu / admin123")
        print("  - parent@school.edu / parent123")
        
        # Create sample students
        sample_students = [
            Student(
                student_id='STU001',
                name='John Doe',
                grade=10,
                section='A',
                age=15,
                gender='M',
                attendance_rate=0.95,
                gpa=3.8,
                parent_education='Bachelor',
                family_income='Medium',
                study_hours_per_week=20,
                extracurricular_activities=2,
                previous_failures=0
            ),
            Student(
                student_id='STU002',
                name='Jane Smith',
                grade=10,
                section='A',
                age=16,
                gender='F',
                attendance_rate=0.88,
                gpa=3.2,
                parent_education='High School',
                family_income='Low',
                study_hours_per_week=15,
                extracurricular_activities=1,
                previous_failures=1
            ),
            Student(
                student_id='STU003',
                name='Mike Johnson',
                grade=11,
                section='B',
                age=17,
                gender='M',
                attendance_rate=0.75,
                gpa=2.5,
                parent_education='High School',
                family_income='Low',
                study_hours_per_week=10,
                extracurricular_activities=0,
                previous_failures=2
            ),
            Student(
                student_id='STU004',
                name='Sarah Williams',
                grade=11,
                section='B',
                age=16,
                gender='F',
                attendance_rate=0.92,
                gpa=3.6,
                parent_education='Master',
                family_income='High',
                study_hours_per_week=25,
                extracurricular_activities=3,
                previous_failures=0
            ),
            Student(
                student_id='STU005',
                name='David Brown',
                grade=12,
                section='C',
                age=18,
                gender='M',
                attendance_rate=0.70,
                gpa=2.2,
                parent_education='No Formal',
                family_income='Low',
                study_hours_per_week=8,
                extracurricular_activities=0,
                previous_failures=3
            )
        ]
        
        for student in sample_students:
            db.session.add(student)
        
        db.session.commit()
        print(f"✓ Created {len(sample_students)} sample students")
        
        # Create sample predictions
        predictions_data = [
            (1, 0.15, 'low', ['High GPA', 'Good Attendance']),
            (2, 0.45, 'medium', ['Previous Failure', 'Low Family Income']),
            (3, 0.78, 'high', ['Low Attendance', 'Multiple Failures', 'Low Study Hours']),
            (4, 0.10, 'low', ['High GPA', 'High Family Income', 'Active in Activities']),
            (5, 0.85, 'high', ['Very Low Attendance', 'Multiple Failures', 'No Activities'])
        ]
        
        for student_id, risk_score, risk_level, factors in predictions_data:
            prediction = RiskPrediction(
                student_id=student_id,
                risk_score=risk_score,
                risk_level=risk_level,
                contributing_factors=factors,
                prediction_date=datetime.utcnow()
            )
            db.session.add(prediction)
        
        db.session.commit()
        print(f"✓ Created {len(predictions_data)} sample predictions")
        
        print("\n✅ Database initialization complete!")
        print("\nYou can now login with:")
        print("  Username: teacher@school.edu")
        print("  Password: teacher123")

if __name__ == '__main__':
    init_demo_data()
