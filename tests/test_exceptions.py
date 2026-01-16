"""Tests for exception classes."""

from ultrahuman_api_client.exceptions import (
    UltrahumanAPIError,
    UltrahumanAPIAuthenticationError,
    UltrahumanAPIBadRequestError,
    UltrahumanAPINotFoundError,
    UltrahumanAPIInternalServerError,
)


class TestUltrahumanAPIError:
    """Tests for base UltrahumanAPIError."""

    def test_error_with_status_code(self) -> None:
        """Test error with status code includes it in string representation."""
        error = UltrahumanAPIError("Test error", status_code=400)
        assert error.message == "Test error"
        assert error.status_code == 400
        assert "[400] Test error" == str(error)

    def test_error_without_status_code(self) -> None:
        """Test error without status code."""
        error = UltrahumanAPIError("Test error", status_code=None)
        assert error.message == "Test error"
        assert error.status_code is None
        assert "Test error" == str(error)

    def test_error_inheritance(self) -> None:
        """Test that error is an Exception."""
        error = UltrahumanAPIError("Test error")
        assert isinstance(error, Exception)


class TestUltrahumanAPIAuthenticationError:
    """Tests for UltrahumanAPIAuthenticationError."""

    def test_default_message(self) -> None:
        """Test error with default message."""
        error = UltrahumanAPIAuthenticationError()
        assert error.status_code == 401
        assert "Authentication failed" in str(error)

    def test_custom_message(self) -> None:
        """Test error with custom message."""
        error = UltrahumanAPIAuthenticationError("Custom auth error")
        assert error.status_code == 401
        assert error.message == "Custom auth error"
        assert "[401] Custom auth error" == str(error)


class TestUltrahumanAPIBadRequestError:
    """Tests for UltrahumanAPIBadRequestError."""

    def test_default_message(self) -> None:
        """Test error with default message."""
        error = UltrahumanAPIBadRequestError()
        assert error.status_code == 400
        assert "Bad request" in str(error)

    def test_custom_message(self) -> None:
        """Test error with custom message."""
        error = UltrahumanAPIBadRequestError("Invalid date format")
        assert error.status_code == 400
        assert error.message == "Invalid date format"
        assert "[400] Invalid date format" == str(error)


class TestUltrahumanAPINotFoundError:
    """Tests for UltrahumanAPINotFoundError."""

    def test_default_message(self) -> None:
        """Test error with default message."""
        error = UltrahumanAPINotFoundError()
        assert error.status_code == 404
        assert "not found" in str(error).lower()

    def test_custom_message(self) -> None:
        """Test error with custom message."""
        error = UltrahumanAPINotFoundError("User not found")
        assert error.status_code == 404
        assert error.message == "User not found"
        assert "[404] User not found" == str(error)


class TestUltrahumanAPIInternalServerError:
    """Tests for UltrahumanAPIInternalServerError."""

    def test_default_message(self) -> None:
        """Test error with default message."""
        error = UltrahumanAPIInternalServerError()
        assert error.status_code == 500
        assert "Internal server error" in str(error)

    def test_custom_message(self) -> None:
        """Test error with custom message."""
        error = UltrahumanAPIInternalServerError("Server is down")
        assert error.status_code == 500
        assert error.message == "Server is down"
        assert "[500] Server is down" == str(error)
