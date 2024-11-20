from extensions import db


class Relationship(db.Model):
    __tablename__ = 'relationships'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('individuals.id'), nullable=False)
    related_individual_id = db.Column(db.Integer, db.ForeignKey('individuals.id'), nullable=False)
    relationship_type = db.Column(db.String(100), nullable=False)

    parent = db.relationship(
        'Individual',
        foreign_keys=[parent_id],
        overlaps="children_relationships, parent_relationship"
    )
    related_individual = db.relationship(
        'Individual',
        foreign_keys=[related_individual_id],
        overlaps="parent_relationships, child_relationship"
    )

    def __repr__(self):
        return (
            f"<Relationship id={self.id}, parent_id={self.parent_id}, "
            f"related_individual_id={self.related_individual_id}, relationship_type={self.relationship_type}>"
        )
