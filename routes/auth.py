from flask import Blueprint, jsonify, request
from flask_pydantic import validate
from sqlalchemy.exc import IntegrityError
from extensions import db
from models.user import User
from schemas.auth_schema import UserCreate, UserLogin, UserOut
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)
from werkzeug.utils import secure_filename
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Configuration for avatar uploads
UPLOAD_FOLDER = 'static/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
auth_bp.config = {
    'UPLOAD_FOLDER': UPLOAD_FOLDER,
    'ALLOWED_EXTENSIONS': ALLOWED_EXTENSIONS
}

# Ensure upload folder exists
os.makedirs(auth_bp.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in auth_bp.config[
            'ALLOWED_EXTENSIONS']


# Signup Route
@auth_bp.route('/signup', methods=['POST'])
@validate()
def signup(body: UserCreate):
    # Check if avatar is provided
    avatar_path = None
    if 'avatar' in request.files:
        avatar_file = request.files['avatar']
        if avatar_file and allowed_file(avatar_file.filename):
            filename = secure_filename(avatar_file.filename)
            avatar_path = os.path.join(
                auth_bp.config['UPLOAD_FOLDER'], filename)
            avatar_file.save(avatar_path)
            avatar_path = f'/static/avatars/{filename}'
        else:
            return jsonify(
                {'error': 'Invalid avatar file type.'}), 400

    # Create new user
    new_user = User(
        email=body.email,
        avatar=avatar_path
    )
    new_user.set_password(body.password)

    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists.'}), 400

    # Log the user in after signup
    access_token = create_access_token(identity=new_user.id)
    refresh_token = create_refresh_token(identity=new_user.id)
    response = jsonify({'message': 'Signup successful'})
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response, 201


# Login Route
@auth_bp.route('/login', methods=['POST'])
@validate()
def login(body: UserLogin):
    user = User.query.filter_by(email=body.email).first()
    if not user or not user.check_password(body.password):
        return jsonify({'error': 'Invalid email or password.'}), 401

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    response = jsonify({'message': 'Login successful'})
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response, 200


# /me Route
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    user_out = UserOut.from_orm(user)
    return jsonify(user_out.model_dump()), 200


# Refresh Token Route
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    response = jsonify({'message': 'Token refreshed'})
    set_access_cookies(response, new_access_token)
    return response, 200


# Logout Route
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({'message': 'Successfully logged out'})
    unset_jwt_cookies(response)
    return response, 200
