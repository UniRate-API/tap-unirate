"""Stream definitions for tap-unirate."""

from __future__ import annotations

import typing as t
from collections.abc import Mapping

from singer_sdk import typing as th  # JSON Schema helpers

from tap_unirate.client import UniRateStream

if t.TYPE_CHECKING:
    import requests


class CurrenciesStream(UniRateStream):
    """Supported currency codes.

    ``GET /api/currencies`` returns ``{"currencies": ["USD", "EUR", ...]}``.
    Each code is emitted as its own record.
    """

    name = "currencies"
    path = "/api/currencies"
    primary_keys: t.ClassVar[list[str]] = ["code"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property(
            "code",
            th.StringType,
            required=True,
            description="ISO 4217 currency code.",
        ),
    ).to_dict()

    def parse_response(
        self,
        response: requests.Response,
    ) -> t.Iterable[dict]:
        """Yield one record per supported currency code."""
        payload = response.json()
        for code in payload.get("currencies", []):
            yield {"code": code}


class ExchangeRatesStream(UniRateStream):
    """Latest exchange rates for the configured base currency.

    ``GET /api/rates?from=<base>`` returns
    ``{"rates": {"EUR": "0.92", "GBP": "0.79", ...}}``. Each target currency
    becomes a record keyed on ``(base_currency, currency)``.
    """

    name = "exchange_rates"
    path = "/api/rates"
    primary_keys: t.ClassVar[list[str]] = ["base_currency", "currency"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property(
            "base_currency",
            th.StringType,
            required=True,
            description="Base currency the rate is quoted against.",
        ),
        th.Property(
            "currency",
            th.StringType,
            required=True,
            description="Target currency code.",
        ),
        th.Property(
            "rate",
            th.NumberType,
            required=True,
            description="Units of the target currency per one base unit.",
        ),
    ).to_dict()

    def get_url_params(
        self,
        context: Mapping[str, t.Any] | None,
        next_page_token: t.Any | None,
    ) -> dict[str, t.Any]:
        """Pass the configured base currency as the ``from`` query param."""
        return {"from": self._base_currency}

    @property
    def _base_currency(self) -> str:
        return t.cast(
            str,
            self.config.get("base_currency", "USD"),
        ).upper()

    def parse_response(
        self,
        response: requests.Response,
    ) -> t.Iterable[dict]:
        """Yield one record per target-currency rate."""
        payload = response.json()
        base = self._base_currency
        for currency, rate in payload.get("rates", {}).items():
            yield {
                "base_currency": base,
                "currency": currency,
                "rate": float(rate),
            }


class VatRatesStream(UniRateStream):
    """Country VAT rates.

    ``GET /api/vat/rates`` returns
    ``{"vat_rates": {"DE": {"country_code": "DE", "country_name": "Germany",
    "vat_rate": 19.0}, ...}}``. Each country is emitted as its own record.
    """

    name = "vat_rates"
    path = "/api/vat/rates"
    primary_keys: t.ClassVar[list[str]] = ["country_code"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property(
            "country_code",
            th.StringType,
            required=True,
            description="ISO 3166-1 alpha-2 country code.",
        ),
        th.Property(
            "country_name",
            th.StringType,
            description="Human-readable country name.",
        ),
        th.Property(
            "vat_rate",
            th.NumberType,
            description="Standard VAT rate as a percentage.",
        ),
    ).to_dict()

    def parse_response(
        self,
        response: requests.Response,
    ) -> t.Iterable[dict]:
        """Yield one record per country VAT entry."""
        payload = response.json()
        for code, entry in payload.get("vat_rates", {}).items():
            yield {
                "country_code": entry.get("country_code", code),
                "country_name": entry.get("country_name"),
                "vat_rate": entry.get("vat_rate"),
            }
