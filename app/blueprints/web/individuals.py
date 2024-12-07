from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, current_app as app
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.individual import Individual
from app.models.identity import Identity
from app.models.enums import GenderEnum
from app.extensions import db
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from app.utils.family_utils import \
    add_relationship_for_new_individual
from datetime import datetime
from typing import Optional

web_individuals_bp = Blueprint('web_individuals_bp', __name__,
                               template_folder='templates/individuals')


def parse_date(date_str: Optional[str]) -> Optional[datetime.date]:
    """Utility function to safely parse a date string."""
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            app.logger.error(f"Invalid date format: {date_str}")
    return None


# Get Individuals
@web_individuals_bp.route('/', methods=['GET'])
@jwt_required()
def get_individuals():
    current_user_id = int(get_jwt_identity())
    search_query = request.args.get('q')
    limit = request.args.get('limit', 10, type=int)

    query = Individual.query.filter_by(
        user_id=current_user_id).options(
        joinedload(Individual.identities))

    if search_query:
        query = query.join(Identity).filter(
            (Individual.birth_place.ilike(f"%{search_query}%")) |
            (Identity.first_name.ilike(f"%{search_query}%")) |
            (Identity.last_name.ilike(f"%{search_query}%"))
        )

    individuals = query.order_by(Individual.updated_at.desc()).limit(
        limit).all()
    return render_template(
        'individuals_list.html',
        individuals=individuals,
        GenderEnum=GenderEnum
    )


# Create Individual with Default Identity
@web_individuals_bp.route('/create', methods=['GET', 'POST'])
@jwt_required()
def create_individual():
    current_user_id = int(get_jwt_identity())

    if request.method == 'POST':
        # Extract form data
        birth_date = parse_date(request.form.get('birth_date'))
        birth_place = request.form.get('birth_place') or None
        death_date = parse_date(request.form.get('death_date'))
        death_place = request.form.get('death_place') or None
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        gender_str = request.form.get('gender')

        # Validate required fields
        if not first_name or not last_name or not gender_str:
            flash("First name, last name, and gender are required.",
                  'error')
            return redirect(
                url_for('web_individuals_bp.create_individual'))

        try:
            gender = GenderEnum(gender_str)

            # Create the individual
            new_individual = Individual(
                user_id=current_user_id,
                birth_date=birth_date,
                birth_place=birth_place,
                death_date=death_date,
                death_place=death_place
            )
            db.session.add(new_individual)
            db.session.flush()

            # Create the default identity
            default_identity = Identity(
                individual_id=new_individual.id,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                valid_from=birth_date
            )
            db.session.add(default_identity)

            # Handle optional relationships
            relationship = request.form.get('relationship')
            related_individual_id = request.form.get(
                'related_individual_id', type=int)
            family_id = request.form.get('family_id', type=int)

            if relationship and (related_individual_id or family_id):
                add_relationship_for_new_individual(
                    relationship, related_individual_id,
                    new_individual, family_id, current_user_id
                )

            db.session.commit()
            flash(
                'Individual and default identity created successfully.',
                'success')
            return redirect(
                url_for('web_individuals_bp.get_individuals'))

        except ValueError as e:
            flash(f"Invalid input: {e}", 'error')
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error creating individual: {e}")
            flash('An error occurred while creating the individual.',
                  'error')

    return render_template('create_individual_modal.html',
                           GenderEnum=GenderEnum, current_user_id=int(get_jwt_identity()))


# Update Individual
@web_individuals_bp.route('/<int:individual_id>/update',
                          methods=['GET', 'POST'])
@jwt_required()
def update_individual(individual_id):
    current_user_id = int(get_jwt_identity())
    individual = Individual.query.filter_by(
        id=individual_id, user_id=current_user_id
    ).first_or_404()

    if request.method == 'POST':
        # Extract form data
        birth_date = parse_date(request.form.get('birth_date'))
        birth_place = request.form.get('birth_place') or None
        death_date = parse_date(request.form.get('death_date'))
        death_place = request.form.get('death_place') or None
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        gender_str = request.form.get('gender')

        try:
            # Update individual
            individual.birth_date = birth_date
            individual.birth_place = birth_place
            individual.death_date = death_date
            individual.death_place = death_place

            # Update primary identity
            primary_identity = individual.primary_identity
            if primary_identity:
                primary_identity.first_name = first_name
                primary_identity.last_name = last_name
                primary_identity.gender = GenderEnum(gender_str)

            db.session.commit()
            flash('Individual updated successfully.', 'success')
        except ValueError as e:
            db.session.rollback()
            flash(f"Invalid input: {e}", 'error')
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error updating individual: {e}")
            flash('An error occurred while updating the individual.',
                  'danger')

        return redirect(
            url_for('web_individuals_bp.get_individuals'))

    selected_gender = individual.primary_identity.gender if individual.primary_identity else None

    return render_template('create_individual_modal.html',
                           GenderEnum=GenderEnum,
                           selected_gender=selected_gender,
                           individual=individual,
                           current_user_id=int(get_jwt_identity()))


# Delete Individual
@web_individuals_bp.route('/<int:individual_id>/delete',
                          methods=['POST'])
@jwt_required()
def delete_individual(individual_id: int):
    current_user_id = int(get_jwt_identity())
    individual = Individual.query.filter_by(
        id=individual_id, user_id=current_user_id
    ).first_or_404()

    db.session.delete(individual)
    db.session.commit()
    flash('Individual deleted successfully.', 'success')
    return redirect(url_for('web_individuals_bp.get_individuals'))
