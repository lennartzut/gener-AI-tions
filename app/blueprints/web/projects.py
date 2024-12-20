from flask import Blueprint, render_template, request, redirect, \
    url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.project import Project

web_projects_bp = Blueprint('web_projects_bp', __name__)


@web_projects_bp.route('/', methods=['GET', 'POST'])
@jwt_required(optional=True)
def list_projects():
    current_user_id = get_jwt_identity()
    if not current_user_id:
        return render_template('main_landing.html')

    if request.method == 'POST':
        project_name = request.form.get('project_name')
        if project_name:
            new_project = Project(user_id=current_user_id,
                                  name=project_name)
            db.session.add(new_project)
            db.session.commit()
            flash('Project created successfully.', 'success')
        else:
            flash('Project name cannot be empty.', 'error')
        return redirect(url_for('web_projects_bp.list_projects'))

    projects = Project.query.filter_by(user_id=current_user_id,
                                       deleted_at=None).all()
    return render_template('projects/projects_list.html',
                           projects=projects)


@web_projects_bp.route('/select_project/<int:project_id>',
                       methods=['GET'])
@jwt_required()
def select_project(project_id):
    current_user_id = get_jwt_identity()
    project = Project.query.filter_by(id=project_id,
                                      user_id=current_user_id,
                                      deleted_at=None).first()
    if not project:
        flash('Project not found or not owned by you.', 'error')
        return redirect(url_for('web_projects_bp.list_projects'))
    # Redirect to unified project page (individuals on left, selected individual on right)
    return redirect(url_for('web_individuals_bp.get_individuals',
                            project_id=project_id))


@web_projects_bp.route('/update_project/<int:project_id>',
                       methods=['POST'])
@jwt_required()
def update_project(project_id):
    current_user_id = get_jwt_identity()
    project = Project.query.filter_by(id=project_id,
                                      user_id=current_user_id,
                                      deleted_at=None).first()
    if not project:
        flash('Project not found or not owned by you.', 'error')
        return redirect(url_for('web_projects_bp.list_projects'))

    project_name = request.form.get('project_name')
    if project_name:
        project.name = project_name
        db.session.commit()
        flash('Project updated successfully.', 'success')
    else:
        flash('Project name cannot be empty.', 'error')

    return redirect(url_for('web_projects_bp.list_projects'))


@web_projects_bp.route('/delete_project/<int:project_id>',
                       methods=['POST'])
@jwt_required()
def delete_project(project_id):
    current_user_id = get_jwt_identity()
    project = Project.query.filter_by(id=project_id,
                                      user_id=current_user_id,
                                      deleted_at=None).first()
    if not project:
        flash('Project not found or not owned by you.', 'error')
    else:
        project.soft_delete()
        db.session.commit()
        flash('Project deleted successfully.', 'success')
    return redirect(url_for('web_projects_bp.list_projects'))
