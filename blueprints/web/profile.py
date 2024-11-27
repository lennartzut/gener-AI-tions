from flask import Blueprint, render_template, redirect, \
    url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User

profile_web_bp = Blueprint('profile_web', __name__,
                           template_folder='templates')


@profile_web_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('auth.login'))

    return render_template('profile/profile.html', user=user)
