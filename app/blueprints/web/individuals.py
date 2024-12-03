from flask import Blueprint, render_template, request, redirect, \
    url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.individual import Individual
from app.models.identity import Identity
from app.models.relationship import Relationship
from app.extensions import db
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError

web_individuals_bp = Blueprint(
    'web_individuals_bp',
    __name__,
    template_folder='templates/individuals'
)


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
        # Join with Identity model for searching by name
        query = query.join(Identity).filter(
            (Individual.birth_place.ilike(f"%{search_query}%")) |
            (Identity.first_name.ilike(f"%{search_query}%")) |
            (Identity.last_name.ilike(f"%{search_query}%"))
        )

    individuals = query.order_by(Individual.updated_at.desc()).limit(
        limit).all()
    return render_template('individuals_list.html',
                           individuals=individuals)


# Get Individual by ID
@web_individuals_bp.route('/<int:individual_id>', methods=['GET'])
@jwt_required()
def get_individual(individual_id: int):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=individual_id,
                                            user_id=current_user_id).first_or_404()
    return render_template('individual_detail.html',
                           individual=individual)


# Create Individual with Default Identity
@web_individuals_bp.route('/create', methods=['GET', 'POST'])
@jwt_required()
def create_individual():
    current_user_id = get_jwt_identity()

    if request.method == 'POST':
        # Handle form submission
        birth_date = request.form.get('birth_date')
        birth_place = request.form.get('birth_place')
        death_date = request.form.get('death_date')
        death_place = request.form.get('death_place')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        gender = request.form.get('gender')

        if not first_name or not last_name or not gender:
            flash("First name, last name, and gender are required.",
                  'error')
            return redirect(
                url_for('web_individuals_bp.create_individual'))

        try:
            # Step 1: Create Individual
            new_individual = Individual(
                user_id=current_user_id,
                birth_date=birth_date,
                birth_place=birth_place,
                death_date=death_date,
                death_place=death_place,
            )
            db.session.add(new_individual)
            db.session.flush()  # Ensure `new_individual.id` is available

            # Step 2: Create Default Identity
            default_identity = Identity(
                individual_id=new_individual.id,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                valid_from=birth_date
                # Optional: Use birth_date as default start
            )
            db.session.add(default_identity)
            db.session.commit()

            flash(
                'Individual and default identity created successfully.',
                'success')
            return redirect(
                url_for('web_individuals_bp.get_individuals'))

        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while creating the individual.',
                  'error')
            return redirect(
                url_for('web_individuals_bp.create_individual'))

    return render_template('create_individual.html')


# Update Individual
@web_individuals_bp.route('/<int:individual_id>/edit',
                          methods=['GET', 'POST'])
@jwt_required()
def update_individual(individual_id: int):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=individual_id,
                                            user_id=current_user_id).first_or_404()

    if request.method == 'POST':
        # Handle form submission
        individual.birth_date = request.form.get('birth_date')
        individual.birth_place = request.form.get('birth_place')
        individual.death_date = request.form.get('death_date')
        individual.death_place = request.form.get('death_place')
        db.session.commit()

        flash('Individual updated successfully.', 'success')
        return redirect(url_for('web_individuals_bp.get_individual',
                                individual_id=individual_id))

    return render_template('edit_individual.html',
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


# Family Card
@web_individuals_bp.route('/<int:individual_id>/family-card',
                          methods=['GET'])
@jwt_required()
def get_family_card(individual_id):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=individual_id,
                                            user_id=current_user_id).first_or_404()
    parents = individual.get_parents()
    siblings = individual.get_siblings()
    partners = individual.get_partners()
    children = individual.get_children()
    return render_template(
        'family_card.html',
        individual=individual,
        parents=parents,
        siblings=siblings,
        partners=partners,
        children=children
    )


# Add Relationship
@web_individuals_bp.route('/<int:individual_id>/add-relationship',
                          methods=['POST'])
@jwt_required()
def add_relationship(individual_id: int):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=individual_id,
                                            user_id=current_user_id).first_or_404()

    relationship_type = request.form.get('type')
    target_id = request.form.get('target_id')

    if not relationship_type or not target_id:
        flash(
            'Relationship type and target individual are required.',
            'error')
        return redirect(url_for('web_individuals_bp.get_family_card',
                                individual_id=individual_id))

    target_individual = Individual.query.filter_by(id=target_id,
                                                   user_id=current_user_id).first()
    if not target_individual:
        flash('Target individual not found.', 'error')
        return redirect(url_for('web_individuals_bp.get_family_card',
                                individual_id=individual_id))

    try:
        if relationship_type == 'parent':
            relationship = Relationship(
                parent_id=target_individual.id,
                child_id=individual.id
            )
        elif relationship_type == 'child':
            relationship = Relationship(
                parent_id=individual.id,
                child_id=target_individual.id
            )
        else:
            flash('Invalid relationship type.', 'error')
            return redirect(
                url_for('web_individuals_bp.get_family_card',
                        individual_id=individual_id))

        db.session.add(relationship)
        db.session.commit()
        flash('Relationship added successfully.', 'success')
    except SQLAlchemyError:
        db.session.rollback()
        flash('An error occurred while adding the relationship.',
              'error')

    return redirect(url_for('web_individuals_bp.get_family_card',
                            individual_id=individual_id))
