import logging
from datetime import date, datetime
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


class ValidationUtils:
    """
    Utility class for performing various validations.
    """

    @staticmethod
    def parse_date(date_str: Optional[str]) -> Optional[date]:
        """
        Parses a date string in the format YYYY-MM-DD.

        Args:
            date_str (Optional[str]): The date string to parse.

        Returns:
            Optional[date]: The parsed date object or None if invalid or empty.

        Raises:
            ValueError: If the date string is in an incorrect format.
        """
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(
                f"Invalid date format: {date_str}. Expected format is YYYY-MM-DD."
            )

    @staticmethod
    def validate_date_order(validations: List[
        Tuple[Optional[date], Optional[date], str]]):
        """
        Validates that the provided dates are in the correct chronological order.

        Args:
            validations (List[Tuple[Optional[date], Optional[date], str]]):
                A list of tuples containing:
                    - valid_from (Optional[date]): The start date.
                    - valid_until (Optional[date]): The end date.
                    - error_message (str): The error message to raise if validation fails.

        Raises:
            ValueError: If any date validation fails.
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
        Calculates the age based on a birth date and optional death date.

        Args:
            birth_date (Optional[date]): The birth date.
            death_date (Optional[date], optional): The death date. Defaults to None.

        Returns:
            Optional[int]: The calculated age or None if birth date is not provided.
        """
        if not birth_date:
            return None
        end_date = death_date or date.today()
        age = end_date.year - birth_date.year - (
                (end_date.month, end_date.day) < (
        birth_date.month, birth_date.day)
        )
        return age
