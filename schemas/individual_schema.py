from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.individual import Individual


class IndividualSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Individual
        load_instance = True

    @staticmethod
    def get_identity_schema():
        from schemas.identity_schema import IdentitySchema
        return IdentitySchema(many=True)

    parents = fields.Method("get_parents")
    siblings = fields.Method("get_siblings")
    partners = fields.Method("get_partners")
    children = fields.Method("get_children")
    identities = fields.Method("get_identities")

    def get_parents(self, obj):
        """Fetch and serialize parents of the individual."""
        return IndividualSchema(many=True).dump(obj.get_parents())

    def get_siblings(self, obj):
        """Fetch and serialize siblings of the individual."""
        return IndividualSchema(many=True).dump(obj.get_siblings())

    def get_partners(self, obj):
        """Fetch and serialize partners of the individual."""
        return IndividualSchema(many=True).dump(obj.get_partners())

    def get_children(self, obj):
        """Fetch and serialize children of the individual."""
        return IndividualSchema(many=True).dump(obj.get_children())

    def get_identities(self, obj):
        """Fetch and serialize identities of the individual."""
        identity_schema = self.get_identity_schema()
        return identity_schema.dump(obj.identities)
