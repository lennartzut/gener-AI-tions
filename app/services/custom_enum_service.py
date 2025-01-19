from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.custom_enum import CustomEnum


class CustomEnumService:
    def __init__(self, SessionLocal: Session):
        self.SessionLocal = SessionLocal

    def create_custom_enum(self, user_id: int, enum_name: str,
                           enum_value: str) -> CustomEnum:
        new_enum = CustomEnum(user_id=user_id, enum_name=enum_name,
                              enum_value=enum_value)
        self.SessionLocal.add(new_enum)
        self.SessionLocal.commit()
        self.SessionLocal.refresh(new_enum)
        return new_enum

    def get_custom_enum_by_id(self, enum_id: int) -> Optional[
        CustomEnum]:
        return self.SessionLocal.query(CustomEnum).filter(
            CustomEnum.id == enum_id).first()

    def update_custom_enum(self, enum_id: int, **kwargs) -> Optional[
        CustomEnum]:
        enum = self.get_custom_enum_by_id(enum_id)
        if not enum:
            return None
        for k, v in kwargs.items():
            if hasattr(enum, k):
                setattr(enum, k, v)
        self.SessionLocal.commit()
        self.SessionLocal.refresh(enum)
        return enum

    def delete_custom_enum(self, enum_id: int) -> Optional[
        CustomEnum]:
        enum = self.get_custom_enum_by_id(enum_id)
        if enum:
            self.SessionLocal.delete(enum)
            self.SessionLocal.commit()
            return enum
        return None

    def list_custom_enums_by_name(self, user_id: int,
                                  enum_name: str) -> List[
        CustomEnum]:
        return self.SessionLocal.query(CustomEnum).filter(
            CustomEnum.user_id == user_id,
            CustomEnum.enum_name == enum_name).all()
