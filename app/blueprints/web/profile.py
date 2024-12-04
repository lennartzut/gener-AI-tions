from flask import Blueprint, render_template, redirect, url_for, \
    flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User

web_profile_bp = Blueprint(
    'web_profile_bp',
    __name__,
    template_folder='templates/profile'
)


@web_profile_bp.route('/', methods=['GET'])
@jwt_required()
def profile():
    """
    Displays the profile of the logged-in user.
    """
    user = User.query.get(get_jwt_identity())
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('web_auth_bp.login'))

    return render_template('profile.html', user=user)
