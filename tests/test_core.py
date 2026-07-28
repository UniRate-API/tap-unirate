"""SDK standard tap tests, run against fully mocked HTTP endpoints.

Uses ``singer_sdk.testing.get_tap_test_class`` to generate the standard
suite (tap CLI, catalog, replication, record schema conformance). An
autouse ``requests_mock`` fixture ensures every generated test that syncs
records hits the in-memory mocks rather than the live API.
"""

from __future__ import annotations

import pytest
import requests_mock as rm_module
from singer_sdk.testing import get_tap_test_class

from tap_unirate.tap import TapUniRate
from tests import fixtures

# Generate the SDK's standard tap test suite.
_BaseTapTests = get_tap_test_class(
    tap_class=TapUniRate,
    config=fixtures.SAMPLE_CONFIG,
)


@pytest.fixture(scope="class", autouse=True)
def _mock_http():
    """Register the HTTP mocks for the class-scoped SDK tap tests.

    Defined at module scope (not as a method) so it works identically across
    Python/pytest versions: a class-scoped fixture written as an instance
    method is deprecated in pytest 9, while wrapping it in ``@classmethod``
    breaks under pytest 8 on Python 3.9 (``classmethod`` has no ``__name__``).
    It is ``scope="class"`` so the mocks are live when the SDK's own
    class-scoped ``runner`` fixture calls ``sync_all()`` — a function-scoped
    fixture would resolve too late and let the sync hit the live API.
    """
    with rm_module.Mocker() as m:
        fixtures.register_all(m)
        yield m


class TestTapUniRate(_BaseTapTests):
    """Standard SDK tap tests with mocked HTTP (see ``_mock_http`` above)."""
