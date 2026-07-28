"""Record-level tests for each tap-unirate stream (fully mocked)."""

from __future__ import annotations

import json

import pytest
import requests_mock as rm_module

from tap_unirate.tap import TapUniRate
from tests import fixtures


@pytest.fixture
def tap() -> TapUniRate:
    """Return a tap configured against the mock base URL."""
    return TapUniRate(config=fixtures.SAMPLE_CONFIG, parse_env_config=False)


@pytest.fixture
def mocked():
    """Yield a requests_mock mocker with every endpoint registered."""
    with rm_module.Mocker() as m:
        fixtures.register_all(m)
        yield m


def _get_stream(tap: TapUniRate, name: str):
    return next(s for s in tap.streams.values() if s.name == name)


def _collect(stream) -> list[dict]:
    return list(stream.get_records(context=None))


# --- discovery / catalog -------------------------------------------------


def test_discover_streams_count(tap: TapUniRate) -> None:
    assert len(tap.discover_streams()) == 3


def test_stream_names(tap: TapUniRate) -> None:
    names = {s.name for s in tap.streams.values()}
    assert names == {"currencies", "exchange_rates", "vat_rates"}


def test_catalog_is_valid_json(tap: TapUniRate) -> None:
    catalog = tap.catalog_dict
    # Round-trips through JSON without error.
    json.loads(json.dumps(catalog))
    assert {c["tap_stream_id"] for c in catalog["streams"]} == {
        "currencies",
        "exchange_rates",
        "vat_rates",
    }


# --- currencies ----------------------------------------------------------


def test_currencies_primary_key(tap: TapUniRate) -> None:
    assert _get_stream(tap, "currencies").primary_keys == ["code"]


def test_currencies_records(tap: TapUniRate, mocked) -> None:
    records = _collect(_get_stream(tap, "currencies"))
    assert len(records) == len(fixtures.CURRENCIES_RESPONSE["currencies"])
    assert {r["code"] for r in records} == set(
        fixtures.CURRENCIES_RESPONSE["currencies"]
    )


def test_currencies_schema_keys(tap: TapUniRate, mocked) -> None:
    record = next(iter(_collect(_get_stream(tap, "currencies"))))
    assert set(record) == {"code"}


# --- exchange_rates ------------------------------------------------------


def test_exchange_rates_primary_key(tap: TapUniRate) -> None:
    assert _get_stream(tap, "exchange_rates").primary_keys == [
        "base_currency",
        "currency",
    ]


def test_exchange_rates_records(tap: TapUniRate, mocked) -> None:
    records = _collect(_get_stream(tap, "exchange_rates"))
    assert len(records) == len(fixtures.RATES_RESPONSE["rates"])
    for r in records:
        assert set(r) == {"base_currency", "currency", "rate"}
        assert r["base_currency"] == "USD"
        assert isinstance(r["rate"], float)


def test_exchange_rates_rate_parsed_to_float(tap: TapUniRate, mocked) -> None:
    records = {r["currency"]: r for r in _collect(_get_stream(tap, "exchange_rates"))}
    assert records["EUR"]["rate"] == 0.92


def test_exchange_rates_sends_from_param(tap: TapUniRate, mocked) -> None:
    _collect(_get_stream(tap, "exchange_rates"))
    last = mocked.request_history[-1]
    assert last.qs["from"] == ["usd"]  # requests_mock lowercases query keys/vals
    assert last.qs["api_key"] == ["test-key"]


def test_exchange_rates_custom_base_currency(mocked) -> None:
    cfg = {**fixtures.SAMPLE_CONFIG, "base_currency": "eur"}
    tap = TapUniRate(config=cfg, parse_env_config=False)
    records = _collect(_get_stream(tap, "exchange_rates"))
    assert all(r["base_currency"] == "EUR" for r in records)
    assert mocked.request_history[-1].qs["from"] == ["eur"]


# --- vat_rates -----------------------------------------------------------


def test_vat_rates_primary_key(tap: TapUniRate) -> None:
    assert _get_stream(tap, "vat_rates").primary_keys == ["country_code"]


def test_vat_rates_records(tap: TapUniRate, mocked) -> None:
    records = _collect(_get_stream(tap, "vat_rates"))
    assert len(records) == len(fixtures.VAT_RATES_RESPONSE["vat_rates"])
    for r in records:
        assert set(r) == {"country_code", "country_name", "vat_rate"}


def test_vat_rates_values(tap: TapUniRate, mocked) -> None:
    records = {r["country_code"]: r for r in _collect(_get_stream(tap, "vat_rates"))}
    assert records["DE"]["country_name"] == "Germany"
    assert records["DE"]["vat_rate"] == 19.0


# --- auth / headers ------------------------------------------------------


def test_accept_json_header_sent(tap: TapUniRate, mocked) -> None:
    _collect(_get_stream(tap, "currencies"))
    assert mocked.request_history[-1].headers["Accept"] == "application/json"


def test_user_agent_header_sent(tap: TapUniRate, mocked) -> None:
    _collect(_get_stream(tap, "currencies"))
    assert mocked.request_history[-1].headers["User-Agent"].startswith("tap-unirate/")


def test_api_key_in_query_for_all_streams(tap: TapUniRate, mocked) -> None:
    for name in ("currencies", "exchange_rates", "vat_rates"):
        _collect(_get_stream(tap, name))
        assert mocked.request_history[-1].qs["api_key"] == ["test-key"]
