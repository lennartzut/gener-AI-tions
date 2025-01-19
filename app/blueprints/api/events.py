from flask import Blueprint, jsonify, request, current_app, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from app.models.event import Event
from app.models.project_model import Project
from app.schemas.event_schema import EventCreate, EventUpdate, \
    EventOut
from sqlalchemy.orm import Session

api_events_bp = Blueprint('api_events_bp', __name__)


def get_valid_project(user_id: int, project_id: int) -> Project:
    project = Project.query.filter_by(id=project_id,
                                      user_id=user_id).first()
    if not project:
        abort(404, "Project not found or not owned by this user.")
    return project


@api_events_bp.route('/', methods=['GET'])
@jwt_required()
def list_events():
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400
    get_valid_project(current_user_id, project_id)
    try:
        # Assuming no direct project_id on events (need a logic?),
        # If events link to individuals/families in that project.
        # For simplicity, list all events is tricky. Add a filter: entity_type & entity_id from request?
        events = Event.query.all()
        results = [EventOut.model_validate(e).dict() for e in events]
        return jsonify({"data": results}), 200
    except SQLAlchemyError as e:
        current_app.logger.error(f"Session error listing events: {e}")
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500


@api_events_bp.route('/', methods=['POST'])
@jwt_required()
def create_event():
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400
    get_valid_project(current_user_id, project_id)
    try:
        data = request.get_json() or {}
        event_data = EventCreate(**data)
        new_event = Event(**event_data.dict())
        Session.session.add(new_event)
        Session.session.commit()
        return jsonify({"message": "Event created successfully",
                        "data": EventOut.model_validate(
                            new_event).dict()}), 201
    except SQLAlchemyError as e:
        Session.session.rollback()
        current_app.logger.error(f"Session error creating event: {e}")
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        Session.session.rollback()
        current_app.logger.error(f"Error creating event: {e}")
        return jsonify(
            {"error": "Invalid data", "details": str(e)}), 400


@api_events_bp.route('/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400
    get_valid_project(current_user_id, project_id)
    try:
        event = Event.query.get(event_id)
        if not event:
            return jsonify({"error": "Event not found"}), 404
        data = request.get_json() or {}
        event_update = EventUpdate(**data)
        for k, v in event_update.dict(exclude_unset=True).items():
            setattr(event, k, v)
        Session.session.commit()
        return jsonify({"message": "Event updated successfully",
                        "data": EventOut.model_validate(
                            event).dict()}), 200
    except SQLAlchemyError as e:
        Session.session.rollback()
        current_app.logger.error(
            f"Session error updating event {event_id}: {e}")
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        Session.session.rollback()
        current_app.logger.error(f"Error updating event: {e}")
        return jsonify(
            {"error": "Invalid data", "details": str(e)}), 400


@api_events_bp.route('/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400
    get_valid_project(current_user_id, project_id)
    try:
        event = Event.query.get(event_id)
        if not event:
            return jsonify({"error": "Event not found"}), 404
        Session.session.delete(event)
        Session.session.commit()
        return jsonify(
            {"message": "Event deleted successfully"}), 200
    except SQLAlchemyError as e:
        Session.session.rollback()
        current_app.logger.error(
            f"Session error deleting event {event_id}: {e}")
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500
