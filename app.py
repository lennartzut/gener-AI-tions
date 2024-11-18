import os
from flask import Flask
from dotenv import load_dotenv
from extensions import db, migrate
from routes import api
import logging

# Load environment variables
load_dotenv()

# Initialize Flask application
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Database configuration
database_url = os.getenv('DATABASE_URL')
if not database_url:
    raise ValueError("DATABASE_URL not found in .env file.")
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)

# Register blueprints
app.register_blueprint(api, url_prefix='/api')

# Test route
@app.route('/')
def home():
    return "Hello, Flask is running!"

# Run application
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
