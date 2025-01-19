from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.event import Event
from app.models.project_model import Project
from app.extensions import SessionLocal
from datetime import datetime

web_events_bp = Blueprint('web_events_bp', __name__, template_folder='templates/events')

def get_valid_project(user_id: int, project_id: int):
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        flash('Project not found or not owned by you.', 'error')
        return None
    return project

@web_events_bp.route('/', methods=['GET', 'POST'])
@jwt_required()
def list_events():
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        flash('Project ID is required.', 'error')
        return redirect(url_for('web_projects_bp.list_projects'))

    project = get_valid_project(current_user_id, project_id)
    if not project:
        return redirect(url_for('web_projects_bp.list_projects'))

    if request.method == 'POST':
        # Create new event
        entity_type = request.form.get('entity_type')
        entity_id = request.form.get('entity_id', type=int)
        event_type = request.form.get('event_type')
        event_date_str = request.form.get('event_date')
        event_place = request.form.get('event_place')
        notes = request.form.get('notes')

        event_date = None
        if event_date_str:
            try:
                event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        new_event = Event(
            entity_type=entity_type,
            entity_id=entity_id,
            event_type=event_type,
            event_date=event_date,
            event_place=event_place,
            notes=notes
        )
        SessionLocal.session.add(new_event)
        SessionLocal.session.commit()
        flash('Event created successfully.', 'success')
        return redirect(url_for('web_events_bp.list_events', project_id=project_id))

    # GET: list all events (for simplicity, no filtering)
    events = Event.query.all()
    return render_template('events/events_list.html', events=events, project_id=project_id)

@web_events_bp.route('/<int:event_id>/update', methods=['POST'])
@jwt_required()
def update_event(event_id):
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        flash('Project ID is required.', 'error')
        return redirect(url_for('web_projects_bp.list_projects'))

    project = get_valid_project(current_user_id, project_id)
    if not project:
        return redirect(url_for('web_projects_bp.list_projects'))

    event = Event.query.get_or_404(event_id)
    event_type = request.form.get('event_type')
    event_place = request.form.get('event_place')
    notes = request.form.get('notes')
    event_date_str = request.form.get('event_date')

    if event_type:
        event.event_type = event_type
    if event_place:
        event.event_place = event_place
    if notes is not None:
        event.notes = notes

    if event_date_str:
        try:
            event.event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    SessionLocal.session.commit()
    flash('Event updated successfully.', 'success')
    return redirect(url_for('web_events_bp.list_events', project_id=project_id))

@web_events_bp.route('/<int:event_id>/delete', methods=['POST'])
@jwt_required()
def delete_event(event_id):
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        flash('Project ID is required.', 'error')
        return redirect(url_for('web_projects_bp.list_projects'))

    project = get_valid_project(current_user_id, project_id)
    if not project:
        return redirect(url_for('web_projects_bp.list_projects'))

    event = Event.query.get_or_404(event_id)
    SessionLocal.session.delete(event)
    SessionLocal.session.commit()
    flash('Event deleted successfully.', 'success')
    return redirect(url_for('web_events_bp.list_events', project_id=project_id))
