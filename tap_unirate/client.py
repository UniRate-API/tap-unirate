"""REST client base class for tap-unirate."""

from __future__ import annotations

import typing as t

from singer_sdk.authenticators import APIKeyAuthenticator
from singer_sdk.streams import RESTStream

__version__ = "0.1.0"


class UniRateStream(RESTStream):
    """Base stream class for the UniRate API.

    UniRate authenticates via an ``api_key`` query parameter and always
    requires ``Accept: application/json`` (``/api/currencies`` returns an
    HTML 404 otherwise).
    """

    # UniRate wraps its payloads in a single top-level object rather than a
    # bare array, so each concrete stream flattens the response itself in
    # ``parse_response`` rather than relying on a shared ``records_jsonpath``.
    records_jsonpath = "$[*]"

    @property
    def url_base(self) -> str:
        """Return the API base URL, configurable for testing."""
        return t.cast(
            str,
            self.config.get("base_url", "https://api.unirateapi.com"),
        )

    @property
    def authenticator(self) -> APIKeyAuthenticator:
        """Authenticate every request with the ``api_key`` query parameter."""
        return APIKeyAuthenticator(
            key="api_key",
            value=t.cast(str, self.config["api_key"]),
            location="params",
        )

    @property
    def http_headers(self) -> dict[str, str]:
        """Send ``Accept: application/json`` on every request."""
        headers = super().http_headers
        headers["Accept"] = "application/json"
        headers["User-Agent"] = f"tap-unirate/{__version__}"
        return headers
