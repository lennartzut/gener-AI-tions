import pytest
from sqlalchemy import text

from app import create_app
from app.create_tables import create_tables
from app.extensions import SessionLocal
from app.models.base_model import Base


@pytest.fixture(scope='session')
def app():
    """
    Fixture to provide a Flask application configured for testing.

    Sets up the database tables before tests and tears them down
    after all tests are completed.

    Yields:
        Flask app instance.
    """
    test_app = create_app(env='testing')
    with test_app.app_context():
        create_tables(test_app)
        yield test_app

        engine = test_app.extensions.get("engine")
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope='function')
def client(app):
    """
    Fixture to provide a test client for making HTTP requests
    against the Flask app.

    Args:
        app (fixture): The Flask app instance.

    Returns:
        Test client instance.
    """
    return app.test_client()


@pytest.fixture(scope='function')
def db_session():
    """
    Fixture to provide a scoped SQLAlchemy session for direct DB
    interactions.

    Automatically closes after each test function.

    Yields:
        SQLAlchemy session.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope='function', autouse=True)
def setup_test_data(db_session):
    """
    Fixture to ensure a clean database state and create test data
    with all required fields populated.

    Sets up initial data including users, projects, individuals,
    identities, and relationships.

    Yields:
        None
    """
    from app.models.user_model import User
    from app.models.project_model import Project
    from app.models.individual_model import Individual
    from app.models.relationship_model import Relationship
    from app.models.identity_model import Identity

    db_session.rollback()
    Base.metadata.drop_all(bind=db_session.bind)
    Base.metadata.create_all(bind=db_session.bind)

    user = User(id=1, username="testuser",
                email="testuser@example.com")
    user.set_password("TestPass123!")
    db_session.add(user)
    db_session.flush()

    project = Project(id=1, name="Test Project", user_id=user.id,
                      project_number=1)
    db_session.add(project)

    individual_1 = Individual(
        id=1,
        project_id=project.id,
        user_id=user.id,
        birth_date="1990-01-01",
        individual_number=1
    )
    individual_2 = Individual(
        id=2,
        project_id=project.id,
        user_id=user.id,
        birth_date="1992-02-02",
        individual_number=2
    )
    individual_3 = Individual(
        id=3,
        project_id=project.id,
        user_id=user.id,
        birth_date="1995-03-03",
        individual_number=3
    )
    db_session.add(individual_1)
    db_session.add(individual_2)
    db_session.add(individual_3)
    db_session.flush()

    identity_1 = Identity(
        id=1,
        individual_id=1,
        first_name="Ind1First",
        last_name="Ind1Last",
        gender="male",
        valid_from="1990-01-01",
        is_primary=True,
        identity_number=1
    )
    identity_2 = Identity(
        id=2,
        individual_id=2,
        first_name="Ind2First",
        last_name="Ind2Last",
        gender="female",
        valid_from="1992-02-02",
        is_primary=True,
        identity_number=2
    )
    identity_3 = Identity(
        id=3,
        individual_id=3,
        first_name="Ind3First",
        last_name="Ind3Last",
        gender="unknown",
        valid_from="1995-03-03",
        is_primary=True,
        identity_number=3
    )
    db_session.add(identity_1)
    db_session.add(identity_2)
    db_session.add(identity_3)

    relationship = Relationship(
        id=1,
        project_id=project.id,
        individual_id=individual_1.id,
        related_id=individual_2.id,
        initial_relationship="parent"
    )
    db_session.add(relationship)
    db_session.commit()

    db_session.execute(text(
        "SELECT setval(pg_get_serial_sequence('users', 'id'), 2, TRUE)"
    ))
    db_session.execute(text(
        "SELECT setval(pg_get_serial_sequence('projects', 'id'), 1, TRUE)"
    ))
    db_session.execute(text(
        "SELECT setval(pg_get_serial_sequence('individuals', 'id'), 3, TRUE)"
    ))
    db_session.execute(text(
        "SELECT setval(pg_get_serial_sequence('relationships', 'id'), 1, TRUE)"
    ))
    db_session.execute(text(
        "SELECT setval(pg_get_serial_sequence('identities', 'id'), 3, TRUE)"
    ))

    db_session.commit()
    yield
    db_session.rollback()
