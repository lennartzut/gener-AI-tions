from datetime import date, datetime
from typing import Optional


class ValidationUtils:
    @staticmethod
    def parse_date(date_str: Optional[str]) -> Optional[datetime.date]:
        """
        Parses a date string in the format YYYY-MM-DD.
        Returns a date object or None if the input is invalid or empty.
        """
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. Expected format is YYYY-MM-DD.")

    @staticmethod
    def validate_date_order(
        valid_from: Optional[datetime.date], valid_until: Optional[datetime.date], error_message: str
    ):
        """
        Validates that `valid_from` is before `valid_until`.
        Raises a ValueError with the provided error message if invalid.
        """
        if valid_from and valid_until and valid_from > valid_until:
            raise ValueError(error_message)

    @staticmethod
    def calculate_age(birth_date: Optional[date],
                      death_date: Optional[date] = None) -> Optional[
        int]:
        if not birth_date:
            return None
        end_date = death_date or date.today()
        age = end_date.year - birth_date.year - (
                    (end_date.month, end_date.day) < (
            birth_date.month, birth_date.day))
        return age
