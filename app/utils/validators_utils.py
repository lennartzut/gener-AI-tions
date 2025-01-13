import logging
from typing import List, Tuple, Optional
from datetime import date, datetime

logger = logging.getLogger(__name__)

class ValidationUtils:
    @staticmethod
    def parse_date(date_str: Optional[str]) -> Optional[date]:
        """
        Parses a date string in the format YYYY-MM-DD.
        Returns a date object or None if the input is invalid or empty.
        """
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(
                f"Invalid date format: {date_str}. Expected format is YYYY-MM-DD.")

    @staticmethod
    def validate_date_order(validations: List[
        Tuple[Optional[date], Optional[date], str]]):
        """
        Validates that dates in the list (valid_from, valid_until, error_message) are in correct order.
        """
        for valid_from, valid_until, error_message in validations:
            if valid_from and valid_until and valid_from > valid_until:
                logger.error(
                    f"Validation failed: {valid_from} > {valid_until}. Error: {error_message}")
                raise ValueError(error_message)

    @staticmethod
    def calculate_age(birth_date: Optional[date],
                      death_date: Optional[date] = None) -> Optional[
        int]:
        """
        Calculate age based on birth date and optional death date.
        """
        if not birth_date:
            return None
        end_date = death_date or date.today()
        age = end_date.year - birth_date.year - (
                    (end_date.month, end_date.day) < (
            birth_date.month, birth_date.day))
        return age
