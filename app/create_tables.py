from app import create_app
from app.models import *

def create_tables(app):
    """
    Creates all tables in the database based on the models.
    """
    engine = app.extensions.get("engine")
    if engine is None:
        raise ValueError("Database engine is not initialized.")

    print(f"Creating tables using engine: {engine}")
    Base.metadata.create_all(engine)
    print("All tables created successfully.")


if __name__ == "__main__":
    app = create_app("development")  # or 'production', 'testing'
    with app.app_context():
        create_tables(app)
