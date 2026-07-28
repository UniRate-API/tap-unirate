"""Shared mock payloads and config for the tap-unirate test suite."""

from __future__ import annotations

BASE_URL = "https://api.unirateapi.com"

SAMPLE_CONFIG = {
    "api_key": "test-key",
    "base_currency": "USD",
    "base_url": BASE_URL,
}

CURRENCIES_RESPONSE = {
    "currencies": ["USD", "EUR", "GBP", "JPY", "CAD"],
}

RATES_RESPONSE = {
    "rates": {
        "EUR": "0.92",
        "GBP": "0.79",
        "JPY": "156.4",
        "CAD": "1.37",
    },
}

VAT_RATES_RESPONSE = {
    "total_countries": 3,
    "date": "2026-04-22",
    "vat_rates": {
        "DE": {"country_code": "DE", "country_name": "Germany", "vat_rate": 19.0},
        "FR": {"country_code": "FR", "country_name": "France", "vat_rate": 20.0},
        "IE": {"country_code": "IE", "country_name": "Ireland", "vat_rate": 23.0},
    },
}


def register_all(mock) -> None:
    """Register every UniRate endpoint against a ``requests_mock`` mocker."""
    mock.get(
        f"{BASE_URL}/api/currencies",
        json=CURRENCIES_RESPONSE,
    )
    mock.get(
        f"{BASE_URL}/api/rates",
        json=RATES_RESPONSE,
    )
    mock.get(
        f"{BASE_URL}/api/vat/rates",
        json=VAT_RATES_RESPONSE,
    )
