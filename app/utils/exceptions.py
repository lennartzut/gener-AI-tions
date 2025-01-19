class UserAlreadyExistsError(Exception):
    """
    Exception raised when attempting to create or update a user that
    already exists.

    Attributes:
        message (str): Explanation of the error.
        field (str): The field that caused the error (e.g.,
        'email' or 'username').
    """

    def __init__(self, message: str, field: str):
        super().__init__(message)
        self.message = message
        self.field = field