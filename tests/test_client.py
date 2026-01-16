"""Tests for the UltrahumanAPIClient."""

from datetime import date
from typing import Any
from unittest.mock import patch

import pytest
from pydantic import SecretStr
import httpx

from ultrahuman_api_client.client import UltrahumanAPIClient
from ultrahuman_api_client.exceptions import (
    UltrahumanAPIAuthenticationError,
    UltrahumanAPIBadRequestError,
    UltrahumanAPINotFoundError,
    UltrahumanAPIInternalServerError,
    UltrahumanAPIError,
)


class TestClientInitialization:
    """Tests for client initialization."""

    def test_init_with_api_key(self, api_key: SecretStr, base_url: str) -> None:
        """Test client initialization with explicit API key."""
        client = UltrahumanAPIClient(api_key=api_key, base_url=base_url)
        assert client._api_key == api_key
        assert client._base_url == base_url
        client.close()

    def test_init_without_api_key_raises_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that initialization without API key raises ValueError."""
        monkeypatch.delenv("ULTRAHUMAN_API_KEY", raising=False)
        # Mock load_dotenv to prevent loading .env file
        with patch("ultrahuman_api_client.client.load_dotenv"):
            with pytest.raises(ValueError, match="API key is not provided"):
                UltrahumanAPIClient()

    def test_init_with_env_api_key(
        self, monkeypatch: pytest.MonkeyPatch, base_url: str
    ) -> None:
        """Test client initialization with API key from environment."""
        monkeypatch.setenv("ULTRAHUMAN_API_KEY", "env-api-key-123")
        client = UltrahumanAPIClient(base_url=base_url)
        assert client._api_key.get_secret_value() == "env-api-key-123"
        client.close()

    def test_init_with_default_base_url(self, api_key: SecretStr) -> None:
        """Test client initialization with default base URL."""
        client = UltrahumanAPIClient(api_key=api_key)
        assert client._base_url == "https://partner.ultrahuman.com/api/v1"
        client.close()

    def test_client_headers_contain_api_key(
        self, api_key: SecretStr, base_url: str
    ) -> None:
        """Test that client headers contain the API key."""
        client = UltrahumanAPIClient(api_key=api_key, base_url=base_url)
        assert "Authorization" in client._client.headers
        assert client._client.headers["Authorization"] == api_key.get_secret_value()
        client.close()


class TestContextManager:
    """Tests for context manager functionality."""

    def test_context_manager_enters(self, api_key: SecretStr, base_url: str) -> None:
        """Test that client can be used as context manager."""
        with UltrahumanAPIClient(api_key=api_key, base_url=base_url) as client:
            assert isinstance(client, UltrahumanAPIClient)
            # Client should still be open inside context
            assert not client._client.is_closed

    def test_context_manager_closes_client(
        self, api_key: SecretStr, base_url: str
    ) -> None:
        """Test that client is closed when exiting context manager."""
        with UltrahumanAPIClient(api_key=api_key, base_url=base_url) as client:
            pass
        # Client should be closed after exiting context
        assert client._client.is_closed

    def test_manual_close(self, api_key: SecretStr, base_url: str) -> None:
        """Test manual client closing."""
        client = UltrahumanAPIClient(api_key=api_key, base_url=base_url)
        assert not client._client.is_closed
        client.close()
        assert client._client.is_closed


class TestGetDailyMetrics:
    """Tests for get_daily_metrics method."""

    def test_get_daily_metrics_with_date(
        self,
        api_key: SecretStr,
        base_url: str,
        sample_date: date,
        sample_api_response: dict,
        httpx_mock: Any,
    ) -> None:
        """Test getting daily metrics with date parameter."""
        httpx_mock.add_response(
            url=f"{base_url}/partner/daily_metrics",
            method="GET",
            json=sample_api_response,
            match_params={"date": "2024-01-15"},
        )

        client = UltrahumanAPIClient(api_key=api_key, base_url=base_url)
        result = client.get_daily_metrics(date=sample_date)
        client.close()

        assert result.latest_time_zone == "Europe/Berlin"
        assert "2024-01-15" in result.metrics
        assert len(result.metrics["2024-01-15"]) == 2

    def test_get_daily_metrics_with_epoch_range(
        self,
        api_key: SecretStr,
        base_url: str,
        sample_epoch_start: int,
        sample_epoch_end: int,
        sample_api_response: dict,
        httpx_mock: Any,
    ) -> None:
        """Test getting daily metrics with epoch range."""
        httpx_mock.add_response(
            url=f"{base_url}/partner/daily_metrics",
            method="GET",
            json=sample_api_response,
            match_params={
                "start_epoch": "1705276800",
                "end_epoch": "1705363200",
            },
        )

        client = UltrahumanAPIClient(api_key=api_key, base_url=base_url)
        result = client.get_daily_metrics(
            start_epoch=sample_epoch_start, end_epoch=sample_epoch_end
        )
        client.close()

        assert result.latest_time_zone == "Europe/Berlin"

    def test_get_daily_metrics_with_email(
        self,
        api_key: SecretStr,
        base_url: str,
        sample_date: date,
        sample_api_response: dict,
        httpx_mock: Any,
    ) -> None:
        """Test getting daily metrics with email parameter."""
        httpx_mock.add_response(
            url=f"{base_url}/partner/daily_metrics",
            method="GET",
            json=sample_api_response,
            match_params={"date": "2024-01-15", "email": "user@example.com"},
        )

        client = UltrahumanAPIClient(api_key=api_key, base_url=base_url)
        result = client.get_daily_metrics(date=sample_date, email="user@example.com")
        client.close()

        assert result.latest_time_zone == "Europe/Berlin"

    def test_get_daily_metrics_missing_params_raises_error(
        self, api_key: SecretStr, base_url: str
    ) -> None:
        """Test that missing date/epoch parameters raise ValueError."""
        client = UltrahumanAPIClient(api_key=api_key, base_url=base_url)
        with pytest.raises(
            ValueError,
            match="Either 'date' or both 'start_epoch' and 'end_epoch' must be provided",
        ):
            client.get_daily_metrics()
        client.close()

    def test_get_daily_metrics_only_start_epoch_raises_error(
        self, api_key: SecretStr, base_url: str, sample_epoch_start: int
    ) -> None:
        """Test that providing only start_epoch raises ValueError."""
        client = UltrahumanAPIClient(api_key=api_key, base_url=base_url)
        with pytest.raises(
            ValueError,
            match="Either 'date' or both 'start_epoch' and 'end_epoch' must be provided",
        ):
            client.get_daily_metrics(start_epoch=sample_epoch_start)
        client.close()

    def test_get_daily_metrics_only_end_epoch_raises_error(
        self, api_key: SecretStr, base_url: str, sample_epoch_end: int
    ) -> None:
        """Test that providing only end_epoch raises ValueError."""
        client = UltrahumanAPIClient(api_key=api_key, base_url=base_url)
        with pytest.raises(
            ValueError,
            match="Either 'date' or both 'start_epoch' and 'end_epoch' must be provided",
        ):
            client.get_daily_metrics(end_epoch=sample_epoch_end)
        client.close()


class TestErrorHandling:
    """Tests for error handling."""

    def test_authentication_error(
        self,
        api_key: SecretStr,
        base_url: str,
        sample_date: date,
        httpx_mock: Any,
    ) -> None:
        """Test handling of 401 authentication error."""
        httpx_mock.add_response(
            url=f"{base_url}/partner/daily_metrics",
            method="GET",
            status_code=401,
            json={"error": "Invalid API key"},
            match_params={"date": "2024-01-15"},
        )

        client = UltrahumanAPIClient(api_key=api_key, base_url=base_url)
        with pytest.raises(UltrahumanAPIAuthenticationError) as exc_info:
            client.get_daily_metrics(date=sample_date)
        assert exc_info.value.status_code == 401
        assert "Invalid API key" in str(exc_info.value)
        client.close()

    def test_bad_request_error(
        self,
        api_key: SecretStr,
        base_url: str,
        sample_date: date,
        httpx_mock: Any,
    ) -> None:
        """Test handling of 400 bad request error."""
        httpx_mock.add_response(
            url=f"{base_url}/partner/daily_metrics",
            method="GET",
            status_code=400,
            json={"error": "Date range exceeds 7 days"},
            match_params={"date": "2024-01-15"},
        )

        client = UltrahumanAPIClient(api_key=api_key, base_url=base_url)
        with pytest.raises(UltrahumanAPIBadRequestError) as exc_info:
            client.get_daily_metrics(date=sample_date)
        assert exc_info.value.status_code == 400
        assert "Date range exceeds 7 days" in str(exc_info.value)
        client.close()

    def test_not_found_error(
        self,
        api_key: SecretStr,
        base_url: str,
        sample_date: date,
        httpx_mock: Any,
    ) -> None:
        """Test handling of 404 not found error."""
        httpx_mock.add_response(
            url=f"{base_url}/partner/daily_metrics",
            method="GET",
            status_code=404,
            json={"error": "User not found"},
            match_params={"date": "2024-01-15"},
        )

        client = UltrahumanAPIClient(api_key=api_key, base_url=base_url)
        with pytest.raises(UltrahumanAPINotFoundError) as exc_info:
            client.get_daily_metrics(date=sample_date)
        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value)
        client.close()

    def test_internal_server_error(
        self,
        api_key: SecretStr,
        base_url: str,
        sample_date: date,
        httpx_mock: Any,
    ) -> None:
        """Test handling of 500 internal server error."""
        httpx_mock.add_response(
            url=f"{base_url}/partner/daily_metrics",
            method="GET",
            status_code=500,
            json={"error": "Internal server error"},
            match_params={"date": "2024-01-15"},
        )

        client = UltrahumanAPIClient(api_key=api_key, base_url=base_url)
        with pytest.raises(UltrahumanAPIInternalServerError) as exc_info:
            client.get_daily_metrics(date=sample_date)
        assert exc_info.value.status_code == 500
        assert "Internal server error" in str(exc_info.value)
        client.close()

    def test_other_status_code_error(
        self,
        api_key: SecretStr,
        base_url: str,
        sample_date: date,
        httpx_mock: Any,
    ) -> None:
        """Test handling of other status codes."""
        httpx_mock.add_response(
            url=f"{base_url}/partner/daily_metrics",
            method="GET",
            status_code=503,
            json={"error": "Service unavailable"},
            match_params={"date": "2024-01-15"},
        )

        client = UltrahumanAPIClient(api_key=api_key, base_url=base_url)
        with pytest.raises(UltrahumanAPIError) as exc_info:
            client.get_daily_metrics(date=sample_date)
        assert exc_info.value.status_code == 503
        assert "Service unavailable" in str(exc_info.value)
        client.close()

    def test_error_with_message_field(
        self,
        api_key: SecretStr,
        base_url: str,
        sample_date: date,
        httpx_mock: Any,
    ) -> None:
        """Test error extraction from 'message' field when 'error' is not available."""
        httpx_mock.add_response(
            url=f"{base_url}/partner/daily_metrics",
            method="GET",
            status_code=400,
            json={"message": "Invalid date format"},
            match_params={"date": "2024-01-15"},
        )

        client = UltrahumanAPIClient(api_key=api_key, base_url=base_url)
        with pytest.raises(UltrahumanAPIBadRequestError) as exc_info:
            client.get_daily_metrics(date=sample_date)
        assert "Invalid date format" in str(exc_info.value)
        client.close()

    def test_error_with_non_json_response(
        self,
        api_key: SecretStr,
        base_url: str,
        sample_date: date,
        httpx_mock: Any,
    ) -> None:
        """Test error handling with non-JSON error response."""
        httpx_mock.add_response(
            url=f"{base_url}/partner/daily_metrics",
            method="GET",
            status_code=500,
            text="Internal Server Error",
            match_params={"date": "2024-01-15"},
        )

        client = UltrahumanAPIClient(api_key=api_key, base_url=base_url)
        with pytest.raises(UltrahumanAPIInternalServerError) as exc_info:
            client.get_daily_metrics(date=sample_date)
        assert "Internal Server Error" in str(exc_info.value)
        client.close()

    def test_network_error(
        self,
        api_key: SecretStr,
        base_url: str,
        sample_date: date,
        httpx_mock: Any,
    ) -> None:
        """Test handling of network errors."""
        httpx_mock.add_exception(
            httpx.ConnectError("Connection failed"),
            url=f"{base_url}/partner/daily_metrics",
            method="GET",
            match_params={"date": "2024-01-15"},
        )

        client = UltrahumanAPIClient(api_key=api_key, base_url=base_url)
        with pytest.raises(UltrahumanAPIError) as exc_info:
            client.get_daily_metrics(date=sample_date)
        assert exc_info.value.status_code is None
        assert "Request failed" in str(exc_info.value)
        client.close()

    def test_error_in_response_body(
        self,
        api_key: SecretStr,
        base_url: str,
        sample_date: date,
        httpx_mock: Any,
    ) -> None:
        """Test handling of error field in response body even with 200 status."""
        response_data = {
            "status": 401,
            "error": "Authentication failed",
            "data": {
                "metrics": {},
                "latest_time_zone": "UTC",
            },
        }
        httpx_mock.add_response(
            url=f"{base_url}/partner/daily_metrics",
            method="GET",
            status_code=200,
            json=response_data,
            match_params={"date": "2024-01-15"},
        )

        client = UltrahumanAPIClient(api_key=api_key, base_url=base_url)
        with pytest.raises(UltrahumanAPIAuthenticationError) as exc_info:
            client.get_daily_metrics(date=sample_date)
        assert exc_info.value.status_code == 401
        assert "Authentication failed" in str(exc_info.value)
        client.close()

    def test_invalid_json_response(
        self,
        api_key: SecretStr,
        base_url: str,
        sample_date: date,
        httpx_mock: Any,
    ) -> None:
        """Test handling of invalid JSON in successful response."""
        httpx_mock.add_response(
            url=f"{base_url}/partner/daily_metrics",
            method="GET",
            status_code=200,
            text="Invalid JSON response",
            match_params={"date": "2024-01-15"},
        )

        client = UltrahumanAPIClient(api_key=api_key, base_url=base_url)
        with pytest.raises(UltrahumanAPIError) as exc_info:
            client.get_daily_metrics(date=sample_date)
        assert "Failed to parse response" in str(exc_info.value)
        client.close()
