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


@web_individuals_bp.route('/', methods=['GET'])
@jwt_required()
def get_individuals():
    """
    Displays a list of individuals for the current user.
    Supports optional search query and limit parameters.
    """
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
                           individuals=individuals)


@web_individuals_bp.route('/create', methods=['GET', 'POST'])
@jwt_required()
def create_individual():
    """
    Creates a new individual along with a default identity.
    GET: Renders the form for creating an individual.
    POST: Processes the submitted form and creates an individual.
    """
    current_user_id = get_jwt_identity()
    relationship = request.args.get('relationship')
    related_individual_id = request.args.get('related_individual_id',
                                             type=int)
    family_id = request.args.get('family_id', type=int)

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        gender_str = request.form.get('gender')
        birth_date = request.form.get('birth_date')
        birth_place = request.form.get('birth_place')
        death_date = request.form.get('death_date')
        death_place = request.form.get('death_place')

        if not first_name or not last_name or not gender_str:
            flash("First name, last name, and gender are required.",
                  'error')
            return redirect(url_for(
                'web_individuals_bp.create_individual',
                relationship=relationship,
                related_individual_id=related_individual_id,
                family_id=family_id
            ))

        try:
            gender = GenderEnum(gender_str)

            # Create the new individual
            new_individual = Individual(
                user_id=current_user_id,
                birth_date=birth_date,
                birth_place=birth_place,
                death_date=death_date,
                death_place=death_place,
            )
            db.session.add(new_individual)
            db.session.flush()  # Ensure new_individual.id is available

            # Create the default identity
            default_identity = Identity(
                individual_id=new_individual.id,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                valid_from=birth_date
            )
            db.session.add(default_identity)

            # Handle relationships if specified
            if relationship and related_individual_id:
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

        except ValueError:
            flash(f"Invalid gender value: {gender_str}", 'error')
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Error creating individual: {e}")
            flash('An error occurred while creating the individual.',
                  'error')

    return render_template('create_individual.html',
                           GenderEnum=GenderEnum)


@web_individuals_bp.route('/<int:individual_id>/update',
                          methods=['POST'])
@jwt_required()
def update_individual(individual_id):
    """
    Updates the details of an existing individual.
    """
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=individual_id,
                                            user_id=current_user_id).first_or_404()

    try:
        # Update individual fields
        individual.birth_date = request.form.get(
            'birth_date') or None
        individual.birth_place = request.form.get(
            'birth_place') or None
        individual.death_date = request.form.get(
            'death_date') or None
        individual.death_place = request.form.get(
            'death_place') or None

        # Update identity fields
        identity_id = request.args.get('identity_id', type=int)
        identity = Identity.query.filter_by(id=identity_id,
                                            individual_id=individual_id).first()
        if identity:
            identity.first_name = request.form.get(
                'first_name') or None
            identity.last_name = request.form.get(
                'last_name') or None

        db.session.commit()
        flash('Individual updated successfully.', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f"Error updating individual: {e}")
        flash('An error occurred while updating the individual.',
              'danger')

    return redirect(url_for('web_individuals_bp.get_family_card',
                            individual_id=individual_id))


@web_individuals_bp.route('/<int:individual_id>/delete',
                          methods=['POST'])
@jwt_required()
def delete_individual(individual_id: int):
    """
    Deletes an individual and all associated data.
    """
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=individual_id,
                                            user_id=current_user_id).first_or_404()

    try:
        db.session.delete(individual)
        db.session.commit()
        flash('Individual deleted successfully.', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f"Error deleting individual: {e}")
        flash('An error occurred while deleting the individual.',
              'danger')

    return redirect(url_for('web_individuals_bp.get_individuals'))


@web_individuals_bp.route('/<int:individual_id>/family-card',
                          methods=['GET'])
@jwt_required()
def get_family_card(individual_id):
    """
    Displays the family card of an individual.
    """
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(
        id=individual_id,
        user_id=current_user_id
    ).options(
        joinedload(Individual.identities)
    ).first_or_404()

    identities = individual.identities
    selected_identity = get_selected_identity(
        identities,
        request.args.get('identity_id', type=int)
    )

    # Get family details
    parents, siblings, partners, children, parent_family, partner_family = get_family_details(
        individual)

    # Map parent IDs to their family IDs
    parent_family_ids = {}
    for parent in parents:
        family = Family.query.filter(
            Family.children.any(id=individual.id),
            (Family.partner1_id == parent.id) | (
                        Family.partner2_id == parent.id)
        ).first()
        parent_family_ids[parent.id] = family.id if family else None

    return render_template(
        'family_card.html',
        individual=individual,
        identities=identities,
        selected_identity=selected_identity,
        parents=parents,
        siblings=siblings,
        partners=partners,
        children=children,
        parent_family=parent_family,
        partner_family=partner_family,
        parent_family_ids=parent_family_ids,
        RelationshipTypeEnum=RelationshipTypeEnum
    )


# Helper Functions
def add_relationship_for_new_individual(relationship,
                                        related_individual_id,
                                        new_individual, family_id,
                                        user_id):
    """
    Adds a relationship for a newly created individual based on the specified type.

    :param relationship: The type of relationship (parent, partner, child).
    :param related_individual_id: ID of the related individual.
    :param new_individual: The newly created individual object.
    :param family_id: Optional ID of an existing family.
    :param user_id: Current user's ID.
    """
    related_individual = Individual.query.filter_by(
        id=related_individual_id, user_id=user_id).first_or_404()

    if relationship == 'parent':
        # Create a parent-child relationship
        relationship_obj = Relationship(
            parent_id=new_individual.id,
            child_id=related_individual.id,
            relationship_type=RelationshipType.PARENT
        )
        db.session.add(relationship_obj)

        # Associate the parent with a family
        existing_families = Family.query.filter(
            Family.children.any(id=related_individual.id)).all()
        if existing_families:
            family = existing_families[0]
            if not family.partner1_id:
                family.partner1_id = new_individual.id
            elif not family.partner2_id:
                family.partner2_id = new_individual.id
        else:
            family = Family(partner1_id=new_individual.id)
            db.session.add(family)
            family.children.append(related_individual)

    elif relationship == 'partner':
        # Create a partnership between the two individuals
        family = Family(
            partner1_id=related_individual.id,
            partner2_id=new_individual.id,
            relationship_type=RelationshipTypeEnum.MARRIAGE
        )
        db.session.add(family)

    elif relationship == 'child':
        if family_id:
            family = Family.query.get_or_404(family_id)
            family.children.append(new_individual)
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
            raise ValueError("Family ID is required to add a child.")
    else:
        raise ValueError(
            f"Invalid relationship type: {relationship}")


def redirect_to_family_or_individual(related_individual_id,
                                     family_id):
    """
    Redirects to the appropriate individual or family card based on the IDs.

    :param related_individual_id: ID of the related individual.
    :param family_id: ID of the related family.
    :return: Redirect to the appropriate route.
    """
    if related_individual_id:
        return redirect(url_for('web_individuals_bp.get_family_card',
                                individual_id=related_individual_id))
    elif family_id:
        family = Family.query.get(family_id)
        if family:
            return redirect(
                url_for('web_individuals_bp.get_family_card',
                        individual_id=family.partner1_id or family.partner2_id)
            )
    return redirect(url_for('web_individuals_bp.get_individuals'))


def get_selected_identity(identities, selected_identity_id):
    """
    Retrieves the selected identity or defaults to the primary identity.

    :param identities: List of identity objects.
    :param selected_identity_id: ID of the selected identity.
    :return: The selected identity or None if not found.
    """
    if not identities:
        return None
    return next(
        (i for i in identities if i.id == selected_identity_id),
        identities[0])


def get_family_details(individual):
    """
    Retrieves family details such as parents, siblings, partners, and children.

    :param individual: The individual for whom to fetch family details.
    :return: A tuple containing family details (parents, siblings, partners, children, parent_family, partner_family).
    """
    parents = individual.get_parents()
    siblings = individual.get_siblings()
    partners = individual.get_partners()

    parent_family = None
    if parents:
        parent_family = Family.query.filter(
            Family.children.any(id=individual.id),
            (Family.partner1_id.in_([p.id for p in parents]) |
             Family.partner2_id.in_([p.id for p in parents]))
        ).first()

    selected_partner = partners[0] if partners else None
    partner_family = None
    if selected_partner:
        partner_family = Family.query.filter(
            ((Family.partner1_id == individual.id) & (
                    Family.partner2_id == selected_partner.id)) |
            ((Family.partner1_id == selected_partner.id) & (
                    Family.partner2_id == individual.id))
        ).first()

    children = individual.get_children(
        partner_id=selected_partner.id if selected_partner else None)
    return parents, siblings, partners, children, parent_family, partner_family
