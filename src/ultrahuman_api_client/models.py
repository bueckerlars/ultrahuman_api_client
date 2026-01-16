from typing import List, Dict, Union, Any, Optional, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


# ============================================================================
# Basis-Modelle
# ============================================================================

class MetricValue(BaseModel):
    """Single metric value with timestamp."""
    value: float
    timestamp: int

    @field_validator('value')
    @classmethod
    def validate_value(cls, v: float) -> float:
        """Ensure value is a valid number."""
        return float(v)

    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: int) -> int:
        """Ensure timestamp is non-negative."""
        if v < 0:
            raise ValueError("Timestamp must be non-negative")
        return v


class BaseMetricObject(BaseModel):
    """Base class for standard metric objects with values, title, unit, and last reading."""
    day_start_timestamp: int
    title: str
    unit: str
    last_reading: float
    values: List[MetricValue]


class BaseMetricObjectWithTrend(BaseMetricObject):
    """Base class for metric objects with trend information."""
    avg: float
    subtitle: str
    trend_title: str
    trend_direction: Literal["positive", "negative"]


class BaseMetricObjectSteps(BaseModel):
    """Base class for steps metric (no title/unit/last_reading)."""
    day_start_timestamp: int
    values: List[MetricValue]
    subtitle: str
    total: float
    avg: float
    trend_title: str
    trend_direction: Literal["positive", "negative"]


class SimpleValueObject(BaseModel):
    """Simple metric object with just value and timestamp."""
    value: float
    day_start_timestamp: int


class IndexObject(BaseModel):
    """Base class for index metrics (recovery_index, movement_index, etc.)."""
    value: float
    title: str
    day_start_timestamp: int


# ============================================================================
# Spezifische Metrik-Objekte
# ============================================================================

class HeartRateObject(BaseMetricObject):
    """Heart Rate metric object."""
    pass


class TemperatureObject(BaseMetricObject):
    """Temperature metric object."""
    pass


class SPO2Object(BaseMetricObject):
    """SPO2 (Blood Oxygen) metric object."""
    pass


class HRVObject(BaseMetricObjectWithTrend):
    """Heart Rate Variability metric object with trend."""
    pass


class StepsObject(BaseMetricObjectSteps):
    """Steps metric object."""
    pass


class NightRHRObject(BaseMetricObjectWithTrend):
    """Night Resting Heart Rate metric object with trend."""
    pass


# ============================================================================
# Sleep-Untermodelle
# ============================================================================

class TrackingParam(BaseModel):
    """Tracking parameter for metrics."""
    key_name: str
    value: str


class QuickMetric(BaseModel):
    """Quick metric in sleep object."""
    title: str
    display_text: str
    unit: Optional[str] = None
    value: Union[int, float]
    deeplink: Optional[str] = None
    type: str
    education_modal_deeplink: Optional[str] = None
    tracking_params: Optional[List[TrackingParam]] = None
    display_text_marked_up: Optional[str] = None


class QuickMetricTiled(BaseModel):
    """Tiled quick metric in sleep object."""
    title: str
    value: str
    tag: str
    tag_color: str
    deeplink: str
    trends_unit: str
    trends_value: Union[int, float]
    type: str


class SleepStage(BaseModel):
    """Sleep stage information."""
    title: str
    type: Literal["deep_sleep", "light_sleep", "rem_sleep", "awake"]
    percentage: int
    stage_time_text: str
    stage_time: int


class SleepGraphEntry(BaseModel):
    """Entry in sleep graph."""
    start: int
    end: int
    type: Literal["awake", "light_sleep", "deep_sleep", "rem_sleep"]
    toss_turn: Optional[int] = None


class MovementGraphEntry(BaseModel):
    """Entry in movement graph."""
    timestamp: int
    type: Literal["light", "medium", "vigorous"]


class HRGraphEntry(BaseModel):
    """Entry in heart rate graph."""
    value: float
    timestamp: int


class MarkPoint(BaseModel):
    """Mark point in graph."""
    mark_type: str
    mark_color: str
    mark_point: int


class GraphData(BaseModel):
    """Graph data with marks."""
    title: str
    data: List[Union[HRGraphEntry, MovementGraphEntry]]
    marks: Optional[List[MarkPoint]] = None


class Badge(BaseModel):
    """Badge information."""
    text: str
    type: str


class SleepScore(BaseModel):
    """Sleep score."""
    score: int


class TotalSleep(BaseModel):
    """Total sleep information."""
    minutes: int
    hours: int
    remaining_minutes: int
    seconds: int
    badge: Badge


class SleepEfficiency(BaseModel):
    """Sleep efficiency information."""
    percentage: int
    contributor: int


class TimeInBed(BaseModel):
    """Time in bed information."""
    minutes: int
    hours: int
    remaining_minutes: int
    badge: Badge


class REMSleep(BaseModel):
    """REM sleep information."""
    minutes: int
    seconds: int
    percentage: float
    hours: int
    remaining_minutes: int
    contributor: float


class DeepSleep(BaseModel):
    """Deep sleep information."""
    minutes: int
    seconds: int
    hours: int
    remaining_minutes: int
    contributor: float


class LightSleep(BaseModel):
    """Light sleep information."""
    minutes: int
    seconds: int
    percentage: int
    hours: int
    remaining_minutes: int


class TemperatureDeviation(BaseModel):
    """Temperature deviation information."""
    celsius: float
    contributor: int


class RestorativeSleep(BaseModel):
    """Restorative sleep information."""
    percentage: int
    badge: Badge


class Movements(BaseModel):
    """Movements information."""
    count: int


class MorningAlertness(BaseModel):
    """Morning alertness information."""
    minutes: int


class FullSleepCycles(BaseModel):
    """Full sleep cycles information."""
    cycles: int


class TossesAndTurns(BaseModel):
    """Tosses and turns information."""
    count: int


class AverageBodyTemperature(BaseModel):
    """Average body temperature information."""
    celsius: float
    contributor: int


class SleepGraph(BaseModel):
    """Sleep graph structure."""
    title: str
    data: List[SleepGraphEntry]
    education_modal_deeplink: Optional[str] = None


class MovementGraph(BaseModel):
    """Movement graph structure."""
    title: str
    data: List[MovementGraphEntry]


class HRGraph(BaseModel):
    """Heart rate graph structure."""
    title: str
    data: List[HRGraphEntry]
    marks: Optional[List[MarkPoint]] = None


class SleepHRDrop(BaseModel):
    """Sleep HR drop information."""
    timestamp: Optional[int] = None
    value: Optional[float] = None


# ============================================================================
# Sleep-Objekt (komplex)
# ============================================================================

class SleepObject(BaseModel):
    """Complex sleep metric object."""
    bedtime_start: int
    bedtime_end: int
    quick_metrics: List[QuickMetric]
    quick_metrics_tiled: List[QuickMetricTiled]
    sleep_stages: List[SleepStage]
    sleep_graph: SleepGraph
    movement_graph: MovementGraph
    hr_graph: HRGraph
    sleep_score: SleepScore
    total_sleep: TotalSleep
    sleep_efficiency: SleepEfficiency
    time_in_bed: TimeInBed
    rem_sleep: REMSleep
    deep_sleep: DeepSleep
    light_sleep: LightSleep
    temperature_deviation: TemperatureDeviation
    hr_drop: Optional[SleepHRDrop] = None
    restorative_sleep: RestorativeSleep
    movements: Movements
    morning_alertness: MorningAlertness
    full_sleep_cycles: FullSleepCycles
    tosses_and_turns: TossesAndTurns
    average_body_temperature: AverageBodyTemperature


# ============================================================================
# Union aller möglichen Metrik-Objekte
# ============================================================================

MetricObject = Union[
    HeartRateObject,
    TemperatureObject,
    SPO2Object,
    HRVObject,
    StepsObject,
    NightRHRObject,
    SimpleValueObject,  # für avg_sleep_hrv, sleep_rhr
    IndexObject,  # für recovery_index, movement_index, active_minutes, vo2_max
    SleepObject,
]


# ============================================================================
# MetricEntry mit Custom Validator
# ============================================================================

class MetricEntry(BaseModel):
    """Metric entry with type and object, using discriminated union based on type."""
    type: str
    metric_data: Any = Field(..., alias="object")

    @model_validator(mode='after')
    def validate_metric_data(self) -> "MetricEntry":
        """Validate and parse object based on type field."""
        # Map type to appropriate model
        type_mapping: Dict[str, type[BaseModel]] = {
            'hr': HeartRateObject,
            'temp': TemperatureObject,
            'spo2': SPO2Object,
            'hrv': HRVObject,
            'steps': StepsObject,
            'night_rhr': NightRHRObject,
            'avg_sleep_hrv': SimpleValueObject,
            'sleep_rhr': SimpleValueObject,
            'recovery_index': IndexObject,
            'movement_index': IndexObject,
            'active_minutes': IndexObject,
            'vo2_max': IndexObject,
            'sleep': SleepObject,
        }
        
        model_class = type_mapping.get(self.type)
        if model_class and self.metric_data is not None:
            # Validate the object data with the appropriate model
            try:
                if not isinstance(self.metric_data, model_class):
                    validated_object: BaseModel = model_class.model_validate(self.metric_data)
                    self.metric_data = validated_object
            except Exception:
                # If validation fails, keep original data
                # This allows for graceful degradation
                pass
        
        return self


# ============================================================================
# Response-Modelle
# ============================================================================

class UltrahumanData(BaseModel):
    """Ultrahuman API data structure."""
    metrics: Dict[str, List[MetricEntry]]
    latest_time_zone: str


class UltrahumanResponse(BaseModel):
    """Ultrahuman API response structure."""
    status: int
    error: Optional[str] = None
    data: UltrahumanData

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: int) -> int:
        """Validate status code."""
        if v < 100 or v > 599:
            raise ValueError("Status must be a valid HTTP status code")
        return v

    @classmethod
    def from_json(cls, json_data: Union[str, Dict[str, Any]]) -> "UltrahumanResponse":
        """
        Parse JSON data into UltrahumanResponse model.
        
        Args:
            json_data: JSON string or dictionary containing the API response
            
        Returns:
            UltrahumanResponse instance
            
        Raises:
            ValueError: If JSON data is invalid or cannot be parsed
        """
        import json
        
        # If json_data is a string, parse it first
        if isinstance(json_data, str):
            try:
                json_data = json.loads(json_data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON string: {e}")
        
        # Validate and parse using Pydantic
        try:
            return cls.model_validate(json_data)
        except Exception as e:
            raise ValueError(f"Failed to parse UltrahumanResponse: {e}")
