from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, current_app
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import SessionLocal
from app.schemas.project_schema import ProjectCreate, ProjectUpdate
from app.services.project_service import ProjectService

web_projects_bp = Blueprint('web_projects_bp', __name__,
                            template_folder='templates/projects')


@web_projects_bp.route('/', methods=['GET'])
@jwt_required()
def list_projects():
    current_user_id = get_jwt_identity()
    if not current_user_id:
        flash("Please log in.", "danger")
        return redirect(url_for('web_auth_bp.login'))

    try:
        with SessionLocal() as session:
            service = ProjectService(db=session)
            projects = service.get_projects_by_user(
                user_id=current_user_id)
        return render_template('projects/list_projects.html',
                               projects=projects)
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error fetching projects: {e}")
        flash('An error occurred while fetching your projects.',
              'danger')
        return redirect(url_for('web_main_bp.main_landing'))


@web_projects_bp.route('/create', methods=['POST'])
@jwt_required()
def create_project():
    current_user_id = get_jwt_identity()
    if not current_user_id:
        flash("Please log in.", "danger")
        return redirect(url_for('web_auth_bp.login'))

    form_data = request.form.to_dict()
    try:
        project_create = ProjectCreate.model_validate(form_data)
    except Exception as e:
        flash(f"Validation error: {e}", 'danger')
        return render_template(
            'partials/forms/create_project_form.html',
            form_data=form_data)

    try:
        with SessionLocal() as session:
            service = ProjectService(db=session)
            new_project = service.create_project(
                user_id=current_user_id,
                project_create=project_create)
            if new_project:
                flash('Project created successfully!', 'success')
            else:
                flash(
                    'Failed to create project. A project with this name may already exist.',
                    'danger')
    except SQLAlchemyError as e:
        flash(f"Error creating project: {e}", 'danger')

    return redirect(url_for('web_projects_bp.list_projects'))


@web_projects_bp.route('/<int:project_id>/update',
                       methods=['GET', 'POST'])
@jwt_required()
def update_project(project_id):
    current_user_id = get_jwt_identity()
    if not current_user_id:
        flash("Please log in.", "danger")
        return redirect(url_for('web_auth_bp.login'))

    if request.method == 'POST':
        form_data = request.form.to_dict()
        try:
            project_update = ProjectUpdate.model_validate(form_data)
        except Exception as e:
            flash(f"Validation error: {e}", 'danger')
            return render_template(
                'partials/forms/update_project_form.html',
                form_data=form_data, project_id=project_id)

        try:
            with SessionLocal() as session:
                service = ProjectService(db=session)
                updated_project = service.update_project(
                    project_id=project_id,
                    user_id=current_user_id,
                    project_update=project_update
                )
                if updated_project:
                    flash('Project updated successfully!', 'success')
                else:
                    flash('Failed to update project.', 'danger')
        except SQLAlchemyError as e:
            flash(f"Error updating project: {e}", 'danger')

        return redirect(url_for('web_projects_bp.list_projects'))

    # For GET, render the existing project details in a form
    try:
        with SessionLocal() as session:
            service = ProjectService(db=session)
            project = service.get_project_by_id(
                project_id=project_id)
        return render_template(
            'partials/forms/update_project_form.html',
            project=project)
    except SQLAlchemyError as e:
        flash(f"Error fetching project for update: {e}", 'danger')
        return redirect(url_for('web_projects_bp.list_projects'))


@web_projects_bp.route('/<int:project_id>/delete', methods=['POST'])
@jwt_required()
def delete_project(project_id):
    current_user_id = get_jwt_identity()
    if not current_user_id:
        flash("Please log in.", "danger")
        return redirect(url_for('web_auth_bp.login'))

    try:
        with SessionLocal() as session:
            service = ProjectService(db=session)
            success = service.delete_project(project_id=project_id,
                                             user_id=current_user_id)
            if success:
                flash('Project deleted successfully.', 'success')
            else:
                flash('Failed to delete project or no permission.',
                      'danger')
    except SQLAlchemyError as e:
        flash(f"Error deleting project: {e}", 'danger')

    return redirect(url_for('web_projects_bp.list_projects'))


@web_projects_bp.route('/<int:project_id>/select', methods=['GET'])
@jwt_required()
def select_project(project_id):
    current_user_id = get_jwt_identity()
    try:
        with SessionLocal() as session:
            service = ProjectService(db=session)
            project = service.get_project_by_id(
                project_id=project_id)
            if not project or project.user_id != int(
                    current_user_id):
                flash('Project not found or not owned by you.',
                      'danger')
                return redirect(
                    url_for('web_projects_bp.list_projects'))

            return redirect(
                url_for('web_individuals_bp.get_individuals',
                        project_id=project_id))
    except SQLAlchemyError as e:
        flash(f"Error selecting project: {e}", 'danger')
        return redirect(url_for('web_projects_bp.list_projects'))
