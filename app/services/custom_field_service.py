from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.custom_field import CustomField, CustomFieldValue


class CustomFieldService:
    def __init__(self, SessionLocal: Session):
        self.SessionLocal = SessionLocal

    def create_custom_field(self, user_id: int, table_name: str,
                            field_name: str,
                            field_type: str) -> CustomField:
        new_field = CustomField(user_id=user_id,
                                table_name=table_name,
                                field_name=field_name,
                                field_type=field_type)
        self.SessionLocal.add(new_field)
        self.SessionLocal.commit()
        self.SessionLocal.refresh(new_field)
        return new_field

    def get_custom_field_by_id(self, field_id: int) -> Optional[
        CustomField]:
        return self.SessionLocal.query(CustomField).filter(
            CustomField.id == field_id).first()

    def update_custom_field(self, field_id: int, **kwargs) -> \
    Optional[CustomField]:
        field = self.get_custom_field_by_id(field_id)
        if not field:
            return None
        for k, v in kwargs.items():
            if hasattr(field, k):
                setattr(field, k, v)
        self.SessionLocal.commit()
        self.SessionLocal.refresh(field)
        return field

    def delete_custom_field(self, field_id: int) -> Optional[
        CustomField]:
        field = self.get_custom_field_by_id(field_id)
        if field:
            self.SessionLocal.delete(field)
            self.SessionLocal.commit()
            return field
        return None

    def list_custom_fields_for_user(self, user_id: int) -> List[
        CustomField]:
        return self.SessionLocal.query(CustomField).filter(
            CustomField.user_id == user_id).all()


class CustomFieldValueService:
    def __init__(self, SessionLocal: Session):
        self.SessionLocal = SessionLocal

    def create_custom_field_value(self, custom_field_id: int,
                                  record_id: int,
                                  value: str) -> CustomFieldValue:
        new_value = CustomFieldValue(custom_field_id=custom_field_id,
                                     record_id=record_id,
                                     value=value)
        self.SessionLocal.add(new_value)
        self.SessionLocal.commit()
        self.SessionLocal.refresh(new_value)
        return new_value

    def get_custom_field_value_by_id(self, value_id: int) -> \
    Optional[CustomFieldValue]:
        return self.SessionLocal.query(CustomFieldValue).filter(
            CustomFieldValue.id == value_id).first()

    def update_custom_field_value(self, value_id: int, **kwargs) -> \
    Optional[CustomFieldValue]:
        val = self.get_custom_field_value_by_id(value_id)
        if not val:
            return None
        for k, v in kwargs.items():
            if hasattr(val, k):
                setattr(val, k, v)
        self.SessionLocal.commit()
        self.SessionLocal.refresh(val)
        return val

    def delete_custom_field_value(self, value_id: int) -> Optional[
        CustomFieldValue]:
        val = self.get_custom_field_value_by_id(value_id)
        if val:
            self.SessionLocal.delete(val)
            self.SessionLocal.commit()
            return val
        return None

    def list_values_for_field(self, custom_field_id: int) -> List[
        CustomFieldValue]:
        return self.SessionLocal.query(CustomFieldValue).filter(
            CustomFieldValue.custom_field_id == custom_field_id).all()
