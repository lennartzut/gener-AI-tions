from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, current_app as app
)
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.individual import Individual
from app.models.identity import Identity
from app.models.relationship import Relationship
from app.models.family import Family
from app.models.enums import GenderEnum, RelationshipType, \
    RelationshipTypeEnum
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


# Create Individual with Default Identity and Optional Relationship
@web_individuals_bp.route('/create', methods=['GET', 'POST'])
@jwt_required()
def create_individual():
    current_user_id = get_jwt_identity()

    # Get optional parameters
    relationship = request.args.get(
        'relationship') or request.form.get('relationship')
    related_individual_id = request.args.get('related_individual_id',
                                             type=int) or request.form.get(
        'related_individual_id', type=int)
    family_id = request.args.get('family_id',
                                 type=int) or request.form.get(
        'family_id', type=int)

    if request.method == 'POST':
        # Handle form submission
        birth_date = request.form.get('birth_date')
        birth_place = request.form.get('birth_place')
        death_date = request.form.get('death_date')
        death_place = request.form.get('death_place')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        gender_str = request.form.get('gender')

        if not first_name or not last_name or not gender_str:
            flash("First name, last name, and gender are required.",
                  'error')
            return redirect(
                url_for('web_individuals_bp.create_individual',
                        relationship=relationship,
                        related_individual_id=related_individual_id,
                        family_id=family_id))

        try:
            # Convert gender_str to GenderEnum
            gender = GenderEnum(gender_str)

            # Step 1: Create Individual
            new_individual = Individual(
                user_id=current_user_id,
                birth_date=birth_date,
                birth_place=birth_place,
                death_date=death_date,
                death_place=death_place,
            )
            db.session.add(new_individual)
            db.session.flush()  # Ensure new_individual.id is available

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

            # Step 3: Establish relationship if specified
            if relationship and (related_individual_id or family_id):
                add_relationship_for_new_individual(
                    relationship, related_individual_id,
                    new_individual, family_id, current_user_id
                )

            db.session.commit()

            flash(
                'Individual and default identity created successfully.',
                'success')
            return redirect_to_family_or_individual(
                related_individual_id, family_id)

        except ValueError as ve:
            flash(f"Invalid gender value: {gender_str}", 'error')
            return redirect(
                url_for('web_individuals_bp.create_individual',
                        relationship=relationship,
                        related_individual_id=related_individual_id,
                        family_id=family_id))
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error creating individual: {e}")
            flash('An error occurred while creating the individual.',
                  'error')
            return redirect(
                url_for('web_individuals_bp.create_individual',
                        relationship=relationship,
                        related_individual_id=related_individual_id,
                        family_id=family_id))

    return render_template('create_individual.html',
                           GenderEnum=GenderEnum)


# Add Child to Family
@web_individuals_bp.route('/add-child', methods=['POST'])
@jwt_required()
def add_child():
    current_user_id = get_jwt_identity()
    family_id = request.form.get('family_id', type=int)
    child_id = request.form.get('child_id', type=int)

    if not family_id or not child_id:
        flash('Family ID and Child ID are required.', 'danger')
        return redirect(request.referrer or url_for(
            'web_individuals_bp.get_individuals'))

    try:
        family = Family.query.get_or_404(family_id)
        child = Individual.query.filter_by(id=child_id,
                                           user_id=current_user_id).first_or_404()

        if child not in family.children:
            family.children.append(child)
            # Create parent-child relationships
            if family.partner1_id:
                relationship_obj = Relationship(
                    parent_id=family.partner1_id,
                    child_id=child.id,
                    relationship_type=RelationshipType.PARENT
                )
                db.session.add(relationship_obj)
            if family.partner2_id:
                relationship_obj = Relationship(
                    parent_id=family.partner2_id,
                    child_id=child.id,
                    relationship_type=RelationshipType.PARENT
                )
                db.session.add(relationship_obj)

            db.session.commit()
            flash('Child added to family successfully.', 'success')
        else:
            flash('Child is already part of the family.', 'info')

        # Redirect to the family card of one of the parents
        return redirect(url_for('web_individuals_bp.get_family_card',
                                individual_id=family.partner1_id or family.partner2_id))

    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f"Error adding child to family: {e}")
        flash(
            'An error occurred while adding the child to the family.',
            'danger')
        return redirect(request.referrer or url_for(
            'web_individuals_bp.get_individuals'))


# Update Individual
@web_individuals_bp.route('/<int:individual_id>/update',
                          methods=['POST'])
@jwt_required()
def update_individual(individual_id):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=individual_id,
                                            user_id=current_user_id).first_or_404()

    # Update individual fields
    individual.birth_date = request.form.get('birth_date') or None
    individual.birth_place = request.form.get('birth_place') or None
    individual.death_date = request.form.get('death_date') or None
    individual.death_place = request.form.get('death_place') or None

    # Update selected identity
    identity_id = request.args.get('identity_id', type=int)
    identity = Identity.query.filter_by(id=identity_id,
                                        individual_id=individual_id).first()
    if identity:
        identity.first_name = request.form.get('first_name') or None
        identity.last_name = request.form.get('last_name') or None
        # Update other identity fields as needed

    try:
        db.session.commit()
        flash('Individual updated successfully.', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f"Error updating individual: {e}")
        flash('An error occurred while updating the individual.',
              'danger')

    return redirect(url_for('web_individuals_bp.get_family_card',
                            individual_id=individual_id))


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
    individual = Individual.query.filter_by(
        id=individual_id, user_id=current_user_id
    ).options(
        joinedload(Individual.identities)
    ).first_or_404()

    # Retrieve identities and selected identity
    identities = individual.identities
    selected_identity_id = request.args.get('identity_id',
                                            type=int) or (
                               individual.primary_identity.id if individual.primary_identity else None)
    selected_identity = next(
        (i for i in identities if i.id == selected_identity_id),
        None)

    # Retrieve parents and their family IDs
    parents = individual.get_parents()
    parent_family_ids = {}
    for parent in parents:
        family = get_family_by_parent_and_child(parent.id,
                                                individual.id)
        parent_family_ids[
            parent.id] = family.id if family else 'Unknown'

    # Retrieve siblings
    siblings = individual.get_siblings()

    # Retrieve partners and selected partner
    partners = individual.get_partners()
    selected_partner_id = request.args.get('partner_id', type=int)
    selected_partner = next(
        (p for p in partners if p.id == selected_partner_id),
        partners[0] if partners else None)

    partner_family_ids = {}
    for partner in partners:
        family = get_family_by_parents(individual.id, partner.id)
        partner_family_ids[
            partner.id] = family.id if family else 'Unknown'

    # Retrieve children with selected partner
    children = individual.get_children(
        partner_id=selected_partner.id if selected_partner else None)

    # Retrieve the family with parents
    parent_family = None
    if parents:
        parent_family = Family.query.filter(
            Family.children.contains(individual),
            (Family.partner1_id.in_(
                [p.id for p in parents]) | Family.partner2_id.in_(
                [p.id for p in parents]))
        ).first()

    # Retrieve the selected partner's family
    selected_partner_family = None
    if selected_partner:
        selected_partner_family = Family.query.filter(
            ((Family.partner1_id == individual.id) & (
                    Family.partner2_id == selected_partner.id)) |
            ((Family.partner1_id == selected_partner.id) & (
                    Family.partner2_id == individual.id))
        ).first()

    return render_template(
        'family_card.html',
        individual=individual,
        identities=identities,
        selected_identity=selected_identity,
        parents=parents,
        parent_family_ids=parent_family_ids,
        siblings=siblings,
        partners=partners,
        selected_partner=selected_partner,
        partner_family_ids=partner_family_ids,
        children=children,
        parent_family=parent_family,
        selected_partner_family=selected_partner_family,
        RelationshipTypeEnum=RelationshipTypeEnum
    )


# Add Identity Route
@web_individuals_bp.route('/<int:individual_id>/add-identity',
                          methods=['POST'])
@jwt_required()
def add_identity(individual_id):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=individual_id,
                                            user_id=current_user_id).first_or_404()

    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    gender = request.form.get('gender')
    valid_from = request.form.get('valid_from')
    valid_until = request.form.get('valid_until')

    new_identity = Identity(
        individual_id=individual.id,
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        valid_from=valid_from,
        valid_until=valid_until
    )

    try:
        db.session.add(new_identity)
        db.session.commit()
        flash('Identity added successfully.', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f"Error adding identity: {e}")
        flash('An error occurred while adding the identity.',
              'danger')

    return redirect(url_for('web_individuals_bp.get_family_card',
                            individual_id=individual_id))


# Add Parent
@web_individuals_bp.route('/<int:individual_id>/add-parent',
                          methods=['POST'])
@jwt_required()
def add_parent(individual_id):
    current_user_id = get_jwt_identity()
    child = Individual.query.filter_by(id=individual_id,
                                       user_id=current_user_id).first_or_404()
    parent_id = request.form.get('parent_id', type=int)

    if not parent_id:
        flash('Parent individual is required.', 'danger')
        return redirect(url_for('web_individuals_bp.get_family_card',
                                individual_id=individual_id))

    parent = Individual.query.filter_by(id=parent_id,
                                        user_id=current_user_id).first()
    if not parent:
        flash('Parent not found.', 'danger')
        return redirect(url_for('web_individuals_bp.get_family_card',
                                individual_id=individual_id))

    try:
        # Create parent-child relationship
        relationship = Relationship(
            parent_id=parent.id,
            child_id=child.id,
            relationship_type=RelationshipType.PARENT
        )
        db.session.add(relationship)

        # Handle family association
        existing_families = Family.query.filter(
            Family.children.contains(child)).all()
        if existing_families:
            family = existing_families[0]
            if family.partner1_id != parent.id and family.partner2_id != parent.id:
                if not family.partner1_id:
                    family.partner1_id = parent.id
                elif not family.partner2_id:
                    family.partner2_id = parent.id
                else:
                    pass  # Family already has two parents
        else:
            # Create a new family with the parent and child
            family = Family(partner1_id=parent.id)
            db.session.add(family)
            family.children.append(child)

        db.session.commit()
        flash('Parent added successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding parent: {e}")
        flash('An error occurred while adding the parent.', 'danger')

    return redirect(url_for('web_individuals_bp.get_family_card',
                            individual_id=individual_id))


# Add Partner
@web_individuals_bp.route('/<int:individual_id>/add-partner',
                          methods=['POST'])
@jwt_required()
def add_partner(individual_id):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=individual_id,
                                            user_id=current_user_id).first_or_404()
    partner_id = request.form.get('partner_id', type=int)

    if not partner_id:
        flash('Partner individual is required.', 'danger')
        return redirect(url_for('web_individuals_bp.get_family_card',
                                individual_id=individual_id))

    partner = Individual.query.filter_by(id=partner_id,
                                         user_id=current_user_id).first()
    if not partner:
        flash('Partner not found.', 'danger')
        return redirect(url_for('web_individuals_bp.get_family_card',
                                individual_id=individual_id))

    try:
        # Create family (partnership)
        family = Family(
            partner1_id=individual.id,
            partner2_id=partner.id,
            relationship_type=RelationshipTypeEnum.MARRIAGE
            # or default
        )
        db.session.add(family)
        db.session.commit()
        flash('Partner added successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding partner: {e}")
        flash('An error occurred while adding the partner.',
              'danger')

    return redirect(url_for('web_individuals_bp.get_family_card',
                            individual_id=individual_id))


# Update Family
@web_individuals_bp.route('/families/<int:family_id>/update',
                          methods=['POST'])
@jwt_required()
def update_family(family_id):
    current_user_id = get_jwt_identity()
    family = Family.query.get_or_404(family_id)

    # Check if the current user has permission to update the family
    partners_ids = [family.partner1_id, family.partner2_id]
    user_individuals_ids = [ind.id for ind in
                            Individual.query.filter_by(
                                user_id=current_user_id).all()]
    if not any(pid in user_individuals_ids for pid in partners_ids if
               pid):
        flash('You do not have permission to update this family.',
              'danger')
        return redirect(
            url_for('web_individuals_bp.get_individuals'))

    # Update family information
    family.relationship_type = request.form.get(
        'relationship_type') or family.relationship_type
    family.union_date = request.form.get('union_date') or None
    family.union_place = request.form.get('union_place') or None
    family.dissolution_date = request.form.get(
        'dissolution_date') or None

    try:
        db.session.commit()
        flash('Family information updated successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating family: {e}")
        flash('An error occurred while updating the family.',
              'danger')

    return redirect(request.referrer or url_for(
        'web_individuals_bp.get_individuals'))


# Helper Functions
def redirect_to_family_or_individual(related_individual_id,
                                     family_id):
    if related_individual_id:
        return redirect(url_for('web_individuals_bp.get_family_card',
                                individual_id=related_individual_id))
    elif family_id:
        family = Family.query.get(family_id)
        if family:
            return redirect(
                url_for('web_individuals_bp.get_family_card',
                        individual_id=family.partner1_id or family.partner2_id))
    return redirect(url_for('web_individuals_bp.get_individuals'))


def add_relationship_for_new_individual(relationship,
                                        related_individual_id,
                                        new_individual, family_id,
                                        user_id):
    if relationship == 'parent':
        related_individual = Individual.query.filter_by(
            id=related_individual_id, user_id=user_id).first_or_404()
        relationship_obj = Relationship(parent_id=new_individual.id,
                                        child_id=related_individual.id,
                                        relationship_type=RelationshipType.PARENT)
        db.session.add(relationship_obj)
    elif relationship == 'partner':
        related_individual = Individual.query.filter_by(
            id=related_individual_id, user_id=user_id).first_or_404()
        family = Family(partner1_id=related_individual.id,
                        partner2_id=new_individual.id,
                        relationship_type=RelationshipTypeEnum.MARRIAGE)
        db.session.add(family)
    elif relationship == 'child':
        if not family_id:
            raise ValueError("Family ID is required to add a child.")
        family = Family.query.get_or_404(family_id)
        family.children.append(new_individual)
        # Create parent-child relationships
        if family.partner1_id:
            relationship_obj = Relationship(
                parent_id=family.partner1_id,
                child_id=new_individual.id,
                relationship_type=RelationshipType.PARENT
            )
            db.session.add(relationship_obj)
        if family.partner2_id:
            relationship_obj = Relationship(
                parent_id=family.partner2_id,
                child_id=new_individual.id,
                relationship_type=RelationshipType.PARENT
            )
            db.session.add(relationship_obj)
    else:
        raise ValueError(
            f"Invalid relationship type: {relationship}")


def get_family_by_parents(parent1_id, parent2_id):
    return Family.query.filter(
        ((Family.partner1_id == parent1_id) & (
                Family.partner2_id == parent2_id)) |
        ((Family.partner1_id == parent2_id) & (
                Family.partner2_id == parent1_id))
    ).first()


def get_family_by_parent_and_child(parent_id, child_id):
    return Family.query.filter(
        Family.children.any(id=child_id),
        ((Family.partner1_id == parent_id) | (
                Family.partner2_id == parent_id))
    ).first()
