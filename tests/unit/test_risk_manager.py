"""Unit tests for Risk Manager agent."""

from decimal import Decimal

import pytest

from src.agents.risk_manager import RiskManager
from src.execution.base import OrderRequest


class TestRiskManager:
    """Tests for RiskManager agent."""

    @pytest.fixture
    def risk_manager(self) -> RiskManager:
        """Create a RiskManager instance for testing."""
        return RiskManager()

    def test_initialization(self, risk_manager: RiskManager) -> None:
        """Test Risk Manager initializes with correct defaults."""
        assert risk_manager.name == "risk_manager"
        assert risk_manager._emergency_stop is False
        assert risk_manager._max_position_pct == Decimal("10.0")
        assert risk_manager._max_daily_loss_pct == Decimal("5.0")
        assert risk_manager._max_drawdown_pct == Decimal("15.0")

    @pytest.mark.asyncio
    async def test_health_check(self, risk_manager: RiskManager) -> None:
        """Test health check returns expected structure."""
        health = await risk_manager.health_check()

        assert "name" in health
        assert "running" in health
        assert "emergency_stop" in health
        assert "daily_loss_pct" in health
        assert "open_positions" in health

    @pytest.mark.asyncio
    async def test_evaluate_order_emergency_stop(self, risk_manager: RiskManager) -> None:
        """Test order rejection when emergency stop is active."""
        risk_manager._emergency_stop = True

        order = OrderRequest(
            market_id="test-market",
            side="buy",
            size=Decimal("10"),
            price=Decimal("50"),
            order_type="limit",
        )

        approved, reason = await risk_manager.evaluate_order(order)

        assert approved is False
        assert "emergency stop" in reason.lower()

    def test_position_size_calculation(self, risk_manager: RiskManager) -> None:
        """Test position size is capped correctly."""
        # TODO: Implement position sizing tests
        pass

    def test_daily_loss_tracking(self, risk_manager: RiskManager) -> None:
        """Test daily loss accumulation and halt trigger."""
        # TODO: Implement daily loss tracking tests
        pass

    def test_circuit_breaker(self, risk_manager: RiskManager) -> None:
        """Test circuit breaker activation."""
        # TODO: Implement circuit breaker tests
        pass
