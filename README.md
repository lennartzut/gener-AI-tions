# Gener-AI-tions API

Gener-AI-tions is a robust Flask-based API designed to manage individuals, their identities, and relationships within various projects. It offers comprehensive user authentication, project management, and administrative functionalities, making it ideal for applications requiring detailed record-keeping and relationship mapping.

---

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Database Setup](#database-setup)
  - [Running the Application](#running-the-application)
  - [Database Migrations](#database-migrations)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Features

### User Authentication & Authorization
- Secure user registration and login using JWT.
- Role-based access control with admin privileges.

### Project Management
- Create, retrieve, update, and delete projects.
- Assign projects to specific users.

### Individual & Identity Management
- Manage individuals with detailed profiles.
- Handle multiple identities per individual, including primary identities.

### Relationship Mapping
- Define and manage relationships (e.g., parent, child, partner, sibling) between individuals.
- Ensure data integrity and prevent duplicate or invalid relationships.

### Administrative Controls
- Admins can manage all users and view comprehensive data.

### Comprehensive API Documentation
- Interactive Swagger UI for easy API exploration and testing.

---

## Technologies Used
- **Backend Framework**: Flask
- **Database**: SQLAlchemy ORM with Alembic for migrations
- **Authentication**: JWT (JSON Web Tokens)
- **Data Validation**: Pydantic
- **API Documentation**: Swagger UI
- **Testing**: Pytest
- **Others**: Logging, Flask Blueprints, Flask-JWT-Extended

---

## Getting Started

Follow these instructions to set up and run the Gener-AI-tions API on your local machine.

### Prerequisites
- Python 3.8+
- PostgreSQL (or another supported SQL database)
- Virtual Environment Tool (e.g., `venv`, `virtualenv`)

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/gener-ai-tions.git
   cd gener-ai-tions
   ```

2. **Create and Activate a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. **Environment Variables**
   Create a `.env` file in the root directory and configure the following variables:
   ```env
   FLASK_APP=run.py
   FLASK_ENV=development
   DATABASE_URL=postgresql://username:password@localhost:5432/gener_ai_tions_db
   JWT_SECRET_KEY=your_jwt_secret_key
   ```
   - `FLASK_APP`: Entry point of the Flask application.
   - `FLASK_ENV`: Set to `development` for development purposes.
   - `DATABASE_URL`: Your database connection string.
   - `JWT_SECRET_KEY`: A secure secret key for JWT encoding and decoding.

2. **Load Environment Variables**
   Ensure that environment variables are loaded when running the application. You can use packages like `python-dotenv` or configure your environment accordingly.

---

## Database Setup

Gener-AI-tions uses **Alembic** for managing database migrations, ensuring that your database schema stays in sync with your SQLAlchemy models.

1. **Initialize the Database**
   Ensure that PostgreSQL is running and the database specified in `DATABASE_URL` exists. If not, create it:
   ```bash
   createdb gener_ai_tions_db
   ```

2. **Apply Database Migrations**
   Use Alembic to set up the database schema based on your models:
   ```bash
   alembic upgrade head
   ```

---

## Running the Application

Start the Flask development server:
```bash
flask run
```
The API will be accessible at `http://localhost:5000/`.


---

## Database Migrations

Alembic handles the versioning and migration of your database schema. Below are the common commands you'll use during development:

1. **Creating a New Migration**
   Whenever you make changes to your SQLAlchemy models, generate a new migration script:
   ```bash
   alembic revision --autogenerate -m "Describe your change here"
   ```

2. **Applying Migrations**
   Apply all pending migrations to update the database schema:
   ```bash
   alembic upgrade head
   ```

3. **Downgrading Migrations**
   If you need to revert the last migration:
   ```bash
   alembic downgrade -1
   ```

4. **Viewing Migration History**
   To view the current migration state:
   ```bash
   alembic current
   ```

5. **Storing the Current State Without Applying Migrations**
   If you need to mark the current state as up-to-date without running migrations (useful for aligning Alembic with an existing database):
   ```bash
   alembic stamp head
   ```

---

## API Documentation

Gener-AI-tions provides comprehensive API documentation through Swagger UI.

### Access Swagger UI
Navigate to `http://localhost:5000/api/docs` to explore and interact with the API endpoints.

---

## Testing

Gener-AI-tions includes a suite of tests to ensure the reliability and integrity of the application.

1. **Run Tests with Pytest**
   ```bash
   pytest
   ```

2. **Test Coverage**
   To check test coverage, use the `pytest-cov` plugin:
   ```bash
   pytest --cov=app
   ```

---

## Project Structure

```plaintext
gener-ai-tions/
├── app/
│   ├── blueprints/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── extensions.py
│   ├── error_handlers.py
│   └── utils/
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── tests/
├── .env
├── requirements.txt
├── Procfile
├── start.sh
├── alembic.ini
├── run.py
└── README.md
```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**  
2. **Clone Your Fork**
   ```bash
   git clone https://github.com/yourusername/gener-ai-tions.git
   cd gener-ai-tions
   ```
3. **Create a New Branch**
   ```bash
   git checkout -b feature/YourFeatureName
   ```
4. **Make Your Changes**  
5. **Commit Your Changes**
   ```bash
   git commit -m "Add feature: YourFeatureName"
   ```
6. **Push to Your Fork**
   ```bash
   git push origin feature/YourFeatureName
   ```
7. **Create a Pull Request**

---

## License

This project is licensed under the MIT License.
