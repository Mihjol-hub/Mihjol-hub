#config.py
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'MiguelRomero' #or os.urandom(24)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'JWTSecretMiguelRomero' #or os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'test.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=1)
    JWT_COOKIE_SECURE = False  # Set to True in production
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SAMESITE = 'Lax'
    JWT_COOKIE_CSRF_PROTECT = True
    WTF_CSRF_ENABLED = True  # Enable CSRF protection for forms
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_REFRESH_COOKIE_PATH = '/token/refresh'
    JWT_ERROR_MESSAGE_KEY = 'message'
    JWT_REFRESH_JSON_KEY = 'refresh'
    JWT_CSRF_CHECK_FORM = True
    LOG_LEVEL = 'INFO'

    
    # Addtional configurations for social network features
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB MAX upload size
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    JWT_COOKIE_CSRF_PROTECT = False  # Disable CSRF protection in development
    JWT_COOKIE_CSRF_PROTECTION = False  # Disable CSRF protection in development
    LOG_LEVEL = 'DEBUG'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')
    JWT_COOKIE_SECURE = False  # Disable CSRF protection in testing
    JWT_COOKIE_CSRF_PROTECT = False  # Disable CSRF protection in testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)

class ProductionConfig(Config):
    LOG_LEVEL = 'INFO'
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or os.urandom(32)
    JWT_COOKIE_SECURE = True  # Ensure cookies are only sent over HTTPS
    JWT_COOKIE_CSRF_PROTECT = True  # Enable CSRF protection in production

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
