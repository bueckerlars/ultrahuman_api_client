"""Exceptions for the Ultrahuman API Client."""


class UltrahumanAPIError(Exception):
    """Base exception for the Ultrahuman API Client."""

    def __init__(self, message: str, status_code: int | None = None):
        """
        Initialize the Ultrahuman API Error.

        :param message: The error message.
        :param status_code: The HTTP status code (if available).
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.status_code is not None:
            return f"[{self.status_code}] {self.message}"
        return self.message


class UltrahumanAPIAuthenticationError(UltrahumanAPIError):
    """Exception for authentication errors (401)."""

    def __init__(
        self, message: str = "Authentication failed. Please check your API key."
    ):
        super().__init__(message, status_code=401)


class UltrahumanAPIBadRequestError(UltrahumanAPIError):
    """Exception for bad request errors (400).

    This can occur when:
    - Date range exceeds 7 days
    - Missing required parameters
    - Invalid date format
    """

    def __init__(self, message: str = "Bad request. Please check your parameters."):
        super().__init__(message, status_code=400)


class UltrahumanAPINotFoundError(UltrahumanAPIError):
    """Exception for not found errors (404).

    This can occur when:
    - User not found
    - No data sharing permission
    """

    def __init__(
        self,
        message: str = "Resource not found. User may not exist or data sharing permission may be missing.",
    ):
        super().__init__(message, status_code=404)


class UltrahumanAPIInternalServerError(UltrahumanAPIError):
    """Exception for internal server errors (500).

    Something went wrong on Ultrahuman's end. (These are rare.)
    """

    def __init__(
        self,
        message: str = "Internal server error. Something went wrong on Ultrahuman's end.",
    ):
        super().__init__(message, status_code=500)
