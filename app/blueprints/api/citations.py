from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
from app.models.citation import Citation
from app.models.source import Source
from sqlalchemy.orm import Session

api_citations_bp = Blueprint('api_citations_bp', __name__)


@api_citations_bp.route('/', methods=['GET'])
@jwt_required()
def list_citations():
    try:
        citations = Citation.query.all()
        results = [{"id": c.id, "source_id": c.source_id,
                    "entity_type": c.entity_type,
                    "entity_id": c.entity_id, "notes": c.notes} for c
                   in citations]
        return jsonify({"data": results}), 200
    except SQLAlchemyError as e:
        current_app.logger.error(f"Session error listing citations: {e}")
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500


@api_citations_bp.route('/', methods=['POST'])
@jwt_required()
def create_citation():
    try:
        data = request.get_json() or {}
        source_id = data.get('source_id')
        source = Source.query.get(source_id)
        if not source:
            return jsonify({"error": "Source not found"}), 404
        new_citation = Citation(
            source_id=source_id,
            entity_type=data.get('entity_type'),
            entity_id=data.get('entity_id'),
            notes=data.get('notes')
        )
        Session.session.add(new_citation)
        Session.session.commit()
        return jsonify({"message": "Citation created successfully",
                        "id": new_citation.id}), 201
    except SQLAlchemyError as e:
        Session.session.rollback()
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        Session.session.rollback()
        return jsonify(
            {"error": "Invalid data", "details": str(e)}), 400


@api_citations_bp.route('/<int:citation_id>', methods=['PUT'])
@jwt_required()
def update_citation(citation_id):
    try:
        citation = Citation.query.get(citation_id)
        if not citation:
            return jsonify({"error": "Citation not found"}), 404
        data = request.get_json() or {}
        for k, v in data.items():
            if hasattr(citation, k):
                setattr(citation, k, v)
        Session.session.commit()
        return jsonify(
            {"message": "Citation updated successfully"}), 200
    except SQLAlchemyError as e:
        Session.session.rollback()
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        Session.session.rollback()
        return jsonify(
            {"error": "Invalid data", "details": str(e)}), 400


@api_citations_bp.route('/<int:citation_id>', methods=['DELETE'])
@jwt_required()
def delete_citation(citation_id):
    try:
        citation = Citation.query.get(citation_id)
        if not citation:
            return jsonify({"error": "Citation not found"}), 404
        Session.session.delete(citation)
        Session.session.commit()
        return jsonify(
            {"message": "Citation deleted successfully"}), 200
    except SQLAlchemyError as e:
        Session.session.rollback()
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500
