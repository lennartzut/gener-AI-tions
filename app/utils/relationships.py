from app.models.relationship import Relationship
from app.extensions import db
from app.models.enums import RelationshipType


def relationship_exists(parent_id=None, child_id=None,
                        sibling1_id=None, sibling2_id=None,
                        relationship_type=None):
    """
    Checks if a relationship of a given type already exists.
    """
    if relationship_type == RelationshipType.PARENT:
        return Relationship.query.filter_by(
            parent_id=parent_id,
            child_id=child_id,
            relationship_type=RelationshipType.PARENT
        ).first() is not None

    elif relationship_type == RelationshipType.SIBLING:
        return Relationship.query.filter_by(
            sibling1_id=sibling1_id,
            sibling2_id=sibling2_id,
            relationship_type=RelationshipType.SIBLING
        ).first() is not None

    return False


def add_parent_child_relationship(parent_id, child_id):
    """
    Adds a parent-child relationship if it doesn't already exist.
    """
    if not relationship_exists(parent_id=parent_id,
                               child_id=child_id,
                               relationship_type=RelationshipType.PARENT):
        new_rel = Relationship(
            parent_id=parent_id,
            child_id=child_id,
            relationship_type=RelationshipType.PARENT
        )
        db.session.add(new_rel)


def add_sibling_relationship(sibling1_id, sibling2_id):
    """
    Adds a sibling relationship if it doesn't already exist.
    """
    if not relationship_exists(sibling1_id=sibling1_id,
                               sibling2_id=sibling2_id,
                               relationship_type=RelationshipType.SIBLING):
        new_rel = Relationship(
            sibling1_id=sibling1_id,
            sibling2_id=sibling2_id,
            relationship_type=RelationshipType.SIBLING
        )
        db.session.add(new_rel)
