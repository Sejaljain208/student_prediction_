"""
Generate synthetic student data for demonstration
Creates realistic student records with various risk profiles
"""
import random
import numpy as np
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Student, Attendance, Grade, Activity, Fee, CounselingNote

# Create app context
app = create_app()


def generate_demo_data(num_students=60):
    """Generate demo student data"""
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Create users
        print("Creating users...")
        
        # Admin
        admin = User(username='admin', email='admin@dropoutwatch.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Teachers
        teacher1 = User(username='teacher1', email='teacher1@school.edu', role='teacher')
        teacher1.set_password('teacher123')
        db.session.add(teacher1)
        
        teacher2 = User(username='teacher2', email='teacher2@school.edu', role='teacher')
        teacher2.set_password('teacher123')
        db.session.add(teacher2)
        
        # Counselor
        counselor = User(username='counselor1', email='counselor@school.edu', role='counselor')
        counselor.set_password('counselor123')
        db.session.add(counselor)
        
        # Parents (will create with students)
        parents = []
        for i in range(num_students):
            parent = User(
                username=f'parent{i+1}',
                email=f'parent{i+1}@example.com',
                role='parent'
            )
            parent.set_password('parent123')
            db.session.add(parent)
            parents.append(parent)
        
        db.session.commit()
        print(f"Created {len(parents) + 4} users")
        
        # Create students
        print(f"Creating {num_students} students...")
        students = []
        
        first_names = ['John', 'Emma', 'Michael', 'Sophia', 'William', 'Olivia', 'James', 'Ava', 
                      'Robert', 'Isabella', 'David', 'Mia', 'Joseph', 'Charlotte', 'Daniel', 'Amelia',
                      'Matthew', 'Harper', 'Christopher', 'Evelyn', 'Andrew', 'Abigail', 'Joshua', 'Emily']
        
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                     'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
                     'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Thompson', 'White']
        
        sections = ['A', 'B', 'C', 'D']
        
        for i in range(num_students):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            grade = random.choice([9, 10, 11, 12])
            section = random.choice(sections)
            
            student = Student(
                student_id=f"S2024{str(i+1).zfill(3)}",
                name=name,
                grade=grade,
                section=section,
                email=f"student{i+1}@school.edu",
                phone=f"+1555{str(random.randint(1000000, 9999999))}",
                parent_id=parents[i].id
            )
            db.session.add(student)
            students.append(student)
        
        db.session.commit()
        print(f"Created {len(students)} students")
        
        # Generate attendance data
        print("Generating attendance data...")
        start_date = datetime.now() - timedelta(days=90)
        
        for student in students:
            # Determine risk profile (30% high, 30% medium, 40% low)
            risk_profile = random.choices(['low', 'medium', 'high'], weights=[40, 30, 30])[0]
            
            if risk_profile == 'high':
                attendance_rate = random.uniform(0.50, 0.74)  # Below 75%
            elif risk_profile == 'medium':
                attendance_rate = random.uniform(0.75, 0.85)
            else:
                attendance_rate = random.uniform(0.85, 0.98)
            
            total_days = 90
            present_days = int(total_days * attendance_rate)
            
            for day in range(total_days):
                date = start_date + timedelta(days=day)
                if date.weekday() < 5:  # Monday to Friday
                    status = 'present' if random.random() < attendance_rate else 'absent'
                    
                    attendance = Attendance(
                        student_id=student.id,
                        date=date.date(),
                        status=status,
                        total_days=day + 1,
                        present_days=present_days if day == total_days - 1 else int((day + 1) * attendance_rate),
                        attendance_percentage=attendance_rate * 100
                    )
                    db.session.add(attendance)
        
        db.session.commit()
        print("Attendance data generated")
        
        # Generate grades
        print("Generating grade data...")
        subjects = ['Mathematics', 'English', 'Science', 'History', 'Physics', 'Chemistry']
        
        for student in students:
            # Use same risk profile
            attendance_record = Attendance.query.filter_by(student_id=student.id).first()
            attendance_rate = attendance_record.attendance_percentage / 100 if attendance_record else 0.9
            
            if attendance_rate < 0.75:
                avg_score = random.uniform(40, 65)  # Lower grades for low attendance
            elif attendance_rate < 0.85:
                avg_score = random.uniform(60, 80)
            else:
                avg_score = random.uniform(75, 95)
            
            for subject in subjects:
                # Assignments
                for _ in range(random.randint(5, 10)):
                    score = max(0, min(100, random.gauss(avg_score, 10)))
                    grade = Grade(
                        student_id=student.id,
                        subject=subject,
                        grade_type='assignment',
                        score=score,
                        max_score=100,
                        date=(datetime.now() - timedelta(days=random.randint(1, 90))).date()
                    )
                    db.session.add(grade)
                
                # Exams
                for _ in range(2):
                    score = max(0, min(100, random.gauss(avg_score, 15)))
                    grade = Grade(
                        student_id=student.id,
                        subject=subject,
                        grade_type='exam',
                        score=score,
                        max_score=100,
                        date=(datetime.now() - timedelta(days=random.randint(1, 90))).date()
                    )
                    db.session.add(grade)
                
                # Projects
                score = max(0, min(100, random.gauss(avg_score, 12)))
                grade = Grade(
                    student_id=student.id,
                    subject=subject,
                    grade_type='project',
                    score=score,
                    max_score=100,
                    date=(datetime.now() - timedelta(days=random.randint(1, 90))).date()
                )
                db.session.add(grade)
        
        db.session.commit()
        print("Grade data generated")
        
        # Generate activities
        print("Generating activity data...")
        activity_names = ['Sports', 'Music', 'Drama', 'Debate', 'Art', 'Robotics', 'Volunteer Work']
        participation_levels = ['active', 'moderate', 'low', 'none']
        
        for student in students:
            num_activities = random.randint(0, 3)
            for _ in range(num_activities):
                activity = Activity(
                    student_id=student.id,
                    activity_name=random.choice(activity_names),
                    participation_level=random.choice(participation_levels),
                    hours_per_week=random.uniform(1, 10)
                )
                db.session.add(activity)
        
        db.session.commit()
        print("Activity data generated")
        
        # Generate fees
        print("Generating fee data...")
        for student in students:
            total_fees = random.choice([5000, 7500, 10000, 12000])
            paid_ratio = random.uniform(0.3, 1.0)
            
            fee = Fee(
                student_id=student.id,
                total_fees=total_fees,
                paid_amount=total_fees * paid_ratio,
                due_date=(datetime.now() + timedelta(days=random.randint(-30, 60))).date()
            )
            db.session.add(fee)
        
        db.session.commit()
        print("Fee data generated")
        
        # Generate counseling notes
        print("Generating counseling notes...")
        concern_notes = {
            'low': ['Regular check-in', 'Positive progress', 'No concerns'],
            'medium': ['Attendance concerns', 'Grade improvement needed', 'Family issues mentioned'],
            'high': ['Severe attendance issues', 'Failing multiple subjects', 'Behavioral problems', 'Depression indicators']
        }
        
        for student in students:
            num_notes = random.randint(0, 3)
            for _ in range(num_notes):
                concern_level = random.choice(['low', 'medium', 'high'])
                note = CounselingNote(
                    student_id=student.id,
                    counselor_id=counselor.id,
                    note=random.choice(concern_notes[concern_level]),
                    concern_level=concern_level,
                    date=datetime.now() - timedelta(days=random.randint(1, 90))
                )
                db.session.add(note)
        
        db.session.commit()
        print("Counseling notes generated")
        
        print(f"\n✅ Demo data generation complete!")
        print(f"   - {num_students} students")
        print(f"   - {len(parents) + 4} users (admin, teachers, counselor, parents)")
        print(f"   - Attendance, grades, activities, fees, and counseling notes")
        print(f"\nLogin credentials:")
        print(f"   Admin: admin / admin123")
        print(f"   Teacher: teacher1 / teacher123")
        print(f"   Counselor: counselor1 / counselor123")
        print(f"   Parent: parent1 / parent123 (and parent2, parent3, etc.)")


if __name__ == '__main__':
    generate_demo_data(60)
