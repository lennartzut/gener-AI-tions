from sqlalchemy.exc import SQLAlchemyError
from app.extensions import SessionLocal
from app.models.relationship import Relationship
from app.models.enums_model import RelationshipTypeEnum

def relationship_exists(project_id, individual_id=None, related_id=None, relationship_type=None):
    """
    Check if a Relationship row already exists with the given parameters.
    E.g., if relationship_type == RelationshipTypeEnum.PARENT, we filter for parent-child.
    """
    with SessionLocal() as session:
        query = session.query(Relationship).filter(Relationship.project_id == project_id)
        if relationship_type == RelationshipTypeEnum.PARENT:
            query = query.filter_by(
                individual_id=individual_id,
                related_id=related_id,
                relationship_type=RelationshipTypeEnum.PARENT.value
            )
            return query.first() is not None

        if relationship_type == RelationshipTypeEnum.PARTNER:
            query = query.filter_by(
                individual_id=individual_id,
                related_id=related_id,
                relationship_type=RelationshipTypeEnum.PARTNER.value
            )
            return query.first() is not None

        return False

def add_parent_child_relationship(parent_individual_id, child_individual_id, project_id):
    """
    Create a 'parent' relationship if it doesn't already exist.
    """
    if parent_individual_id == child_individual_id:
        raise ValueError("An individual cannot be their own parent.")

    with SessionLocal() as session:
        # Check if this parent-child relationship already exists
        if not relationship_exists(
            project_id=project_id,
            individual_id=parent_individual_id,
            related_id=child_individual_id,
            relationship_type=RelationshipTypeEnum.PARENT
        ):
            new_rel = Relationship(
                individual_id=parent_individual_id,
                related_id=child_individual_id,
                relationship_type=RelationshipTypeEnum.PARENT.value,
                project_id=project_id
            )
            try:
                session.add(new_rel)
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                raise e