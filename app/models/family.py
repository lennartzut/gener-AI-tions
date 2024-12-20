from sqlalchemy import (Column, Integer, String, Text, Date,
                        ForeignKey, Enum, DateTime)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
from app.models.enums import LegalRelationshipEnum
from app.models.associations import family_children_association_table


class Family(Base):
    __tablename__ = 'families'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id',
                                            ondelete='CASCADE'),
                        nullable=False)
    partner1_id = Column(Integer, ForeignKey('individuals.id',
                                             ondelete='CASCADE'),
                         nullable=True)
    partner2_id = Column(Integer, ForeignKey('individuals.id',
                                             ondelete='CASCADE'),
                         nullable=True)
    relationship_type = Column(Enum(LegalRelationshipEnum),
                               nullable=False)
    union_date = Column(Date, nullable=True)
    union_place = Column(String(100), nullable=True)
    dissolution_date = Column(Date, nullable=True)
    name = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    project = relationship('Project', back_populates='families')
    partner1 = relationship('Individual', foreign_keys=[partner1_id],
                            back_populates='families_as_partner1')
    partner2 = relationship('Individual', foreign_keys=[partner2_id],
                            back_populates='families_as_partner2')

    # This relationship might be optional if we store family_id in Relationship:
    relationships = relationship('Relationship',
                                 back_populates='family')
    children = relationship('Individual',
                            secondary=family_children_association_table,
                            back_populates='families')

    @property
    def partners(self):
        return [p for p in [self.partner1, self.partner2] if p]

    def add_child(self, child):
        if child not in self.children:
            self.children.append(child)

    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)

    def add_partner(self, partner):
        if partner == self.partner1 or partner == self.partner2:
            raise ValueError(
                "This partner is already part of the family.")
        if not self.partner1:
            self.partner1 = partner
        elif not self.partner2:
            self.partner2 = partner
        else:
            raise ValueError(
                "A family cannot have more than two partners.")

    def validate_family(self):
        if self.partner1 and self.partner2 and self.partner1 == self.partner2:
            raise ValueError(
                "Partners in a family cannot be the same individual.")

    def __repr__(self):
        return (
            f"<Family(id={self.id}, partner1_id={self.partner1_id}, "
            f"partner2_id={self.partner2_id}, relationship_type={self.relationship_type})>")
