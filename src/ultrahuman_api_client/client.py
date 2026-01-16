from datetime import date
from dotenv import load_dotenv
from pydantic import SecretStr
from types import TracebackType
from typing import Final, overload, Any, cast
import os

import httpx
from loguru import logger

from ultrahuman_api_client.models import UltrahumanData, UltrahumanResponse
from ultrahuman_api_client.exceptions import (
    UltrahumanAPIError,
    UltrahumanAPIAuthenticationError,
    UltrahumanAPIBadRequestError,
    UltrahumanAPINotFoundError,
    UltrahumanAPIInternalServerError,
)


class UltrahumanAPIClient():

    _BASE_URL: Final[str] = "https://partner.ultrahuman.com/api/v1"

    def __init__(
        self,
        *,
        api_key: SecretStr | None = None,
        base_url: str | None = None,
    ) -> None:
        """
        Initialize the Ultrahuman API Client.

        The base URL is set to the default value of https://api.ultrahuman.com/api/v1/. 
        If a different base URL is provided, it will be used instead.
        If no API key is provided, the API key will be fetched from the environment variable ULTRAHUMAN_API_KEY. 
        If no API key is found in the environment variables, a ValueError will be raised.

        :param api_key: The API key for the Ultrahuman API.
        :param base_url: The base URL for the Ultrahuman API.
        :raises ValueError: If no API key is provided and not found in environment variables.
        """

        logger.debug(f"Initializing Ultrahuman API Client with API key: {api_key} and base URL: {base_url}")
        
        if api_key is None:
            load_dotenv()
            env_api_key = os.getenv("ULTRAHUMAN_API_KEY")
            if env_api_key is not None:
                api_key = SecretStr(env_api_key)
        if api_key is None:
            raise ValueError("API key is not provided and not found in environment variables")
        self._api_key = api_key


        if base_url is None:
            base_url = self._BASE_URL
        self._base_url = base_url

        # Create httpx client with configured headers
        headers = {
            "Authorization": f"{self._api_key.get_secret_value()}",
        }
        self._client = httpx.Client(base_url=base_url, headers=headers)

    def close(self) -> None:
        """
        Close the httpx client.
        
        This method should be called when the client is no longer needed
        to properly clean up resources.
        """
        self._client.close()

    def __enter__(self) -> "UltrahumanAPIClient":
        """
        Enter the context manager.
        
        :return: The client instance.
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Exit the context manager and close the httpx client.
        
        :param exc_type: Exception type.
        :param exc_val: Exception value.
        :param exc_tb: Exception traceback.
        """
        self.close()

    @overload
    def get_daily_metrics(
        self,
        *,
        date: date,
        email: str | None = None,
    ) -> UltrahumanData:
        """
        Get the daily metrics for a given date.

        :param date: The date to get the daily metrics for.
        :param email: The email of the user to get the daily metrics for.
        :return: The daily metrics for the given date.
        """
        ...

    @overload
    def get_daily_metrics(
        self,
        *,
        start_epoch: int,
        end_epoch: int,
        email: str | None = None,
    ) -> UltrahumanData:
        """
        Get the daily metrics for a given date range.

        :param start_epoch: The start of the date range.
        :param end_epoch: The end of the date range.
        :param email: The email of the user to get the daily metrics for.
        :return: The daily metrics for the given date range.
        """
        ...

    def get_daily_metrics(
        self,
        *,
        date: date | None = None,
        start_epoch: int | None = None,
        end_epoch: int | None = None,
        email: str | None = None,
    ) -> UltrahumanData:
        """
        Get the daily metrics for a given date or date range.

        Either `date` or both `start_epoch` and `end_epoch` must be provided.

        :param date: The date to get the daily metrics for.
        :param start_epoch: The start of the date range.
        :param end_epoch: The end of the date range.
        :param email: The email of the user to get the daily metrics for.
        :return: The daily metrics data for the given date or date range.
        :raises ValueError: If neither date nor both epoch parameters are provided.
        :raises UltrahumanAPIAuthenticationError: If authentication fails (401).
        :raises UltrahumanAPIBadRequestError: If the request is invalid (400).
        :raises UltrahumanAPINotFoundError: If the resource is not found (404).
        :raises UltrahumanAPIInternalServerError: If there's a server error (500).
        :raises UltrahumanAPIError: For other API errors.
        """
        url = "partner/daily_metrics"
        
        params: dict[str, str] = {}
        
        if date is not None:
            params["date"] = date.isoformat()
        elif start_epoch is not None and end_epoch is not None:
            params["start_epoch"] = str(start_epoch)
            params["end_epoch"] = str(end_epoch)
        else:
            raise ValueError("Either 'date' or both 'start_epoch' and 'end_epoch' must be provided")
        
        if email is not None:
            params["email"] = email
        
        logger.debug(f"Making request to {self._base_url}{url} with params {params}")
        
        try:
            response = self._client.get(url, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            error_message: str = "Unknown error"
            
            # Try to extract error message from response
            try:
                response_data = e.response.json()
                if isinstance(response_data, dict):
                    response_dict = cast(dict[str, Any], response_data)
                    error_msg = response_dict.get("error")
                    if isinstance(error_msg, str):
                        error_message = error_msg
                    else:
                        msg = response_dict.get("message")
                        if isinstance(msg, str):
                            error_message = msg
                        else:
                            error_message = str(e)
                else:
                    error_message = str(e)
            except Exception:
                error_message = e.response.text or str(e)
            
            # Raise appropriate exception based on status code
            if status_code == 401:
                raise UltrahumanAPIAuthenticationError(error_message)
            elif status_code == 400:
                raise UltrahumanAPIBadRequestError(error_message)
            elif status_code == 404:
                raise UltrahumanAPINotFoundError(error_message)
            elif status_code == 500:
                raise UltrahumanAPIInternalServerError(error_message)
            else:
                raise UltrahumanAPIError(error_message, status_code=status_code)
        except httpx.RequestError as e:
            # Handle network errors
            raise UltrahumanAPIError(f"Request failed: {str(e)}", status_code=None)
        
        # Parse response
        try:
            response_data = response.json()
            ultrahuman_response = UltrahumanResponse.model_validate(response_data)
            
            # Check if response has an error field
            if ultrahuman_response.error:
                # If there's an error in the response body, raise appropriate exception
                status_code = ultrahuman_response.status
                if status_code == 401:
                    raise UltrahumanAPIAuthenticationError(ultrahuman_response.error)
                elif status_code == 400:
                    raise UltrahumanAPIBadRequestError(ultrahuman_response.error)
                elif status_code == 404:
                    raise UltrahumanAPINotFoundError(ultrahuman_response.error)
                elif status_code == 500:
                    raise UltrahumanAPIInternalServerError(ultrahuman_response.error)
                else:
                    raise UltrahumanAPIError(ultrahuman_response.error, status_code=status_code)
            
            return ultrahuman_response.data
        except Exception as e:
            if isinstance(e, UltrahumanAPIError):
                raise
            raise UltrahumanAPIError(f"Failed to parse response: {str(e)}", status_code=None)