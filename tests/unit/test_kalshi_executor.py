"""Unit tests for Kalshi executor."""

import pytest

from src.execution.kalshi import KalshiExecutor


class TestKalshiExecutor:
    """Tests for KalshiExecutor."""

    @pytest.fixture
    def executor(self) -> KalshiExecutor:
        """Create executor instance for testing."""
        return KalshiExecutor(demo=True)

    def test_initialization_demo(self, executor: KalshiExecutor) -> None:
        """Test executor initializes with demo settings."""
        assert executor.platform == "kalshi"
        assert executor._demo is True
        assert "demo" in executor._base_url

    def test_initialization_production(self) -> None:
        """Test executor initializes with production settings."""
        executor = KalshiExecutor(demo=False)
        assert "elections" in executor._base_url

    @pytest.mark.parametrize(
        "price,expected_fee",
        [
            (0.50, 0.02),  # 50 cents: ceil(0.07 * 0.5 * 0.5 * 100) / 100
            (0.90, 0.01),  # 90 cents: ceil(0.07 * 0.9 * 0.1 * 100) / 100
            (0.10, 0.01),  # 10 cents: ceil(0.07 * 0.1 * 0.9 * 100) / 100
            (0.99, 0.01),  # 99 cents: minimal fee
            (0.01, 0.01),  # 1 cent: minimal fee
        ],
    )
    def test_fee_calculation(self, price: float, expected_fee: float) -> None:
        """Test Kalshi fee calculation formula."""
        calculated = KalshiExecutor._calculate_fee(price)
        assert calculated == expected_fee

    @pytest.mark.asyncio
    async def test_connect_without_credentials(self, executor: KalshiExecutor) -> None:
        """Test connection fails gracefully without credentials."""
        result = await executor.connect()
        assert result is False

    @pytest.mark.asyncio
    async def test_get_balance_disconnected(self, executor: KalshiExecutor) -> None:
        """Test balance returns 0 when disconnected."""
        from decimal import Decimal

        balance = await executor.get_balance()
        assert balance == Decimal("0")

    @pytest.mark.asyncio
    async def test_get_positions_disconnected(self, executor: KalshiExecutor) -> None:
        """Test positions returns empty list when disconnected."""
        positions = await executor.get_positions()
        assert positions == []
