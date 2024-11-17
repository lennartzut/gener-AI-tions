import os
from flask import Flask
from dotenv import load_dotenv
from extensions import db
import logging

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return "Hello, Flask is running!"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
