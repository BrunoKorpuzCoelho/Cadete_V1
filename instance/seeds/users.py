from datetime import datetime
from instance.base import User
from instance.base import db

def create_admin():
    """
    Create default admin user with hashed password.
    Password will be automatically hashed by User.__init__()
    """
    cubix = User.query.filter_by(username="cubix").first()
    if not cubix:
        # Password is automatically hashed in User.__init__()
        user = User(
            username="cubix",
            password="cubix",
            name="Administrator",
            type="Admin",
            write_date=datetime.now()
        )
        user.is_locked = False
        user.failed_login_attempts = 0

        db.session.add(user)
        db.session.commit()
        print("✓ Admin user created successfully with hashed password")

def create_basic_user():
    """
    Create default basic user with hashed password.
    Password will be automatically hashed by User.__init__()
    """
    basic_user = User.query.filter_by(username="cadete").first()
    if not basic_user:
        # Password is automatically hashed in User.__init__()
        user = User(
            username="cadete",
            password="cadete",
            name="Basic User",
            type="User",
            write_date=datetime.now()
        )
        user.is_locked = False
        user.failed_login_attempts = 0

        db.session.add(user)
        db.session.commit()
        print("✓ Basic user created successfully with hashed password")

def create_users():
    """Create default users for the system"""
    create_admin()
    create_basic_user()