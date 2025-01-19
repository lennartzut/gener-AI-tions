from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, current_app
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import SessionLocal
from app.models.enums_model import GenderEnum
from app.schemas.individual_schema import IndividualCreate, \
    IndividualUpdate
from app.services.individual_service import IndividualService

web_individuals_bp = Blueprint('web_individuals_bp', __name__,
                               template_folder='templates/individuals')


@web_individuals_bp.route('/', methods=['GET'])
@jwt_required()
def get_individuals():
    """
    Show the project page with all individuals for the current user and project.
    If an individual_id is provided, fetch that individual's details.
    """
    current_user_id = get_jwt_identity()
    if not current_user_id:
        flash("Please log in.", 'danger')
        return redirect(url_for('web_auth_bp.login'))

    project_id = request.args.get('project_id', type=int)
    if not project_id:
        flash('Project ID is required.', 'danger')
        return redirect(url_for('web_projects_bp.list_projects'))

    individual_id = request.args.get('individual_id', type=int)
    try:
        with SessionLocal() as session:
            service = IndividualService(db=session)
            # Fetch all individuals for this project/user
            individuals = service.get_individuals_by_project(
                user_id=int(current_user_id),  # ensure int
                project_id=project_id,
                search_query=request.args.get('q', '').strip()
            )

            selected_individual = None
            if individual_id:
                selected_individual = service.get_individual_by_id(
                    individual_id=individual_id,
                    user_id=int(current_user_id),
                    project_id=project_id
                )

        return render_template(
            'projects/project_page.html',
            project_id=project_id,
            individuals=individuals,
            selected_individual=selected_individual,
            GenderEnum=GenderEnum
        )

    except SQLAlchemyError as e:
        # Log the full stack trace
        current_app.logger.exception(
            "SQLAlchemyError when fetching individuals:")
        # Option A: If you want to see the real error on the console, re-raise it:
        # raise e

        # Option B: If you prefer to keep it user-friendly, flash a message:
        flash('An error occurred while fetching individuals.',
              'danger')
        return redirect(url_for('web_projects_bp.list_projects'))


@web_individuals_bp.route('/', methods=['POST'])
@jwt_required()
def create_individual():
    current_user_id = get_jwt_identity()
    if not current_user_id:
        flash("Please log in.", 'danger')
        return redirect(url_for('web_auth_bp.login'))

    project_id = request.args.get('project_id', type=int)
    if not project_id:
        flash('Project ID is required.', 'danger')
        return redirect(url_for('web_projects_bp.list_projects'))

    form_data = request.form.to_dict()
    try:
        individual_create = IndividualCreate.model_validate(
            form_data)
    except Exception as e:
        flash(f"Validation error: {e}", 'danger')
        return render_template(
            'partials/forms/create_individual_form.html',
            form_data=form_data, project_id=project_id)

    try:
        with SessionLocal() as session:
            service = IndividualService(db=session)
            new_individual = service.create_individual(
                user_id=int(current_user_id),
                project_id=project_id,
                individual_create=individual_create
            )
            if new_individual:
                flash('Individual created successfully.', 'success')
            else:
                flash('Failed to create individual.', 'danger')
    except SQLAlchemyError as e:
        current_app.logger.exception(
            "SQLAlchemyError creating individual:")
        flash(f"Error creating individual in DB: {e}", 'danger')

    return redirect(url_for('web_individuals_bp.get_individuals',
                            project_id=project_id))


@web_individuals_bp.route('/<int:individual_id>/update',
                          methods=['POST'])
@jwt_required()
def update_individual(individual_id):
    current_user_id = get_jwt_identity()
    if not current_user_id:
        flash("Please log in.", 'danger')
        return redirect(url_for('web_auth_bp.login'))

    project_id = request.args.get('project_id', type=int)
    if not project_id:
        flash('Project ID is required.', 'danger')
        return redirect(url_for('web_projects_bp.list_projects'))

    form_data = request.form.to_dict()
    try:
        individual_update = IndividualUpdate.model_validate(
            form_data)
    except Exception as e:
        flash(f"Validation error: {e}", 'danger')
        return render_template(
            'partials/modals/update_individual_modal.html',
            form_data=form_data, project_id=project_id)

    try:
        with SessionLocal() as session:
            service = IndividualService(db=session)
            updated_individual = service.update_individual(
                individual_id=individual_id,
                user_id=int(current_user_id),
                project_id=project_id,
                individual_update=individual_update
            )
            if updated_individual:
                flash('Individual updated successfully.', 'success')
            else:
                flash('Failed to update individual.', 'danger')
    except SQLAlchemyError as e:
        current_app.logger.exception(
            "SQLAlchemyError updating individual:")
        flash(f"Error updating individual in DB: {e}", 'danger')

    return redirect(url_for('web_individuals_bp.get_individuals',
                            project_id=project_id))


@web_individuals_bp.route('/<int:individual_id>/delete',
                          methods=['POST'])
@jwt_required()
def delete_individual(individual_id):
    current_user_id = get_jwt_identity()
    if not current_user_id:
        flash("Please log in.", 'danger')
        return redirect(url_for('web_auth_bp.login'))

    project_id = request.args.get('project_id', type=int)
    if not project_id:
        flash('Project ID is required.', 'danger')
        return redirect(url_for('web_projects_bp.list_projects'))

    try:
        with SessionLocal() as session:
            service = IndividualService(db=session)
            success = service.delete_individual(
                individual_id=individual_id,
                user_id=int(current_user_id),
                project_id=project_id
            )
            if success:
                flash('Individual deleted successfully.', 'success')
            else:
                flash('Failed to delete individual.', 'danger')
    except SQLAlchemyError as e:
        current_app.logger.exception(
            "SQLAlchemyError deleting individual:")
        flash(f"Error deleting individual in DB: {e}", 'danger')

    return redirect(url_for('web_individuals_bp.get_individuals',
                            project_id=project_id))
