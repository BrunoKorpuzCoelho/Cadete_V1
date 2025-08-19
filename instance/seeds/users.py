from datetime import datetime
from instance.base import User
from instance.base import db

def create_admin():
    cubix = User.query.filter_by(username="cubix").first()
    if not cubix:
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

def create_basic_user():
    basic_user = User.query.filter_by(username="user").first()
    if not basic_user:
        user = User(
            username="user",
            password="user",  
            name="Basic User",
            type="User",
            write_date=datetime.now()
        )
        user.is_locked = False
        user.failed_login_attempts = 0
        
        db.session.add(user)
        db.session.commit()

def create_users():
    create_admin()
    create_basic_user()