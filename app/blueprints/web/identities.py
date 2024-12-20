from flask import Blueprint, request, redirect, url_for, flash, \
    render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.identity import Identity
from app.models.individual import Individual
from app.models.enums import GenderEnum
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError

web_identities_bp = Blueprint('web_identities_bp', __name__)


@web_identities_bp.route('/<int:individual_id>/add-identity',
                         methods=['GET', 'POST'])
@jwt_required()
def add_identity(individual_id):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=individual_id,
                                            user_id=current_user_id).first_or_404()

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        gender = request.form.get('gender')
        valid_from = request.form.get('valid_from')
        valid_until = request.form.get('valid_until')

        if not first_name or not last_name or not gender:
            flash("First name, last name, and gender are required.",
                  'danger')
            return redirect(url_for('web_identities_bp.add_identity',
                                    individual_id=individual_id))

        try:
            new_identity = Identity(
                individual_id=individual.id,
                first_name=first_name,
                last_name=last_name,
                gender=GenderEnum(gender),
                valid_from=valid_from or None,
                valid_until=valid_until or None
            )
            db.session.add(new_identity)
            db.session.commit()
            flash('Identity added successfully.', 'success')
        except ValueError:
            db.session.rollback()
            flash("Invalid gender value.", 'danger')
        except SQLAlchemyError:
            db.session.rollback()
            flash('Error adding identity.', 'danger')

        return redirect(url_for('web_individuals_bp.get_individuals',
                                project_id=individual.project_id,
                                individual_id=individual_id))

    return render_template('partials/forms/add_identity_form.html',
                           GenderEnum=GenderEnum)


@web_identities_bp.route(
    '/<int:individual_id>/update-identity/<int:identity_id>',
    methods=['GET', 'POST'])
@jwt_required()
def update_identity(individual_id, identity_id):
    current_user_id = get_jwt_identity()
    identity = Identity.query.filter_by(id=identity_id).join(
        Individual).filter(Individual.id == individual_id,
                           Individual.user_id == current_user_id).first_or_404()

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        gender = request.form.get('gender')
        valid_from = request.form.get('valid_from')
        valid_until = request.form.get('valid_until')

        try:
            identity.first_name = first_name
            identity.last_name = last_name
            identity.gender = GenderEnum(gender)
            identity.valid_from = valid_from or None
            identity.valid_until = valid_until or None

            db.session.commit()
            flash('Identity updated successfully.', 'success')
        except ValueError:
            db.session.rollback()
            flash("Invalid gender value.", 'danger')
        except SQLAlchemyError:
            db.session.rollback()
            flash('Error updating identity.', 'danger')

        return redirect(url_for('web_individuals_bp.get_individuals',
                                project_id=identity.individual.project_id,
                                individual_id=individual_id))

    return render_template(
        'partials/forms/update_identity_modal.html',
                           identity=identity,
                           GenderEnum=GenderEnum)


@web_identities_bp.route(
    '/<int:individual_id>/delete-identity/<int:identity_id>',
    methods=['POST'])
@jwt_required()
def delete_identity(individual_id, identity_id):
    current_user_id = get_jwt_identity()
    identity = Identity.query.filter_by(id=identity_id).join(
        Individual).filter(Individual.id == individual_id,
                           Individual.user_id == current_user_id).first_or_404()

    try:
        db.session.delete(identity)
        db.session.commit()
        flash('Identity deleted successfully.', 'success')
    except SQLAlchemyError:
        db.session.rollback()
        flash('Error deleting identity.', 'danger')

    return redirect(url_for('web_individuals_bp.get_individuals',
                            project_id=identity.individual.project_id,
                            individual_id=individual_id))
