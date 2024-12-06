from flask import (Blueprint, render_template, request, redirect,
                   url_for,
                   flash, current_app as app)
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.individual import Individual
from app.models.family import Family
from sqlalchemy.orm import joinedload
from app.utils.family_utils import (
    get_family_by_parent_and_child,
    get_family_by_parents, add_parent_child_relationship
)
from app.utils.relationships import add_sibling_relationship
from app.models.enums import RelationshipTypeEnum, GenderEnum
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError

web_family_card_bp = Blueprint('web_family_card_bp', __name__,
                               template_folder='templates/family_card')


# Get Family Card
@web_family_card_bp.route('/<int:individual_id>/family-card',
                          methods=['GET'])
@jwt_required()
def get_family_card(individual_id):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(
        id=individual_id, user_id=current_user_id
    ).options(
        joinedload(Individual.identities)
    ).first_or_404()

    identities = individual.identities
    selected_identity_id = request.args.get('identity_id',
                                            type=int) or (
                               individual.primary_identity.id if individual.primary_identity else None
                           )
    selected_identity = next(
        (i for i in identities if i.id == selected_identity_id), None
    )

    parents = individual.get_parents()
    parent_family_ids = {
        parent.id: get_family_by_parent_and_child(parent.id,
                                                  individual.id).id if get_family_by_parent_and_child(
            parent.id, individual.id) else 'Unknown' for parent in
        parents
    }

    siblings = individual.get_siblings()
    partners = individual.get_partners()
    selected_partner_id = request.args.get('partner_id', type=int)
    selected_partner = next(
        (p for p in partners if p.id == selected_partner_id),
        (partners[0] if partners else None)
    )

    partner_family_ids = {
        partner.id: get_family_by_parents(individual.id,
                                          partner.id).id if get_family_by_parents(
            individual.id, partner.id) else 'Unknown' for partner in
        partners
    }

    children = individual.get_children(
        partner_id=selected_partner.id if selected_partner else None)

    parent_family = Family.query.filter(
        Family.children.contains(individual),
        (Family.partner1_id.in_(
            [p.id for p in parents]) | Family.partner2_id.in_(
            [p.id for p in parents]))
    ).first() if parents else None

    selected_partner_family = get_family_by_parents(individual.id,
                                                    selected_partner.id) if selected_partner else None

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
        RelationshipTypeEnum=RelationshipTypeEnum,
        GenderEnum=GenderEnum
    )


# Update Family
@web_family_card_bp.route('/families/<int:family_id>/update',
                          methods=['POST'])
@jwt_required()
def update_family(family_id):
    current_user_id = get_jwt_identity()
    family = Family.query.get_or_404(family_id)

    # Check if the user has permission to modify the family
    partner_ids = [family.partner1_id, family.partner2_id]
    user_individuals_ids = [
        ind.id for ind in
        Individual.query.filter_by(user_id=current_user_id).all()
    ]
    if not any(pid in user_individuals_ids for pid in partner_ids if
               pid):
        flash('You do not have permission to update this family.',
              'danger')
        return redirect(
            url_for('web_individuals_bp.get_individuals'))

    # Update family details
    family.relationship_type = request.form.get(
        'relationship_type') or family.relationship_type
    family.union_date = request.form.get('union_date') or None
    family.union_place = request.form.get('union_place') or None
    family.dissolution_date = request.form.get(
        'dissolution_date') or None

    try:
        db.session.commit()
        flash('Family information updated successfully.', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f"Error updating family: {e}")
        flash('An error occurred while updating the family.',
              'danger')

    return redirect(request.referrer or url_for(
        'web_individuals_bp.get_individuals'))


# Add Child to Family
@web_family_card_bp.route('/add-child', methods=['POST'])
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
            if family.partner1_id:
                add_parent_child_relationship(family.partner1_id,
                                              child.id)
            if family.partner2_id:
                add_parent_child_relationship(family.partner2_id,
                                              child.id)

            # Automatically create sibling relationships
            for sibling in family.children:
                if sibling.id != child.id:
                    add_sibling_relationship(sibling.id, child.id)

            db.session.commit()
            flash('Child added to family successfully.', 'success')
        else:
            flash('Child is already part of the family.', 'info')

        return redirect(url_for('web_family_card_bp.get_family_card',
                                individual_id=family.partner1_id or family.partner2_id))

    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f"Error adding child to family: {e}")
        flash(
            'An error occurred while adding the child to the family.',
            'danger')
        return redirect(request.referrer or url_for(
            'web_individuals_bp.get_individuals'))


# Add Parent
@web_family_card_bp.route('/<int:individual_id>/add-parent',
                          methods=['POST'])
@jwt_required()
def add_parent(individual_id):
    current_user_id = get_jwt_identity()
    child = Individual.query.filter_by(id=individual_id,
                                       user_id=current_user_id).first_or_404()
    parent_id = request.form.get('parent_id', type=int)

    if not parent_id:
        flash('Parent individual is required.', 'danger')
        return redirect(url_for('web_family_card_bp.get_family_card',
                                individual_id=individual_id))

    parent = Individual.query.filter_by(id=parent_id,
                                        user_id=current_user_id).first()

    if not parent:
        flash('Parent not found.', 'danger')
        return redirect(url_for('web_family_card_bp.get_family_card',
                                individual_id=individual_id))

    try:
        add_parent_child_relationship(parent.id, child.id)
        existing_families = Family.query.filter(
            Family.children.contains(child)).all()

        if existing_families:
            family = existing_families[0]
            if family.partner1_id and family.partner2_id:
                for c in family.children:
                    add_parent_child_relationship(parent.id, c.id)
            else:
                if not family.partner1_id:
                    family.partner1_id = parent.id
                elif not family.partner2_id:
                    family.partner2_id = parent.id
        else:
            family = Family(partner1_id=parent.id)
            db.session.add(family)
            family.children.append(child)

        db.session.commit()
        flash('Parent added successfully.', 'success')

    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(
            f"Error adding parent for individual {individual_id}: {e}")
        flash('An error occurred while adding the parent.', 'danger')

    return redirect(url_for('web_family_card_bp.get_family_card',
                            individual_id=individual_id))


# Add Partner
@web_family_card_bp.route('/<int:individual_id>/add-partner',
                          methods=['POST'])
@jwt_required()
def add_partner(individual_id):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=individual_id,
                                            user_id=current_user_id).first_or_404()
    partner_id = request.form.get('partner_id', type=int)

    if not partner_id:
        flash('Partner individual is required.', 'danger')
        return redirect(url_for('web_family_card_bp.get_family_card',
                                individual_id=individual_id))

    partner = Individual.query.filter_by(id=partner_id,
                                         user_id=current_user_id).first()

    if not partner:
        flash('Partner not found.', 'danger')
        return redirect(url_for('web_family_card_bp.get_family_card',
                                individual_id=individual_id))

    try:
        # Check if there's a single-parent family already
        existing_families = Family.query.filter(
            ((Family.partner1_id == individual.id) & (
                Family.partner2_id.is_(None))) |
            ((Family.partner2_id == individual.id) & (
                Family.partner1_id.is_(None)))
        ).all()

        if existing_families:
            # Add this partner as the second parent of the existing family
            family = existing_families[0]
            if not family.partner1_id:
                family.partner1_id = individual.id
                family.partner2_id = partner.id
            elif not family.partner2_id:
                family.partner2_id = partner.id

            # Create parent-child relationships for all existing children
            for child in family.children:
                add_parent_child_relationship(partner.id, child.id)

            # Set a default relationship type if not set
            if not family.relationship_type:
                family.relationship_type = RelationshipTypeEnum.MARRIAGE
        else:
            # No single-parent family found, create a new family
            family = Family(
                partner1_id=individual.id,
                partner2_id=partner.id,
                relationship_type=RelationshipTypeEnum.MARRIAGE
            )
            db.session.add(family)

        db.session.commit()
        flash('Partner added successfully.', 'success')

    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(
            f"Error adding partner for individual {individual_id}: {e}")
        flash('An error occurred while adding the partner.',
              'danger')

    return redirect(url_for('web_family_card_bp.get_family_card',
                            individual_id=individual_id))
