from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.identity import Identity


class IdentitySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Identity
        load_instance = True
