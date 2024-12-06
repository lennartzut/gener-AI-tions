from app.models.family import Family
from app.models.individual import Individual
from app.models.enums import RelationshipTypeEnum
from app.extensions import db
from app.utils.relationships import add_parent_child_relationship


def get_family_by_parents(parent1_id, parent2_id):
    """
    Retrieves a family instance given two parent IDs.
    """
    return Family.query.filter(
        ((Family.partner1_id == parent1_id) & (
                    Family.partner2_id == parent2_id)) |
        ((Family.partner1_id == parent2_id) & (
                    Family.partner2_id == parent1_id))
    ).first()


def get_family_by_parent_and_child(parent_id, child_id):
    """
    Retrieves a family instance that includes the given parent and child.
    """
    return Family.query.filter(
        Family.children.any(id=child_id),
        ((Family.partner1_id == parent_id) | (
                    Family.partner2_id == parent_id))
    ).first()


def add_relationship_for_new_individual(relationship,
                                        related_individual_id,
                                        new_individual, family_id,
                                        user_id):
    """
    Adds a new relationship for a new individual based on the given relationship type.
    The relationship can be as a parent, partner, or child.
    """
    if relationship == 'parent':
        add_parent_relationship(related_individual_id,
                                new_individual.id, user_id)
    elif relationship == 'partner':
        add_partner_relationship(related_individual_id,
                                 new_individual)
    elif relationship == 'child':
        add_child_relationship(family_id, new_individual)
    else:
        raise ValueError(
            f"Invalid relationship type: {relationship}")

    db.session.commit()


def add_parent_relationship(related_individual_id, new_individual_id,
                            user_id):
    """
    Helper function to add a parent-child relationship.
    """
    related_individual = Individual.query.filter_by(
        id=related_individual_id, user_id=user_id).first_or_404()
    add_parent_child_relationship(new_individual_id,
                                  related_individual.id)


def add_partner_relationship(related_individual_id, new_individual):
    """
    Helper function to add a partner relationship.
    """
    related_individual = Individual.query.filter_by(
        id=related_individual_id).first_or_404()
    family = Family(
        partner1_id=related_individual.id,
        partner2_id=new_individual.id,
        relationship_type=RelationshipTypeEnum.MARRIAGE
    )
    db.session.add(family)


def add_child_relationship(family_id, new_individual):
    """
    Helper function to add a new individual as a child in a family.
    """
    if not family_id:
        raise ValueError("Family ID is required to add a child.")
    family = Family.query.get_or_404(family_id)
    family.children.append(new_individual)

    # Add parent-child relationships
    if family.partner1_id:
        add_parent_child_relationship(family.partner1_id,
                                      new_individual.id)
    if family.partner2_id:
        add_parent_child_relationship(family.partner2_id,
                                      new_individual.id)
