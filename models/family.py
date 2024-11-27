from extensions import db


class Family(db.Model):
    __tablename__ = 'families'

    id = db.Column(db.Integer, primary_key=True)
    partner1_id = db.Column(db.Integer,
                            db.ForeignKey('individuals.id'),
                            nullable=False)
    partner2_id = db.Column(db.Integer,
                            db.ForeignKey('individuals.id'),
                            nullable=False)
    relationship_type = db.Column(db.String(100), nullable=True)
    union_date = db.Column(db.Date, nullable=True)
    union_place = db.Column(db.String(100), nullable=True)
    dissolution_date = db.Column(db.Date, nullable=True)

    partner1 = db.relationship(
        'Individual',
        foreign_keys=[partner1_id],
        back_populates='families_as_partner1'
    )
    partner2 = db.relationship(
        'Individual',
        foreign_keys=[partner2_id],
        back_populates='families_as_partner2'
    )

    def __repr__(self):
        return f'<Family id={self.id}, partner1_id={self.partner1_id}, partner2_id={self.partner2_id}>'
