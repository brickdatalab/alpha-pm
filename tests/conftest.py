"""Pytest configuration and fixtures."""

import asyncio
from collections.abc import Generator
from decimal import Decimal

import pytest


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_order_request() -> dict:
    """Sample order request data for testing."""
    return {
        "market_id": "test-market-123",
        "side": "buy",
        "size": Decimal("10"),
        "price": Decimal("50"),
        "order_type": "limit",
    }


@pytest.fixture
def mock_market_data() -> dict:
    """Mock market data for testing."""
    return {
        "id": "test-market-123",
        "title": "Test Market",
        "yes_price": Decimal("50"),
        "no_price": Decimal("50"),
        "volume": Decimal("10000"),
        "end_date": "2025-12-31T23:59:59Z",
    }
