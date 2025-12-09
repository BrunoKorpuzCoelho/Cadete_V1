import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

# Get the base directory of the application
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration"""

    # Flask Secret Key
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY not set in environment variables. Please create a .env file.")

    # Database Configuration
    # Convert relative path from env to absolute path
    db_uri = os.environ.get('DATABASE_URI', 'sqlite:///instance/test.db')
    if db_uri.startswith('sqlite:///') and not db_uri.startswith('sqlite:////'):
        # Remove 'sqlite:///' prefix, make absolute, then add it back
        db_path = db_uri.replace('sqlite:///', '')
        if not os.path.isabs(db_path):
            db_path = os.path.join(basedir, db_path)
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    else:
        SQLALCHEMY_DATABASE_URI = db_uri

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=int(os.environ.get('PERMANENT_SESSION_LIFETIME', 3600)))
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')

    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # No time limit for CSRF tokens

    # Rate Limiting Configuration
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"

    # Security Headers
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year for static files


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'

    # Enforce HTTPS in production
    SESSION_COOKIE_SECURE = True

    # Additional production security settings
    PREFERRED_URL_SCHEME = 'https'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing
    SESSION_COOKIE_SECURE = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': ProductionConfig  # Default to production for safety
}


def get_config():
    """Get configuration based on FLASK_ENV environment variable"""
    env = os.environ.get('FLASK_ENV', 'production')
    return config.get(env, config['default'])
