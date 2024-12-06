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

web_individuals_bp = Blueprint('web_individuals_bp', __name__,
                               template_folder='templates/individuals')


# Get Individuals
@web_individuals_bp.route('/', methods=['GET'])
@jwt_required()
def get_individuals():
    current_user_id = get_jwt_identity()
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
    return render_template('individuals_list.html',
                           individuals=individuals,
                           GenderEnum=GenderEnum)


# Create Individual with Default Identity
@web_individuals_bp.route('/create', methods=['GET', 'POST'])
@jwt_required()
def create_individual():
    current_user_id = get_jwt_identity()
    if request.method == 'POST':
        birth_date = request.form.get('birth_date') or None
        birth_place = request.form.get('birth_place') or None
        death_date = request.form.get('death_date') or None
        death_place = request.form.get('death_place') or None
        first_name = request.form.get('first_name') or None
        last_name = request.form.get('last_name') or None
        gender_str = request.form.get('gender') or None

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

            # Add a relationship if specified
            relationship = request.args.get(
                'relationship') or request.form.get('relationship')
            related_individual_id = request.args.get(
                'related_individual_id',
                type=int) or request.form.get(
                'related_individual_id', type=int)
            family_id = request.args.get('family_id',
                                         type=int) or request.form.get(
                'family_id', type=int)

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

        except ValueError:
            flash(f"Invalid gender value: {gender_str}", 'error')
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error creating individual: {e}")
            flash('An error occurred while creating the individual.',
                  'error')

    return render_template('create_individual_modal.html',
                           GenderEnum=GenderEnum)


# Update Individual
@web_individuals_bp.route('/<int:individual_id>/update',
                          methods=['GET', 'POST'])
@jwt_required()
def update_individual(individual_id):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=individual_id,
                                            user_id=current_user_id).first_or_404()

    if request.method == 'POST':
        birth_date = request.form.get('birth_date') or None
        birth_place = request.form.get('birth_place') or None
        death_date = request.form.get('death_date') or None
        death_place = request.form.get('death_place') or None
        first_name = request.form.get('first_name') or None
        last_name = request.form.get('last_name') or None
        gender_str = request.form.get('gender') or None

        try:
            # Update individual fields
            individual.birth_date = birth_date
            individual.birth_place = birth_place
            individual.death_date = death_date
            individual.death_place = death_place

            # Update selected identity
            primary_identity = individual.primary_identity
            if primary_identity:
                primary_identity.first_name = first_name
                primary_identity.last_name = last_name
                primary_identity.gender = GenderEnum(gender_str)

            db.session.commit()
            flash('Individual updated successfully.', 'success')
        except ValueError:
            db.session.rollback()
            flash(f"Invalid gender value: {gender_str}", 'error')
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
                           individual=individual)


# Delete Individual
@web_individuals_bp.route('/<int:individual_id>/delete',
                          methods=['POST'])
@jwt_required()
def delete_individual(individual_id: int):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=individual_id,
                                            user_id=current_user_id).first_or_404()

    db.session.delete(individual)
    db.session.commit()
    flash('Individual deleted successfully.', 'success')
    return redirect(url_for('web_individuals_bp.get_individuals'))
