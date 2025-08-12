from datetime import datetime
from sqlalchemy import func, event
from pytz import timezone
from flask_login import UserMixin
from extensions import db  

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(255))  
    name = db.Column(db.String(100))  
    type = db.Column(db.String(50), default="User")
    active = db.Column(db.Boolean, default=True)   
    is_locked = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer)
    create_date = db.Column(db.DateTime, default=db.func.current_timestamp())  
    write_date = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __init__(self, username, password, name, write_date, active=True, user_type="user"):
        self.username = username
        self.password = password
        self.name = name
        self.write_date = write_date
        self.active = active
        self.type = user_type