from app.models.relationship import Relationship
from app.extensions import db
from app.models.enums import FamilyRelationshipEnum


def relationship_exists(parent_id=None, child_id=None,
                        sibling1_id=None, sibling2_id=None,
                        relationship_type=None):
    if relationship_type == FamilyRelationshipEnum.PARENT:
        return Relationship.query.filter_by(
            parent_id=parent_id,
            child_id=child_id,
            relationship_type=FamilyRelationshipEnum.PARENT
        ).first() is not None

    elif relationship_type == FamilyRelationshipEnum.SIBLING:
        return Relationship.query.filter_by(
            sibling1_id=sibling1_id,
            sibling2_id=sibling2_id,
            relationship_type=FamilyRelationshipEnum.SIBLING
        ).first() is not None

    return False


def add_parent_child_relationship(parent_id, child_id):
    if parent_id == child_id:
        raise ValueError("An individual cannot be their own parent.")
    if not relationship_exists(parent_id=parent_id,
                               child_id=child_id,
                               relationship_type=FamilyRelationshipEnum.PARENT):
        new_rel = Relationship(
            parent_id=parent_id,
            child_id=child_id,
            relationship_type=FamilyRelationshipEnum.PARENT
        )
        db.session.add(new_rel)


def add_sibling_relationship(sibling1_id, sibling2_id):
    if not relationship_exists(sibling1_id=sibling1_id,
                               sibling2_id=sibling2_id,
                               relationship_type=FamilyRelationshipEnum.SIBLING):
        new_rel = Relationship(
            sibling1_id=sibling1_id,
            sibling2_id=sibling2_id,
            relationship_type=FamilyRelationshipEnum.SIBLING
        )
        db.session.add(new_rel)
