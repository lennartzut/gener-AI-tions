from extensions import db


class Identity(db.Model):
    __tablename__ = 'identities'

    id = db.Column(db.Integer, primary_key=True)
    individual_id = db.Column(db.Integer,
                              db.ForeignKey('individuals.id'),
                              nullable=False)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    gender = db.Column(db.String, nullable=True)
    valid_from = db.Column(db.Date, nullable=True)
    valid_until = db.Column(db.Date, nullable=True)

    # Relationships
    individual = db.relationship('Individual',
                                 back_populates='identities')

    def __repr__(self):
        return f"<Identity id={self.id}, first_name={self.first_name}, last_name={self.last_name}>"
