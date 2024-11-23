import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


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
