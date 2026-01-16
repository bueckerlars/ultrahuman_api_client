"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from ultrahuman_api_client.models import (
    MetricValue,
    HeartRateObject,
    HRVObject,
    StepsObject,
    SimpleValueObject,
    IndexObject,
    MetricEntry,
    UltrahumanData,
    UltrahumanResponse,
)


class TestMetricValue:
    """Tests for MetricValue model."""

    def test_valid_metric_value(self) -> None:
        """Test creating a valid MetricValue."""
        metric = MetricValue(value=72.5, timestamp=1705276800)
        assert metric.value == 72.5
        assert metric.timestamp == 1705276800

    def test_negative_timestamp_raises_error(self) -> None:
        """Test that negative timestamp raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            MetricValue(value=72.5, timestamp=-1)
        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("timestamp",)
            and "non-negative" in str(error["msg"]).lower()
            for error in errors
        )

    def test_value_conversion_to_float(self) -> None:
        """Test that value is converted to float."""
        metric = MetricValue(value=72, timestamp=1705276800)
        assert isinstance(metric.value, float)
        assert metric.value == 72.0


class TestBaseMetricObject:
    """Tests for BaseMetricObject and derived classes."""

    def test_valid_heart_rate_object(self) -> None:
        """Test creating a valid HeartRateObject."""
        hr_data = {
            "day_start_timestamp": 1705276800,
            "title": "Heart Rate",
            "unit": "bpm",
            "last_reading": 72.5,
            "values": [
                {"value": 70.0, "timestamp": 1705276800},
                {"value": 72.5, "timestamp": 1705276900},
            ],
        }
        hr = HeartRateObject.model_validate(hr_data)
        assert hr.title == "Heart Rate"
        assert hr.unit == "bpm"
        assert hr.last_reading == 72.5
        assert len(hr.values) == 2

    def test_valid_hrv_object_with_trend(self) -> None:
        """Test creating a valid HRVObject with trend."""
        hrv_data = {
            "day_start_timestamp": 1705276800,
            "title": "HRV",
            "unit": "ms",
            "last_reading": 45.0,
            "values": [
                {"value": 44.0, "timestamp": 1705276800},
                {"value": 45.0, "timestamp": 1705276900},
            ],
            "avg": 44.5,
            "subtitle": "Heart Rate Variability",
            "trend_title": "Above average",
            "trend_direction": "positive",
        }
        hrv = HRVObject.model_validate(hrv_data)
        assert hrv.avg == 44.5
        assert hrv.trend_direction == "positive"
        assert hrv.trend_title == "Above average"

    def test_invalid_trend_direction_raises_error(self) -> None:
        """Test that invalid trend_direction raises ValidationError."""
        hrv_data = {
            "day_start_timestamp": 1705276800,
            "title": "HRV",
            "unit": "ms",
            "last_reading": 45.0,
            "values": [],
            "avg": 44.5,
            "subtitle": "Heart Rate Variability",
            "trend_title": "Above average",
            "trend_direction": "invalid",
        }
        with pytest.raises(ValidationError):
            HRVObject.model_validate(hrv_data)

    def test_valid_steps_object(self) -> None:
        """Test creating a valid StepsObject."""
        steps_data = {
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
        }
        steps = StepsObject.model_validate(steps_data)
        assert steps.total == 8500.0
        assert steps.avg == 59.0
        assert steps.trend_direction == "positive"


class TestSimpleValueObject:
    """Tests for SimpleValueObject."""

    def test_valid_simple_value_object(self) -> None:
        """Test creating a valid SimpleValueObject."""
        obj = SimpleValueObject(value=45.0, day_start_timestamp=1705276800)
        assert obj.value == 45.0
        assert obj.day_start_timestamp == 1705276800


class TestIndexObject:
    """Tests for IndexObject."""

    def test_valid_index_object(self) -> None:
        """Test creating a valid IndexObject."""
        obj = IndexObject(
            value=85.0, title="Recovery Index", day_start_timestamp=1705276800
        )
        assert obj.value == 85.0
        assert obj.title == "Recovery Index"


class TestMetricEntry:
    """Tests for MetricEntry with custom validator."""

    def test_metric_entry_with_hr_type(self) -> None:
        """Test MetricEntry with hr type validates correctly."""
        entry_data = {
            "type": "hr",
            "object": {
                "day_start_timestamp": 1705276800,
                "title": "Heart Rate",
                "unit": "bpm",
                "last_reading": 72.5,
                "values": [
                    {"value": 70.0, "timestamp": 1705276800},
                ],
            },
        }
        entry = MetricEntry.model_validate(entry_data)
        assert entry.type == "hr"
        assert isinstance(entry.metric_data, HeartRateObject)
        assert entry.metric_data.title == "Heart Rate"

    def test_metric_entry_with_steps_type(self) -> None:
        """Test MetricEntry with steps type validates correctly."""
        entry_data = {
            "type": "steps",
            "object": {
                "day_start_timestamp": 1705276800,
                "subtitle": "Steps",
                "total": 8500.0,
                "avg": 59.0,
                "trend_title": "Above average",
                "trend_direction": "positive",
                "values": [],
            },
        }
        entry = MetricEntry.model_validate(entry_data)
        assert entry.type == "steps"
        assert isinstance(entry.metric_data, StepsObject)
        assert entry.metric_data.total == 8500.0

    def test_metric_entry_with_recovery_index_type(self) -> None:
        """Test MetricEntry with recovery_index type validates correctly."""
        entry_data = {
            "type": "recovery_index",
            "object": {
                "value": 85.0,
                "title": "Recovery Index",
                "day_start_timestamp": 1705276800,
            },
        }
        entry = MetricEntry.model_validate(entry_data)
        assert entry.type == "recovery_index"
        assert isinstance(entry.metric_data, IndexObject)
        assert entry.metric_data.value == 85.0

    def test_metric_entry_with_unknown_type(self) -> None:
        """Test MetricEntry with unknown type still works (graceful degradation)."""
        entry_data = {
            "type": "unknown_type",
            "object": {"some": "data"},
        }
        # Should not raise error, but keep original data
        entry = MetricEntry.model_validate(entry_data)
        assert entry.type == "unknown_type"
        # metric_data should remain as dict since validation fails
        assert isinstance(entry.metric_data, dict)


class TestUltrahumanResponse:
    """Tests for UltrahumanResponse model."""

    def test_valid_response(self) -> None:
        """Test creating a valid UltrahumanResponse."""
        response_data = {
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
                                "values": [],
                            },
                        },
                    ],
                },
                "latest_time_zone": "Europe/Berlin",
            },
        }
        response = UltrahumanResponse.model_validate(response_data)
        assert response.status == 200
        assert response.error is None
        assert response.data.latest_time_zone == "Europe/Berlin"

    def test_invalid_status_code_raises_error(self) -> None:
        """Test that invalid status code raises ValidationError."""
        response_data = {
            "status": 999,
            "error": None,
            "data": {
                "metrics": {},
                "latest_time_zone": "UTC",
            },
        }
        with pytest.raises(ValidationError) as exc_info:
            UltrahumanResponse.model_validate(response_data)
        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("status",) and "status code" in str(error["msg"]).lower()
            for error in errors
        )

    def test_from_json_with_dict(self) -> None:
        """Test from_json method with dictionary input."""
        json_data = {
            "status": 200,
            "error": None,
            "data": {
                "metrics": {},
                "latest_time_zone": "UTC",
            },
        }
        response = UltrahumanResponse.from_json(json_data)
        assert response.status == 200
        assert response.data.latest_time_zone == "UTC"

    def test_from_json_with_string(self) -> None:
        """Test from_json method with JSON string input."""
        json_str = '{"status": 200, "error": null, "data": {"metrics": {}, "latest_time_zone": "UTC"}}'
        response = UltrahumanResponse.from_json(json_str)
        assert response.status == 200
        assert response.data.latest_time_zone == "UTC"

    def test_from_json_with_invalid_json_raises_error(self) -> None:
        """Test that from_json raises ValueError for invalid JSON."""
        with pytest.raises(ValueError, match="Invalid JSON"):
            UltrahumanResponse.from_json("invalid json")


class TestUltrahumanData:
    """Tests for UltrahumanData model."""

    def test_valid_data(self) -> None:
        """Test creating valid UltrahumanData."""
        data = {
            "metrics": {
                "2024-01-15": [
                    {
                        "type": "hr",
                        "object": {
                            "day_start_timestamp": 1705276800,
                            "title": "Heart Rate",
                            "unit": "bpm",
                            "last_reading": 72.5,
                            "values": [],
                        },
                    },
                ],
            },
            "latest_time_zone": "Europe/Berlin",
        }
        ultrahuman_data = UltrahumanData.model_validate(data)
        assert ultrahuman_data.latest_time_zone == "Europe/Berlin"
        assert "2024-01-15" in ultrahuman_data.metrics
        assert len(ultrahuman_data.metrics["2024-01-15"]) == 1
