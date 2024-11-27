from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.individual import Individual
from models.identity import Identity
from models.relationship import Relationship
from extensions import db

individuals_web_bp = Blueprint('individuals_web', __name__,
                               template_folder='templates')


# Get Individuals
@individuals_web_bp.route('/', methods=['GET'])
@jwt_required()
def get_individuals():
    current_user_id = get_jwt_identity()
    search_query = request.args.get('q')
    limit = request.args.get('limit', 10, type=int)

    query = Individual.query.filter_by(user_id=current_user_id)
    if search_query:
        query = query.filter(
            Individual.birth_place.ilike(f"%{search_query}%")
        )

    individuals = query.order_by(Individual.updated_at.desc()).limit(limit).all()
    return render_template('individuals/individuals_list.html', individuals=individuals)


# Get Individual by ID
@individuals_web_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_individual(id: int):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=id, user_id=current_user_id).first_or_404()
    return render_template('individuals/individual_detail.html', individual=individual)


# Create Individual with Default Identity
@individuals_web_bp.route('/create', methods=['GET', 'POST'])
@jwt_required()
def create_individual():
    if request.method == 'POST':
        # Handle form submission
        current_user_id = get_jwt_identity()
        birth_date = request.form.get('birth_date')
        birth_place = request.form.get('birth_place')
        death_date = request.form.get('death_date')
        death_place = request.form.get('death_place')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        gender = request.form.get('gender')

        if not first_name or not last_name or not gender:
            flash("First name, last name, and gender are required.", 'error')
            return redirect(url_for('web.individuals_web.create_individual'))

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
            valid_from=birth_date  # Optional: Use birth_date as default start
        )
        db.session.add(default_identity)
        db.session.commit()

        flash('Individual and default identity created successfully.', 'success')
        return redirect(url_for('web.individuals_web.get_individuals'))

    return render_template('individuals/create_individual.html')


# Update Individual
@individuals_web_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@jwt_required()
def update_individual(id: int):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=id, user_id=current_user_id).first_or_404()

    if request.method == 'POST':
        # Handle form submission
        individual.birth_date = request.form.get('birth_date')
        individual.birth_place = request.form.get('birth_place')
        individual.death_date = request.form.get('death_date')
        individual.death_place = request.form.get('death_place')
        db.session.commit()

        flash('Individual updated successfully.', 'success')
        return redirect(url_for('web.individuals_web.get_individual', id=id))

    return render_template('individuals/edit_individual.html', individual=individual)


# Delete Individual
@individuals_web_bp.route('/<int:id>/delete', methods=['POST'])
@jwt_required()
def delete_individual(id: int):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=id, user_id=current_user_id).first_or_404()

    db.session.delete(individual)
    db.session.commit()
    flash('Individual deleted successfully.', 'success')
    return redirect(url_for('web.individuals_web.get_individuals'))


# Family Card
@individuals_web_bp.route('/<int:id>/family-card', methods=['GET'])
@jwt_required()
def get_family_card(id):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=id, user_id=current_user_id).first_or_404()
    parents = individual.get_parents()
    siblings = individual.get_siblings()
    partners = individual.get_partners()
    children = individual.get_children()
    return render_template('individuals/family_card.html',
                           individual=individual,
                           parents=parents,
                           siblings=siblings,
                           partners=partners,
                           children=children)


# Add Relationship
@individuals_web_bp.route('/<int:id>/add-relationship', methods=['POST'])
@jwt_required()
def add_relationship(id: int):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=id, user_id=current_user_id).first_or_404()

    relationship_type = request.form.get('type')
    target_id = request.form.get('target_id')

    if not relationship_type or not target_id:
        flash('Relationship type and target individual are required.', 'error')
        return redirect(url_for('web.individuals_web.get_family_card', id=id))

    target_individual = Individual.query.filter_by(id=target_id, user_id=current_user_id).first()
    if not target_individual:
        flash('Target individual not found.', 'error')
        return redirect(url_for('web.individuals_web.get_family_card', id=id))

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
        return redirect(url_for('web.individuals_web.get_family_card', id=id))

    db.session.add(relationship)
    db.session.commit()
    flash('Relationship added successfully.', 'success')
    return redirect(url_for('web.individuals_web.get_family_card', id=id))
