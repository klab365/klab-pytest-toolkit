"""Klab Pytest Toolkit - Web Fixtures"""

from klab_pytest_toolkit_webfixtures.validators import (
    JsonResponseValidator,
    JsonResponseValidatorFactory,
)

from klab_pytest_toolkit_webfixtures.api_client import ApiClientFactory, RestApiClient

from klab_pytest_toolkit_webfixtures.web_client import (
    WebClientFactory,
    WebClient,
    PlayWrightWebClient,
)

__version__ = "0.0.1"

__all__ = [
    "JsonResponseValidator",
    "JsonResponseValidatorFactory",
    "RestApiClient",
    "ApiClientFactory",
    "WebClient",
    "WebClientFactory",
    "PlayWrightWebClient",
]
