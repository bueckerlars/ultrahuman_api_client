"""Pytest configuration and fixtures."""

from datetime import date
from typing import Any

import pytest
from pydantic import SecretStr


@pytest.fixture
def api_key() -> SecretStr:
    """Fixture providing a test API key."""
    return SecretStr("test-api-key-12345")


@pytest.fixture
def base_url() -> str:
    """Fixture providing a test base URL."""
    return "https://test-api.example.com/api/v1"


@pytest.fixture
def sample_date() -> date:
    """Fixture providing a sample date for testing."""
    return date(2024, 1, 15)


@pytest.fixture
def sample_epoch_start() -> int:
    """Fixture providing a sample start epoch timestamp."""
    return 1705276800  # 2024-01-15 00:00:00 UTC


@pytest.fixture
def sample_epoch_end() -> int:
    """Fixture providing a sample end epoch timestamp."""
    return 1705363200  # 2024-01-16 00:00:00 UTC


@pytest.fixture
def sample_api_response() -> dict[str, Any]:
    """Fixture providing a sample successful API response."""
    return {
        "status": 200,
        "error": None,
        "data": {
            "metrics": {
                "2024-01-15": [
                    {
                        "type": "hr",
                        "object": {
                            "day_start_timestamp": 1705276800,
                            "title": "Heart Rate",
                            "unit": "bpm",
                            "last_reading": 72.5,
                            "values": [
                                {"value": 70.0, "timestamp": 1705276800},
                                {"value": 72.5, "timestamp": 1705276900},
                            ],
                        },
                    },
                    {
                        "type": "steps",
                        "object": {
                            "day_start_timestamp": 1705276800,
                            "subtitle": "Steps",
                            "total": 8500.0,
                            "avg": 59.0,
                            "trend_title": "Above average",
                            "trend_direction": "positive",
                            "values": [
                                {"value": 100, "timestamp": 1705276800},
                                {"value": 200, "timestamp": 1705276900},
                            ],
                        },
                    },
                ],
            },
            "latest_time_zone": "Europe/Berlin",
        },
    }


@pytest.fixture(autouse=True)
def clear_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clear environment variables before each test."""
    monkeypatch.delenv("ULTRAHUMAN_API_KEY", raising=False)
