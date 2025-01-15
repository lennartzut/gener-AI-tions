from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity

web_main_bp = Blueprint('web_main_bp', __name__)


@web_main_bp.route('/', methods=['GET'])
@jwt_required(optional=True)
def main_landing():
    """
    Main landing page. If user is logged in, redirect to projects,
    otherwise show a landing template.
    """
    current_user_id = get_jwt_identity()
    if current_user_id:
        return redirect(url_for('web_projects_bp.list_projects'))
    return render_template('main/main_landing.html')
