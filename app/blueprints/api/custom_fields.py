from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from app.models.custom_field import CustomField
from app.models.user_model import User
from sqlalchemy.orm import Session

api_custom_fields_bp = Blueprint('api_custom_fields_bp', __name__)


@api_custom_fields_bp.route('/', methods=['GET'])
@jwt_required()
def list_custom_fields():
    current_user_id = get_jwt_identity()
    try:
        fields = CustomField.query.filter_by(
            user_id=current_user_id).all()
        results = [{"id": f.id, "table_name": f.table_name,
                    "field_name": f.field_name,
                    "field_type": f.field_type} for f in fields]
        return jsonify({"data": results}), 200
    except SQLAlchemyError as e:
        current_app.logger.error(
            f"Session error listing custom fields: {e}")
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500


@api_custom_fields_bp.route('/', methods=['POST'])
@jwt_required()
def create_custom_field():
    current_user_id = get_jwt_identity()
    try:
        data = request.get_json() or {}
        cf = CustomField(
            user_id=current_user_id,
            table_name=data.get('table_name'),
            field_name=data.get('field_name'),
            field_type=data.get('field_type')
        )
        Session.session.add(cf)
        Session.session.commit()
        return jsonify(
            {"message": "Custom field created", "id": cf.id}), 201
    except SQLAlchemyError as e:
        Session.session.rollback()
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        Session.session.rollback()
        return jsonify(
            {"error": "Invalid data", "details": str(e)}), 400


@api_custom_fields_bp.route('/<int:field_id>', methods=['PUT'])
@jwt_required()
def update_custom_field(field_id):
    current_user_id = get_jwt_identity()
    try:
        cf = CustomField.query.get(field_id)
        if not cf or cf.user_id != current_user_id:
            return jsonify({
                               "error": "Custom field not found or not owned by you"}), 404
        data = request.get_json() or {}
        for k, v in data.items():
            if hasattr(cf, k):
                setattr(cf, k, v)
        Session.session.commit()
        return jsonify({"message": "Custom field updated"}), 200
    except SQLAlchemyError as e:
        Session.session.rollback()
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        Session.session.rollback()
        return jsonify(
            {"error": "Invalid data", "details": str(e)}), 400


@api_custom_fields_bp.route('/<int:field_id>', methods=['DELETE'])
@jwt_required()
def delete_custom_field(field_id):
    current_user_id = get_jwt_identity()
    try:
        cf = CustomField.query.get(field_id)
        if not cf or cf.user_id != current_user_id:
            return jsonify({
                               "error": "Custom field not found or not owned by you"}), 404
        Session.session.delete(cf)
        Session.session.commit()
        return jsonify({"message": "Custom field deleted"}), 200
    except SQLAlchemyError as e:
        Session.session.rollback()
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500
