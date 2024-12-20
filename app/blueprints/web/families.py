from flask import Blueprint, flash, redirect, url_for, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.family import Family
from sqlalchemy.exc import SQLAlchemyError

web_families_bp = Blueprint('web_families_bp', __name__)


@web_families_bp.route('/<int:family_id>/update', methods=['POST'])
@jwt_required()
def update_family(family_id):
    current_user_id = get_jwt_identity()
    # If needed, handle updates the same way as before or remove entirely if using APIs.
    family = Family.query.get(family_id)
    if not family:
        flash('Family not found.', 'error')
        return redirect(request.referrer or url_for(
            'web_projects_bp.list_projects'))

    family.relationship_type = request.form.get('relationship_type',
                                                family.relationship_type)
    family.union_date = request.form.get('union_date') or None
    family.union_place = request.form.get('union_place') or None
    family.dissolution_date = request.form.get(
        'dissolution_date') or None

    try:
        db.session.commit()
        flash('Family information updated successfully.', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('An error occurred while updating the family.',
              'danger')
    return redirect(
        request.referrer or url_for('web_projects_bp.list_projects'))
