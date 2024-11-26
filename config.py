import os
from dotenv import load_dotenv
from datetime import timedelta
import secrets

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') or secrets.token_urlsafe(32)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_COOKIE_SECURE = False
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_REFRESH_COOKIE_PATH = '/auth/refresh'
    JWT_COOKIE_CSRF_PROTECT = False
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/avatars')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    SCHEDULER_API_ENABLED = True


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL',
                                             'sqlite:///:memory:')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT = True
