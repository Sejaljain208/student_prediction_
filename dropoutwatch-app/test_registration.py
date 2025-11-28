"""
Test script to verify user registration persistence
"""
from app import create_app
from app.models import db, User

app = create_app()

with app.app_context():
    # Query all users
    users = User.query.all()
    
    print(f"\n{'='*60}")
    print(f"Total users in database: {len(users)}")
    print(f"{'='*60}\n")
    
    for user in users:
        print(f"ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print(f"Created: {user.created_at}")
        print(f"{'-'*60}")
    
    # Test login for a specific user
    test_username = "testuser123"
    test_user = User.query.filter_by(username=test_username).first()
    
    if test_user:
        print(f"\n✅ User '{test_username}' found in database!")
        print(f"   Email: {test_user.email}")
        print(f"   Role: {test_user.role}")
        
        # Test password check
        if test_user.check_password("test1234"):
            print(f"   ✅ Password verification successful!")
        else:
            print(f"   ❌ Password verification failed!")
    else:
        print(f"\n❌ User '{test_username}' not found in database.")
    
    print(f"\n{'='*60}")
    print("Registration persistence test complete!")
    print(f"{'='*60}\n")
