from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models import Individual


class IndividualSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Individual
        load_instance = True
