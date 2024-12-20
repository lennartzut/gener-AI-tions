from flask import Blueprint, render_template, request, redirect, \
    url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.extensions import db

web_profile_bp = Blueprint('web_profile_bp', __name__)


@web_profile_bp.route('/', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('web_auth_bp.login'))
    return render_template('profile/profile.html', user=user)


@web_profile_bp.route('/', methods=['POST'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('web_auth_bp.login'))

    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    if username:
        user.username = username
    if email:
        user.email = email
    if password:
        user.set_password(password)

    try:
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    except Exception:
        db.session.rollback()
        flash('Error updating profile.', 'error')

    return redirect(url_for('web_profile_bp.profile'))


@web_profile_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('web_auth_bp.login'))

    try:
        db.session.delete(user)
        db.session.commit()
        flash('Account deleted successfully.', 'success')
    except Exception:
        db.session.rollback()
        flash('Error deleting account.', 'error')

    return redirect(url_for('web_auth_bp.signup'))
