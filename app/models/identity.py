from sqlalchemy.sql import func
from sqlalchemy import (Column, Boolean, Integer, String, Date,
                        DateTime, Enum,
                        ForeignKey, CheckConstraint,
                        UniqueConstraint)
from sqlalchemy.orm import relationship
from datetime import date
from app.models.base import Base
from app.models.enums import GenderEnum


class Identity(Base):
    __tablename__ = 'identities'
    __table_args__ = (
        UniqueConstraint('individual_id', 'valid_from',
                         'valid_until',
                         name='uix_identity_validity'),
        CheckConstraint(
            'valid_until IS NULL OR valid_until > valid_from',
            name='chk_validity_dates'),
    )

    id = Column(Integer, primary_key=True)
    individual_id = Column(Integer, ForeignKey('individuals.id',
                                               ondelete='CASCADE'),
                           nullable=False, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True)
    valid_from = Column(Date, nullable=True)
    valid_until = Column(Date, nullable=True)
    is_primary = Column(Boolean, nullable=False,
                        server_default='false')
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    individual = relationship('Individual',
                              back_populates='identities')

    def __repr__(self):
        gender_val = self.gender.value if self.gender else 'None'
        return f"<Identity(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}', gender='{gender_val}')>"

    def full_name(self):
        names = [self.first_name, self.last_name]
        return ' '.join(filter(None, names)).strip() or "Unnamed"

    def is_valid(self):
        today = date.today()
        if self.valid_from and today < self.valid_from:
            return False
        if self.valid_until and today > self.valid_until:
            return False
        return True
