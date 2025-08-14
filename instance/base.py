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

    def __init__(self, username, password, name, write_date, active=True, type="user"):
        self.username = username
        self.password = password
        self.name = name
        self.write_date = write_date
        self.active = active
        self.user_type = type

class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    gross_value = db.Column(db.Float, nullable=False)
    iva_rate = db.Column(db.Float, nullable=False)
    iva_value = db.Column(db.Float, nullable=False)
    net_value = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('expenses', lazy=True))
    create_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    write_date = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    def __init__(self, transaction_type, description, gross_value, iva_rate, iva_value, net_value, user_id):
        self.transaction_type = transaction_type
        self.description = description
        self.gross_value = gross_value
        self.iva_rate = iva_rate
        self.iva_value = iva_value
        self.net_value = net_value
        self.user_id = user_id

class Employee(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    position = db.Column(db.String(100), nullable=False)
    gross_salary = db.Column(db.Float, nullable=False)  
    social_security_rate = db.Column(db.Float, default=0)  
    employer_social_security_rate = db.Column(db.Float, default=0)  
    create_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    write_date = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    def __init__(self, name, gross_salary, position, social_security_rate=0, employer_social_security_rate=0, is_active=True):
        self.name = name
        self.gross_salary = gross_salary
        self.social_security_rate = social_security_rate
        self.employer_social_security_rate = employer_social_security_rate
        self.is_active = is_active
        self.position = position

class MonthlySummary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    total_sales = db.Column(db.Float, default=0.0)
    total_sales_without_vat = db.Column(db.Float, default=0.0)
    total_vat = db.Column(db.Float, default=0.0)
    total_costs = db.Column(db.Float, default=0.0)
    profit = db.Column(db.Float, default=0.0)
    profit_without_vat = db.Column(db.Float, default=0.0)
    create_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    write_date = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    __table_args__ = (
        db.UniqueConstraint('month', 'year', name='_month_year_uc'),
    )
    
    def __init__(self, month, year, total_sales=0.0, total_sales_without_vat=0.0, 
                 total_vat=0.0, total_costs=0.0, profit=0.0, profit_without_vat=0.0):
        self.month = month
        self.year = year
        self.total_sales = total_sales
        self.total_sales_without_vat = total_sales_without_vat
        self.total_vat = total_vat
        self.total_costs = total_costs
        self.profit = profit
        self.profit_without_vat = profit_without_vat