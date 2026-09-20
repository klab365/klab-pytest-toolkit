from typing import Any, Dict, Optional
from klab_pytest_toolkit_web._api_client_types import ApiClient
import requests


class RestApiClient(ApiClient):
    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize REST API client.

        Args:
            base_url: Base URL for API requests
            headers: Optional default headers for all requests
            timeout: Default timeout in seconds for all requests. Can be
                overridden per request via the ``timeout`` argument.
        """
        self.base_url = base_url
        self.headers = headers or {}
        self.timeout = timeout
        self.session = requests.Session()

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        """
        Make a GET request.

        Args:
            endpoint: API endpoint path
            params: Optional query parameters
            timeout: Optional timeout in seconds for this request

        Returns:
            Response object
        """
        url = f"{self.base_url}{endpoint}"
        return self.session.get(
            url,
            params=params,
            headers=self.headers,
            timeout=timeout if timeout is not None else self.timeout,
        )

    def post(
        self,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        """
        Make a POST request.

        Args:
            endpoint: API endpoint path
            payload: Optional JSON payload
            timeout: Optional timeout in seconds for this request

        Returns:
            Response object
        """
        url = f"{self.base_url}{endpoint}"
        return self.session.post(
            url,
            json=payload,
            headers=self.headers,
            timeout=timeout if timeout is not None else self.timeout,
        )

    def put(
        self,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        """
        Make a PUT request.

        Args:
            endpoint: API endpoint path
            payload: Optional JSON payload
            timeout: Optional timeout in seconds for this request

        Returns:
            Response object
        """
        url = f"{self.base_url}{endpoint}"
        return self.session.put(
            url,
            json=payload,
            headers=self.headers,
            timeout=timeout if timeout is not None else self.timeout,
        )

    def patch(
        self,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        """
        Make a PATCH request.

        Args:
            endpoint: API endpoint path
            payload: Optional JSON payload
            timeout: Optional timeout in seconds for this request

        Returns:
            Response object
        """
        url = f"{self.base_url}{endpoint}"
        return self.session.patch(
            url,
            json=payload,
            headers=self.headers,
            timeout=timeout if timeout is not None else self.timeout,
        )

    def delete(
        self,
        endpoint: str,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        """
        Make a DELETE request.

        Args:
            endpoint: API endpoint path
            timeout: Optional timeout in seconds for this request

        Returns:
            Response object
        """
        url = f"{self.base_url}{endpoint}"
        return self.session.delete(
            url,
            headers=self.headers,
            timeout=timeout if timeout is not None else self.timeout,
        )

    def close(self) -> None:
        """Close the session."""
        self.session.close()
