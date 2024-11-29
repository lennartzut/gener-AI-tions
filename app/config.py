import os
from dotenv import load_dotenv
from datetime import timedelta
import secrets

# Load environment variables from a .env file
load_dotenv()


class Config:
    """
    Base configuration with default settings.
    """
    SECRET_KEY = os.getenv('SECRET_KEY') or secrets.token_urlsafe(32)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') or secrets.token_urlsafe(32)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_COOKIE_SECURE = False  # Should be True in production
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_REFRESH_COOKIE_PATH = '/'
    JWT_COOKIE_CSRF_PROTECT = False


class DevelopmentConfig(Config):
    """
    Development-specific configurations.
    """
    DEBUG = True
    JWT_COOKIE_CSRF_PROTECT = False


class TestingConfig(Config):
    """
    Testing-specific configurations.
    """
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', 'sqlite:///:memory:')
    JWT_COOKIE_CSRF_PROTECT = False


class ProductionConfig(Config):
    """
    Production-specific configurations.
    """
    DEBUG = False
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT = False

