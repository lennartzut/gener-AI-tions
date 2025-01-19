import logging
from app.models.enums_model import InitialRelationshipEnum
from app.schemas.relationship_schema import RelationshipCreate

logger = logging.getLogger(__name__)

def map_relationship_create(r_create: RelationshipCreate) -> dict:
    """
    Convert a RelationshipCreate Pydantic model into a dict suitable
    for creating a Relationship model. Moves relationship_detail to
    either relationship_detail_horizontal or relationship_detail_vertical.
    """
    # Start with everything except 'relationship_detail' from the model:
    data = r_create.model_dump(exclude={"relationship_detail"})

    # Log the incoming relationship creation data
    logger.debug(f"Mapping RelationshipCreate: {r_create.model_dump()}")

    # If user provided a detail, decide horizontal vs vertical:
    if r_create.relationship_detail:
        if r_create.initial_relationship in {
            InitialRelationshipEnum.CHILD, InitialRelationshipEnum.PARENT
        }:
            data["relationship_detail_horizontal"] = r_create.relationship_detail
        elif r_create.initial_relationship == InitialRelationshipEnum.PARTNER:
            data["relationship_detail_vertical"] = r_create.relationship_detail

    return data