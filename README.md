# Ultrahuman API Client

[![GitHub Issues](https://img.shields.io/github/issues/bueckerlars/ultrahuman_api_client)](https://github.com/bueckerlars/ultrahuman_api_client/issues)
[![Dependencies](https://img.shields.io/librariesio/github/bueckerlars/ultrahuman_api_client)](https://libraries.io/github/bueckerlars/ultrahuman_api_client)
[![License](https://img.shields.io/github/license/bueckerlars/ultrahuman_api_client)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)](https://www.python.org/downloads/)

A Python client library for interacting with the Ultrahuman Partner API. This client provides a simple and type-safe interface to retrieve daily health metrics from the Ultrahuman platform.

## Installation

### Prerequisites

Make sure you have Python (>=3.13) installed on your system.
The recommended way to manage dependencies is with [uv](https://github.com/astral-sh/uv), a fast Python package manager.

#### Installing `uv`

##### macOS

```bash
brew install astral-sh/uv/uv
```

##### Windows

PowerShell (recommended):

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

Or, using [scoop](https://scoop.sh):

```powershell
scoop install uv
```

##### Linux

One-line install script (most distributions):

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

Or via prebuilt binaries:

See the [uv GitHub releases](https://github.com/astral-sh/uv/releases) page.

For more information, see the [uv installation guide](https://github.com/astral-sh/uv#installation).

## Installing Dependencies

After installing `uv`, you can set up the project dependencies using the following commands:

- **For regular usage:**

  ```bash
  uv sync
  ```

  This will install all required runtime dependencies.

- **For development (includes all optional and dev dependencies, such as testing and linting tools):**

  ```bash
  uv sync --all-extras
  ```

  This ensures a complete environment for development and contribution.

> *Note:* See the [`uv` documentation](https://github.com/astral-sh/uv#uv-sync) for more details on managing dependencies.


## Quick Start

### Basic Usage

```python
from datetime import date
from ultrahuman_api_client.client import UltrahumanAPIClient

# Initialize client with API key
client = UltrahumanAPIClient(api_key="your-api-key-here")

# Get daily metrics for a specific date
data = client.get_daily_metrics(date=date(2024, 1, 15))

# Access the metrics
metrics = data.metrics
print(f"Latest timezone: {data.latest_time_zone}")
```

### Using Environment Variables

You can also set your API key via environment variable:

```bash
export ULTRAHUMAN_API_KEY="your-api-key-here"
```

Then initialize the client without providing the API key:

```python
from ultrahuman_api_client.client import UltrahumanAPIClient

client = UltrahumanAPIClient()
```

The client will automatically load the API key from the `ULTRAHUMAN_API_KEY` environment variable. If you're using a `.env` file, it will be automatically loaded.

### Using as Context Manager

The client supports the context manager protocol for automatic resource cleanup:

```python
from datetime import date
from ultrahuman_api_client.client import UltrahumanAPIClient

with UltrahumanAPIClient(api_key="your-api-key") as client:
    data = client.get_daily_metrics(date=date(2024, 1, 15))
    # Client is automatically closed when exiting the context
```

### Date Range Queries

You can also query metrics for a date range using epoch timestamps:

```python
from ultrahuman_api_client.client import UltrahumanAPIClient

client = UltrahumanAPIClient(api_key="your-api-key")

# Get metrics for a date range
response = client.get_daily_metrics(
    start_epoch=1705276800,  # 2024-01-15 00:00:00 UTC
    end_epoch=1705363200,    # 2024-01-16 00:00:00 UTC
)
```

### Querying Specific User

If you need to query metrics for a specific user, you can provide the email:

```python
from datetime import date
from ultrahuman_api_client.client import UltrahumanAPIClient

client = UltrahumanAPIClient(api_key="your-api-key")

data = client.get_daily_metrics(
    date=date(2024, 1, 15),
    email="user@example.com",
)
```

### Error Handling

The client provides specific exception classes for different error scenarios:

```python
from ultrahuman_api_client.client import UltrahumanAPIClient
from ultrahuman_api_client.exceptions import (
    UltrahumanAPIAuthenticationError,
    UltrahumanAPIBadRequestError,
    UltrahumanAPINotFoundError,
    UltrahumanAPIInternalServerError,
    UltrahumanAPIError,
)

client = UltrahumanAPIClient(api_key="your-api-key")

try:
    data = client.get_daily_metrics(date=date(2024, 1, 15))
except UltrahumanAPIAuthenticationError as e:
    print(f"Authentication failed: {e}")
except UltrahumanAPIBadRequestError as e:
    print(f"Bad request: {e}")
except UltrahumanAPINotFoundError as e:
    print(f"Not found: {e}")
except UltrahumanAPIInternalServerError as e:
    print(f"Server error: {e}")
except UltrahumanAPIError as e:
    print(f"API error [{e.status_code}]: {e}")
```

All exceptions inherit from `UltrahumanAPIError` and include:
- `message`: The error message
- `status_code`: The HTTP status code (if available)

## API Reference

### `UltrahumanAPIClient`

The main client class for interacting with the Ultrahuman API.

#### Constructor

```python
UltrahumanAPIClient(
    *,
    api_key: SecretStr | None = None,
    base_url: str | None = None,
)
```

**Parameters:**
- `api_key` (optional): The API key for authentication. If not provided, the client will try to load it from the `ULTRAHUMAN_API_KEY` environment variable.
- `base_url` (optional): The base URL for the API. Defaults to `https://partner.ultrahuman.com/api/v1`.

**Raises:**
- `ValueError`: If no API key is provided and not found in environment variables.

#### Methods

##### `get_daily_metrics`

Retrieve daily metrics for a specific date or date range.

```python
def get_daily_metrics(
    *,
    date: date | None = None,
    start_epoch: int | None = None,
    end_epoch: int | None = None,
    email: str | None = None,
) -> UltrahumanData
```

**Parameters:**
- `date` (optional): A `date` object specifying the date to retrieve metrics for.
- `start_epoch` (optional): Unix timestamp (seconds) for the start of the date range.
- `end_epoch` (optional): Unix timestamp (seconds) for the end of the date range.
- `email` (optional): Email address of the user to query metrics for.

**Returns:**
- `UltrahumanData`: A Pydantic model containing the validated metrics data with `metrics` and `latest_time_zone` fields.

**Raises:**
- `ValueError`: If neither `date` nor both `start_epoch` and `end_epoch` are provided.
- `UltrahumanAPIAuthenticationError`: If authentication fails (401).
- `UltrahumanAPIBadRequestError`: If the request is invalid, e.g., date range exceeds 7 days, missing required parameters, or invalid date format (400).
- `UltrahumanAPINotFoundError`: If the user is not found or data sharing permission is missing (404).
- `UltrahumanAPIInternalServerError`: If there's a server error on Ultrahuman's end (500).
- `UltrahumanAPIError`: For other API errors.

**Note:** Either `date` or both `start_epoch` and `end_epoch` must be provided.

##### `close`

Manually close the HTTP client and clean up resources.

```python
def close(self) -> None
```

This method is automatically called when using the client as a context manager.

## Response Models

The client uses Pydantic models to represent API responses. The `get_daily_metrics` method returns an `UltrahumanData` object directly:

- `UltrahumanData`: The main data structure returned by `get_daily_metrics`
  - `latest_time_zone`: Timezone string
  - `metrics`: Dictionary mapping date strings to lists of `MetricEntry` objects

The client automatically handles error responses and raises appropriate exceptions (see the `get_daily_metrics` method documentation above).

Each `MetricEntry` contains:
- `type`: The metric type (e.g., "hr", "steps", "sleep", "hrv", etc.)
- `metric_data`: The metric data object, validated against the appropriate model based on the type

Supported metric types include:
- `hr` (Heart Rate)
- `temp` (Temperature)
- `spo2` (Blood Oxygen)
- `hrv` (Heart Rate Variability)
- `steps` (Step Count)
- `night_rhr` (Night Resting Heart Rate)
- `sleep` (Sleep Data)
- `recovery_index`
- `movement_index`
- `active_minutes`
- `vo2_max`
- And more...

## Development

### Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/bueckerlars/ultrahuman_api_client.git
cd ultrahuman_api_client
uv sync --all-extras
pre-commit install
```

### Running Tests

Run the test suite with pytest:

```bash
pytest
```

With coverage:

```bash
pytest --cov=src --cov-report=html
```

### Code Quality

This project uses:
- **ruff** for linting and formatting
- **pyright** in strict mode for type checking
- **pre-commit** hooks for automated quality checks

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- **Repository**: [bueckerlars/ultrahuman_api_client](https://github.com/bueckerlars/ultrahuman_api_client)
- **Issues**: [Bug Tracker](https://github.com/bueckerlars/ultrahuman_api_client/issues)
- **License**: [MIT License](LICENSE)
