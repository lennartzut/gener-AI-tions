from app.models.relationship import Relationship
from app.models.enums import FamilyRelationshipEnum


def relationship_exists(project_id, parent_id=None, child_id=None,
                        sibling1_id=None, sibling2_id=None,
                        relationship_type=None):
    query = Relationship.query.filter(
        Relationship.project_id == project_id)
    if relationship_type == FamilyRelationshipEnum.PARENT:
        query = query.filter_by(parent_id=parent_id,
                                child_id=child_id,
                                relationship_type=FamilyRelationshipEnum.PARENT)
        return query.first() is not None
    elif relationship_type == FamilyRelationshipEnum.SIBLING:
        # If we ever reimplement sibling logic with project_id fields added:
        query = query.filter_by(sibling1_id=sibling1_id,
                                sibling2_id=sibling2_id,
                                relationship_type=FamilyRelationshipEnum.SIBLING)
        return query.first() is not None
    return False


def add_parent_child_relationship(parent_id, child_id, project_id):
    if parent_id == child_id:
        raise ValueError("An individual cannot be their own parent.")
    if not relationship_exists(project_id, parent_id=parent_id,
                               child_id=child_id,
                               relationship_type=FamilyRelationshipEnum.PARENT):
        new_rel = Relationship(
            parent_id=parent_id,
            child_id=child_id,
            relationship_type=FamilyRelationshipEnum.PARENT,
            project_id=project_id
        )
        db.session.add(new_rel)


def add_sibling_relationship(sibling1_id, sibling2_id, project_id):
    if not relationship_exists(project_id, sibling1_id=sibling1_id,
                               sibling2_id=sibling2_id,
                               relationship_type=FamilyRelationshipEnum.SIBLING):
        new_rel = Relationship(
            sibling1_id=sibling1_id,
            sibling2_id=sibling2_id,
            project_id=project_id,
            relationship_type=FamilyRelationshipEnum.SIBLING
        )
        db.session.add(new_rel)
