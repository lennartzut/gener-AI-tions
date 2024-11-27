from extensions import db


class Relationship(db.Model):
    __tablename__ = 'relationships'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer,
                          db.ForeignKey('individuals.id'),
                          nullable=False)
    child_id = db.Column(db.Integer, db.ForeignKey('individuals.id'),
                         nullable=False)
    relationship_type = db.Column(db.String(100), nullable=False)

    parent = db.relationship(
        'Individual',
        foreign_keys=[parent_id],
        back_populates='child_relationships'
    )
    child = db.relationship(
        'Individual',
        foreign_keys=[child_id],
        back_populates='parent_relationships'
    )

    def __repr__(self):
        return (
            f"<Relationship id={self.id}, parent_id={self.parent_id}, "
            f"child_id={self.child_id}, relationship_type={self.relationship_type}>"
        )
