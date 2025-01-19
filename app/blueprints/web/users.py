from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, current_app, make_response
)
from flask_jwt_extended import jwt_required, unset_jwt_cookies
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import SessionLocal
from app.schemas.user_schema import UserUpdate
from app.services.user_service import UserService, \
    UserAlreadyExistsError
from app.utils.auth_utils import get_current_user_id

web_users_bp = Blueprint('web_users_bp', __name__,
                         template_folder='templates/users')


@web_users_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    try:
        user_id = get_current_user_id()
        with SessionLocal() as session:
            service = UserService(db=session)
            user = service.get_user_by_id(user_id)
            if not user:
                flash('User not found.', 'danger')
                return redirect(url_for('web_auth_bp.login'))
            return render_template('users/profile.html', user=user)
    except SQLAlchemyError as e:
        current_app.logger.error(f"Profile retrieval error: {e}")
        flash('An error occurred while fetching your profile.',
              'danger')
        return redirect(url_for('web_projects_bp.list_projects'))


@web_users_bp.route('/profile/update', methods=['POST'])
@jwt_required()
def update_profile():
    try:
        user_id = get_current_user_id()
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for('web_auth_bp.login'))

    form_data = request.form.to_dict()
    try:
        user_update = UserUpdate.model_validate(form_data)
    except Exception as e:
        flash(f"Validation error: {e}", 'danger')
        return redirect(url_for('web_users_bp.profile'))

    try:
        with SessionLocal() as session:
            service = UserService(db=session)
            updated_user = service.update_user(user_id=user_id,
                                               user_update=user_update)
            if updated_user:
                flash('Profile updated successfully!', 'success')
            else:
                flash('Failed to update profile.', 'danger')
    except UserAlreadyExistsError as e:
        flash(str(e), 'danger')
    except SQLAlchemyError as e:
        flash(f"Database error: {e}", 'danger')
    except Exception as e:
        flash(f"Profile update error: {e}", 'danger')

    return redirect(url_for('web_users_bp.profile'))


@web_users_bp.route('/profile/delete', methods=['POST'])
@jwt_required()
def delete_profile():
    try:
        user_id = get_current_user_id()
        with SessionLocal() as session:
            service = UserService(db=session)
            success = service.delete_user(user_id=user_id)
            if success:
                flash('Account deleted successfully.', 'success')
                response = make_response(
                    redirect(url_for('web_auth_bp.signup')))
                unset_jwt_cookies(response)
                return response
            else:
                flash('Failed to delete account.', 'danger')
    except SQLAlchemyError as e:
        flash(
            f"Database error occurred while deleting your account: {e}",
            'danger')
    except Exception as e:
        current_app.logger.error(f"Account deletion error: {e}")
        flash(
            'An unexpected error occurred while deleting your account.',
            'danger')

    return redirect(url_for('web_users_bp.profile'))
