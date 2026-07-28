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


class TestTapUniRate(_BaseTapTests):
    """Standard SDK tap tests with mocked HTTP.

    The mocker is ``scope="class"`` so it is active when the SDK's own
    class-scoped ``runner`` fixture calls ``sync_all()`` — a function-scoped
    fixture would resolve too late and let the sync hit the live API.
    """

    @pytest.fixture(scope="class", autouse=True)
    @classmethod
    def _mock_http(cls):
        with rm_module.Mocker() as m:
            fixtures.register_all(m)
            yield m
