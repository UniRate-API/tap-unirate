"""TapUniRate: the tap entry point."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON Schema helpers

from tap_unirate import streams


class TapUniRate(Tap):
    """Singer tap for the UniRate currency-exchange API."""

    name = "tap-unirate"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            secret=True,
            title="API Key",
            description="UniRate API key. Get a free one at https://unirateapi.com.",
        ),
        th.Property(
            "base_currency",
            th.StringType,
            default="USD",
            title="Base Currency",
            description=(
                "Base currency (ISO 4217) for the exchange_rates stream. "
                "Defaults to USD."
            ),
        ),
        th.Property(
            "base_url",
            th.StringType,
            default="https://api.unirateapi.com",
            title="API Base URL",
            description="Override the API base URL (primarily for testing).",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.UniRateStream]:
        """Return a list of discovered streams.

        Returns:
            A list of stream instances.
        """
        return [
            streams.CurrenciesStream(self),
            streams.ExchangeRatesStream(self),
            streams.VatRatesStream(self),
        ]


if __name__ == "__main__":
    TapUniRate.cli()
