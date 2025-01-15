# alembic/env.py

import os
import sys
from logging.config import fileConfig
import logging  # <-- Add this import

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Add the project directory to sys.path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your Flask app and SQLAlchemy engine
from app import create_app
from app.extensions import engine, SessionLocal  # Ensure these imports work

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# Instead of context.get_logger(__name__), do:
logger = logging.getLogger("alembic.env")

# Create Flask app context
app = create_app(env=os.getenv('FLASK_ENV', 'production'))
app.app_context().push()

# Import all models to ensure Alembic can detect them
from app.models import *

# Add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata  # Replace 'Base' with your declarative base

def get_url():
    return app.config.get('SQLALCHEMY_DATABASE_URI')

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
