Gener-AI-tions

Gener-AI-tions is a genealogical (or family tree) management application built with Flask, SQLAlchemy, and pydantic. The goal is to provide a clean architecture for handling:
	•	User management (sign up, login, logout, update profile, delete account)
	•	Projects (organize genealogical or historical data by project)
	•	Individuals (people within a project, with birth/death info, notes, etc.)
	•	Identities (name/gender sets for an individual; can have multiple, with one primary)
	•	Relationships (connect individuals as parent/child, partners, etc.)

It supports JWT-based authentication and integrates with pytest for testing.

Table of Contents
	1.	Key Features
	2.	Project Architecture & Directory Structure
	3.	Models Overview
	4.	Requirements
	5.	Installation & Setup
	6.	Environment Variables
	7.	Database Initialization
	8.	Running the Application
	9.	Testing
	10.	Usage & Endpoints
	11.	Partial Updates
	12.	Deployment Notes
	13.	License
	14.	Contact / Contributing

Key Features
	1.	JWT Authentication: Provides routes for /api/auth/signup, /api/auth/login, etc.
	2.	Role-based Decorator: @admin_required to restrict certain endpoints to admin users.
	3.	Projects: Each user can create multiple projects, each project can contain multiple individuals and relationships.
	4.	Individuals: Stores birth/death info, has a one-to-many relationship with identities and a many-to-many-like relationship with other individuals (via relationships).
	5.	Identities: An individual can have multiple identities, each with optional valid_from / valid_until dates; one identity is flagged as primary.
	6.	Relationships: Using enumerations to define parent/child or partner. Can store union/dissolution dates, type of relationship, notes, etc.
	7.	Flexible: Built with pydantic for input validation (and partial update logic), plus robust error handling.

Project Architecture & Directory Structure

A high-level look at the repo (some folders omitted for brevity):

gener-AI-tions/
  ├── app/
  │   ├── blueprints/                (Flask endpoints; or "api_*.py" routes)
  │   ├── config.py                  (Configuration classes: Dev, Testing, Production)
  │   ├── context_processors.py      (Inject current user into Jinja templates, etc.)
  │   ├── create_tables.py           (Script to create DB tables)
  │   ├── error_handlers.py          (Global exception handling)
  │   ├── extensions.py              (Initialize DB engine, JWT, CORS)
  │   ├── models/
  │   │   ├── base_model.py          (Declarative base + imports)
  │   │   ├── enums_model.py         (Enum definitions: GenderEnum, etc.)
  │   │   ├── identity_model.py      (Identity SQLAlchemy model)
  │   │   ├── individual_model.py    (Individual SQLAlchemy model)
  │   │   ├── project_model.py       (Project SQLAlchemy model)
  │   │   ├── relationship_model.py  (Relationship SQLAlchemy model)
  │   │   ├── user_model.py          (User SQLAlchemy model)
  │   ├── schemas/                   (pydantic schemas for data validation)
  │   ├── services/                  (Business logic classes, e.g. IdentityService, IndividualService)
  │   ├── utils/                     (Utility modules: auth helpers, validators, custom exceptions)
  │   ├── __init__.py                (App initialization logic or create_app function)
  │   └── ...
  ├── tests/
  │   ├── conftest.py                (pytest fixtures)
  │   ├── test_*.py                  (Your test modules)
  ├── .env                           (Environment variables for local dev)
  ├── requirements.txt
  ├── run.py / wsgi.py (entry point) or similar
  ├── README.md                      (This file)
  └── ...

Models Overview

1. User
	•	Fields: username, email, password_hash, is_admin, etc.
	•	Relationship to Project (user.projects) and Individual (user.individuals).

2. Project
	•	Fields: name, user_id, project_number, timestamps.
	•	Relationship to Individual and Relationship.

3. Individual
	•	Fields: user_id, project_id, birth_date, death_date, etc.
	•	Relationship to Identities (one-to-many).
	•	Relationship to other Individuals through the Relationship table (via relationships_as_individual / relationships_as_related).
	•	One identity can be marked is_primary (exposed as primary_identity).

4. Identity
	•	Fields: individual_id, first_name, last_name, gender, valid_from, valid_until, is_primary, etc.
	•	Linked to Individual.
	•	For name changes, alternate aliases, etc.

5. Relationship
	•	Fields: individual_id, related_id, initial_relationship (child/parent/partner), relationship_detail (horizontal/vertical), optional union/dissolution dates, notes, etc.
	•	Ties two Individual records together in the same Project.

6. Enums (from app.models.enums_model):
	•	GenderEnum: e.g. male, female, non binary, etc.
	•	InitialRelationshipEnum: e.g. child, parent, partner.
	•	HorizontalRelationshipTypeEnum: e.g. biological, step, adoptive (for child/parent).
	•	VerticalRelationshipTypeEnum: e.g. marriage, civil union, partnership (for partner relationships).

Requirements

Below is a typical listing, also reflected in requirements.txt:

Flask==2.3.3
SQLAlchemy==2.0.21
psycopg2-binary==2.9.7
pydantic==2.2.1
Werkzeug==2.3.6
python-dotenv==1.0.0
Flask-JWT-Extended==4.5.3
Flask-Cors==3.0.10
bcrypt==4.0.1
Flask-Bcrypt==1.0.1

pytest==8.2.2
pytest-cov==4.1.0
pytest-anyio==4.3.0

(Adjust or pin the versions as you see fit.)

Installation & Setup
	1.	Clone the repository:

git clone https://github.com/your-org/gener-AI-tions.git
cd gener-AI-tions


	2.	(Optional) Create & activate a virtual environment:

python3 -m venv venv
source venv/bin/activate


	3.	Install dependencies:

pip install -r requirements.txt


	4.	Create a .env file (or set equivalent environment variables) see below.

Environment Variables

Inside your .env file (or your environment), you’ll need something like:

# .env

# Required: Database URLs for development, testing
DATABASE_URL=postgresql://username:password@localhost:5432/generations_db
TEST_DATABASE_URL=postgresql://username:password@localhost:5432/generations_test_db

# JWT secrets
JWT_SECRET_KEY=some-random-jwt-secret
SECRET_KEY=another-random-flask-secret

# Token expiration
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800

# Bcrypt 
BCRYPT_LOG_ROUNDS=12

# Additional optional config
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
JWT_COOKIE_SECURE=False
JWT_COOKIE_CSRF_PROTECT=False

Key fields:
	•	DATABASE_URL – main database for dev or production.
	•	TEST_DATABASE_URL – your test database (used by pytest).
	•	SECRET_KEY – a secret for Flask sessions or CSRF tokens.
	•	JWT_SECRET_KEY – a separate secret to sign JWTs.

Database Initialization

From the project root, run:

export FLASK_ENV=development
python run.py

This calls create_app("development") and runs create_tables(app). By default, it creates tables in whatever DB is pointed to by DATABASE_URL.

Alternatively, you can do:

python -m app.create_tables

(Adjust the exact command to your setup; you might have a run.py or a different entry script.)

Running the Application

To start the Flask dev server:

flask run

	•	By default, it serves on http://127.0.0.1:5000/.
	•	Check http://127.0.0.1:5000/health for a quick “healthy” status.

Or if you have a custom run.py:

python run.py

Testing

We use pytest. The tests/ folder has:
	•	conftest.py – sets up DB fixtures, app() fixture, etc.
	•	test_*.py – each file covers a different set of routes.

Steps to run tests:
	1.	In .env, ensure TEST_DATABASE_URL is set.
	2.	Execute:

PYTHONPATH=$(pwd) pytest

The environment is “testing,” and it uses the TestingConfig.

The test suite will:
	•	Create the schema in your test database.
	•	Insert some seed data (like a user, a project, an individual, etc.).
	•	Run your test routes.

If you see errors about “Object of type ValueError is not JSON serializable,” ensure you updated the @app.errorhandler(Exception) logic (as shown in the code above) or you catch ValueError in your routes so it returns a 400 properly.

Usage & Endpoints

All routes are prefixed with "/api" (see your blueprint registrations). A quick summary:
	•	Auth:
	•	POST /api/auth/signup
	•	POST /api/auth/login
	•	POST /api/auth/logout
	•	Users (logged in):
	•	GET /api/users/ – get current user profile
	•	PATCH /api/users/update – update current user info
	•	DELETE /api/users/delete – delete current user
	•	Projects:
	•	GET /api/projects/ – list user’s projects
	•	POST /api/projects/ – create a new project
	•	GET /api/projects/{project_id} – get details
	•	PUT /api/projects/{project_id} – update
	•	DELETE /api/projects/{project_id} – delete
	•	Individuals:
	•	GET /api/individuals/?project_id={id} – list individuals in a project
	•	POST /api/individuals/?project_id={id} – create new individual
	•	GET /api/individuals/{individual_id}?project_id={id} – get details
	•	PATCH /api/individuals/{individual_id}?project_id={id} – update
	•	DELETE /api/individuals/{individual_id}?project_id={id} – delete
	•	GET /api/individuals/search?project_id={id}&q=... – search
	•	Identities:
	•	GET /api/identities?project_id={id}
	•	POST /api/identities?project_id={id} – create identity for an individual
	•	GET /api/identities/{identity_id}?project_id={id}
	•	PATCH /api/identities/{identity_id}?project_id={id}
	•	DELETE /api/identities/{identity_id}?project_id={id}
	•	Relationships:
	•	GET /api/relationships?project_id={id} – list
	•	POST /api/relationships?project_id={id} – create
	•	GET /api/relationships/{relationship_id}?project_id={id} – get detail
	•	PATCH /api/relationships/{relationship_id}?project_id={id} – update
	•	DELETE /api/relationships/{relationship_id}?project_id={id} – delete

For a full spec, see your swagger.json or OpenAPI doc.

Partial Updates

All PATCH endpoints (for Individuals, Identities, Relationships, Users, etc.) allow partial updates via pydantic’s exclude_unset=True. Meaning:
	•	If you omit a field in the JSON, it remains unchanged in the database.
	•	If you send a field with null (and if your code allows nullable), it may set that field to null.
	•	If you send a value that triggers a pydantic or custom ValueError (like invalid date ranges), you’ll get a 400 Bad Request.

Deployment Notes

For production:
	1.	Set FLASK_ENV=production.
	2.	Ensure you have robust secrets (SECRET_KEY, JWT_SECRET_KEY).
	3.	Possibly use gunicorn or uWSGI behind an Nginx or Apache proxy.
	4.	Migrate or create the database before starting the app:

python run.py

or

python -m app.create_tables



Make sure you handle HTTPS termination (especially if JWT_COOKIE_SECURE=True).

License

(Add your preferred license here, e.g., MIT, Apache 2.0, proprietary, etc.)

Contact / Contributing

For contributions:
	1.	Fork the repo, make changes in a feature branch.
	2.	Submit a pull request explaining the changes.
	3.	Ensure all tests pass (pytest).

For questions or support, open an issue in the repository or contact the maintainer at info@example.com.

End of README