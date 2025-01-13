from datetime import date

from sqlalchemy import (Column, Boolean, Integer, String, Date, \
                        DateTime, Enum, ForeignKey, CheckConstraint,
                        UniqueConstraint,
                        Index, text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base_model import Base
from app.models.enums_model import GenderEnum


class Identity(Base):
    __tablename__ = 'identities'
    __table_args__ = (
        UniqueConstraint('individual_id', 'identity_number',
                         name='uix_identity_identity_number'),
        CheckConstraint(
            'valid_until IS NULL OR valid_until > valid_from',
            name='chk_validity_dates'
        ),
        Index(
            'uix_individual_primary_identity',
            'individual_id',
            unique=True,
            postgresql_where=text('is_primary = true')
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    individual_id = Column(Integer, ForeignKey('individuals.id',
                                               ondelete='CASCADE'),
                           nullable=False, index=True)
    identity_number = Column(
        Integer,
        nullable=False
    )
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True)
    valid_from = Column(Date, nullable=True)
    valid_until = Column(Date, nullable=True)
    is_primary = Column(Boolean, nullable=False, server_default='false')
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    # Relationships
    individual = relationship('Individual',
                              back_populates='identities')

    def full_name(self) -> str:
        """Returns the full name of the identity."""
        names = [self.first_name, self.last_name]
        full_name = ' '.join(filter(None, names)).strip()
        return full_name if full_name else "Unnamed"

    def is_valid(self) -> bool:
        """Checks if the identity is valid based on the current date."""
        today = date.today()
        if (self.valid_from and today < self.valid_from) or (
                self.valid_until and today > self.valid_until):
            return False
        return True

    def __repr__(self) -> str:
        return (
            f"<Identity(id={self.id}, individual_id={self.individual_id}, "
            f"first_name='{self.first_name}', last_name='{self.last_name}', gender='{self.gender}')>"
        )
