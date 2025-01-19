from flask import (
    Blueprint, request, render_template, redirect, url_for, flash
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import SessionLocal
from app.models.enums_model import GenderEnum
from app.schemas.identity_schema import IdentityCreate, \
    IdentityUpdate
from app.services.identity_service import IdentityService

web_identities_bp = Blueprint('web_identities_bp', __name__,
                              template_folder='templates/identities')


@web_identities_bp.route('/<int:individual_id>/add-identity',
                         methods=['GET', 'POST'])
@jwt_required()
def add_identity(individual_id):
    current_user_id = get_jwt_identity()
    if not current_user_id:
        flash("Please log in.", 'danger')
        return redirect(url_for('web_auth_bp.login'))

    if request.method == 'POST':
        form_data = request.form.to_dict()
        try:
            identity_create = IdentityCreate.model_validate(
                form_data)
        except Exception as e:
            flash(f"Validation error: {e}", 'danger')
            return render_template(
                'partials/forms/add_identity_form.html',
                form_data=form_data, GenderEnum=GenderEnum)

        try:
            with SessionLocal() as session:
                service = IdentityService(db=session)
                new_identity = service.create_identity(
                    identity_create=identity_create,
                    is_primary=False  # or logic to decide
                )
                if new_identity:
                    flash('Identity added successfully.', 'success')
                else:
                    flash('Failed to create identity.', 'danger')
        except SQLAlchemyError as e:
            flash(f'Error adding identity: {e}', 'danger')

        return redirect(url_for('web_individuals_bp.get_individuals',
                                individual_id=individual_id))

    return render_template('partials/forms/add_identity_form.html',
                           GenderEnum=GenderEnum)


@web_identities_bp.route(
    '/<int:individual_id>/update-identity/<int:identity_id>',
    methods=['GET', 'POST'])
@jwt_required()
def update_identity(individual_id, identity_id):
    current_user_id = get_jwt_identity()
    if not current_user_id:
        flash("Please log in.", 'danger')
        return redirect(url_for('web_auth_bp.login'))

    if request.method == 'POST':
        form_data = request.form.to_dict()
        try:
            identity_update = IdentityUpdate.model_validate(
                form_data)
        except Exception as e:
            flash(f"Validation error: {e}", 'danger')
            return render_template(
                'partials/forms/update_identity_modal.html',
                form_data=form_data, GenderEnum=GenderEnum)

        try:
            with SessionLocal() as session:
                service = IdentityService(db=session)
                updated_identity = service.update_identity(
                    identity_id, identity_update)
                if updated_identity:
                    flash('Identity updated successfully.',
                          'success')
                else:
                    flash('Failed to update identity.', 'danger')
        except SQLAlchemyError as e:
            flash(f'Error updating identity: {e}', 'danger')

        return redirect(url_for('web_individuals_bp.get_individuals',
                                individual_id=individual_id))

    return render_template(
        'partials/forms/update_identity_modal.html',
        GenderEnum=GenderEnum)


@web_identities_bp.route(
    '/<int:individual_id>/delete-identity/<int:identity_id>',
    methods=['POST'])
@jwt_required()
def delete_identity(individual_id, identity_id):
    current_user_id = get_jwt_identity()
    if not current_user_id:
        flash("Please log in.", 'danger')
        return redirect(url_for('web_auth_bp.login'))

    try:
        with SessionLocal() as session:
            service = IdentityService(db=session)
            success = service.delete_identity(identity_id)
            if success:
                flash('Identity deleted successfully.', 'success')
            else:
                flash('Failed to delete identity.', 'danger')
    except SQLAlchemyError as e:
        flash(f'Error deleting identity: {e}', 'danger')

    return redirect(url_for('web_individuals_bp.get_individuals',
                            individual_id=individual_id))
