# tap-unirate

[![PyPI](https://img.shields.io/pypi/v/tap-unirate.svg)](https://pypi.org/project/tap-unirate/)
[![Meltano](https://img.shields.io/badge/Meltano-SDK-311f6b?logo=meltano)](https://hub.meltano.com/extractors/tap-unirate)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A [Singer](https://www.singer.io/) tap for **[UniRateAPI](https://unirateapi.com)**,
built on the [Meltano Singer SDK](https://sdk.meltano.com). Pull live currency
exchange rates, the supported-currency list, and country VAT rates into any
Singer target or Meltano ELT pipeline.

## Streams

| Stream | Endpoint | Primary key | Description |
|---|---|---|---|
| `currencies` | `GET /api/currencies` | `code` | One record per supported ISO 4217 currency code. |
| `exchange_rates` | `GET /api/rates?from=<base>` | `base_currency`, `currency` | Latest rate for every target currency against the configured base. |
| `vat_rates` | `GET /api/vat/rates` | `country_code` | Standard VAT rate per country (ISO 3166-1 alpha-2). |

> Historical rates and time series are **Pro-gated** on the UniRate API and are
> intentionally not exposed by this tap (they return HTTP 403 on the free tier).

## Install

```bash
pip install tap-unirate
```

Requires Python 3.9+.

Or add it to a Meltano project:

```bash
meltano add extractor tap-unirate
```

## Configuration

| Setting | Required | Default | Description |
|---|---|---|---|
| `api_key` | yes | — | UniRate API key. Get a free one at <https://unirateapi.com>. |
| `base_currency` | no | `USD` | Base currency (ISO 4217) for the `exchange_rates` stream. |
| `base_url` | no | `https://api.unirateapi.com` | Override the API base URL (mainly for testing). |

Full config reference:

```bash
tap-unirate --about --format=markdown
```

## Usage

### Standalone

```bash
# Discover the catalog
tap-unirate --config config.json --discover > catalog.json

# Sync records (Singer messages on stdout)
tap-unirate --config config.json --catalog catalog.json | target-jsonl
```

Example `config.json`:

```json
{
  "api_key": "YOUR_UNIRATE_API_KEY",
  "base_currency": "USD"
}
```

### Meltano

```bash
meltano config tap-unirate set api_key $UNIRATE_API_KEY
meltano config tap-unirate set base_currency EUR
meltano run tap-unirate target-jsonl
```

See [`examples/`](examples/) for a sample config and the full discovery flow.

## Development

```bash
pip install -e ".[test]"
pytest
ruff check tap_unirate tests
```

All tests are fully mocked with [`requests-mock`](https://requests-mock.readthedocs.io/)
— no live API calls, no key required. The suite combines the Singer SDK's
standard tap tests (`get_tap_test_class`) with per-stream record assertions.

## Status

`v0.1.0` — initial release. 3 streams. Built on `singer-sdk >= 0.40`.

<!-- unirate-ecosystem-footer:start -->
## Other UniRate clients

UniRate ships official client libraries and framework integrations across the
ecosystem, all maintained under the
[UniRate-API](https://github.com/UniRate-API) org.

- **Languages:** [Python](https://github.com/UniRate-API/unirate-api-python) · [Node.js / TypeScript](https://github.com/UniRate-API/unirate-api-nodejs) · [Go](https://github.com/UniRate-API/unirate-api-go) · [Rust](https://github.com/UniRate-API/unirate-api-rust) · [Java](https://github.com/UniRate-API/unirate-api-java) · [Ruby](https://github.com/UniRate-API/unirate-api-ruby) · [PHP](https://github.com/UniRate-API/unirate-api-php) · [.NET](https://github.com/UniRate-API/unirate-api-dotnet) · [Swift](https://github.com/UniRate-API/unirate-api-swift)
- **Data / orchestration:** [Airflow](https://github.com/UniRate-API/airflow-provider-unirate) · [dbt](https://github.com/UniRate-API/dbt-unirate) · [LangChain](https://github.com/UniRate-API/langchain-unirate)
- **Workflow / no-code:** [n8n](https://github.com/UniRate-API/n8n-nodes-unirate) · [Google Sheets](https://github.com/UniRate-API/unirate-sheets) · [MCP server](https://github.com/UniRate-API/unirate-mcp)

Get a free API key at [unirateapi.com](https://unirateapi.com).
<!-- unirate-ecosystem-footer:end -->

## License

MIT.

## Links

- UniRate API docs: <https://unirateapi.com/docs>
- Meltano Singer SDK: <https://sdk.meltano.com>
- Issues: <https://github.com/UniRate-API/tap-unirate/issues>
