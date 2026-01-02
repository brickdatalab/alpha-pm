"""Risk Manager agent with VETO power over all trades."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any

import structlog

from src.agents.base import AgentStatus, BaseAgent, HealthStatus
from src.config import settings

log = structlog.get_logger()


class RiskDecision(Enum):
    """Risk manager decision on a trade."""

    APPROVED = "approved"
    REJECTED = "rejected"
    REDUCED = "reduced"  # Approved but with reduced size


@dataclass
class TradeRequest:
    """A trade request to be evaluated by risk manager."""

    market_id: str
    platform: str  # 'kalshi' | 'polymarket'
    side: str  # 'buy' | 'sell'
    size: Decimal
    price: Decimal
    signal_source: str  # 'copy' | 'ai' | 'arb'
    confidence: float | None = None


@dataclass
class RiskEvaluation:
    """Result of risk evaluation."""

    decision: RiskDecision
    original_size: Decimal
    approved_size: Decimal
    reasons: list[str]
    checks_passed: dict[str, bool]


class RiskManager(BaseAgent):
    """Risk Manager with VETO power over all trades.

    This agent has the final say on whether a trade executes.
    It enforces:
    - Position limits
    - Daily loss limits
    - Circuit breakers
    - Correlation limits
    """

    def __init__(self) -> None:
        super().__init__("risk_manager")

        # Configuration
        self.max_single_position_pct = settings.max_single_position_pct
        self.max_daily_loss_pct = settings.max_daily_loss_pct
        self.max_drawdown_pct = settings.max_drawdown_pct
        self.consecutive_loss_pause = settings.consecutive_loss_pause

        # State
        self.daily_pnl = Decimal("0")
        self.consecutive_losses = 0
        self.peak_portfolio_value = Decimal("0")
        self.current_portfolio_value = Decimal("0")
        self.positions: dict[str, Decimal] = {}  # market_id -> size

        # Circuit breaker state
        self.is_halted = False
        self.halt_reason: str | None = None
        self.paused_until: datetime | None = None

    async def start(self) -> None:
        """Start the risk manager."""
        self._log.info("Starting risk manager")
        self.status = AgentStatus.RUNNING
        # TODO: Load state from database

    async def stop(self) -> None:
        """Stop the risk manager."""
        self._log.info("Stopping risk manager")
        self.status = AgentStatus.STOPPED
        # TODO: Persist state to database

    async def health_check(self) -> HealthStatus:
        """Check risk manager health."""
        return HealthStatus(
            healthy=self.is_healthy() and not self.is_halted,
            status=self.status,
            message="Halted" if self.is_halted else "OK",
            last_check=datetime.now(timezone.utc),
            details={
                "halted": self.is_halted,
                "halt_reason": self.halt_reason,
                "daily_pnl": str(self.daily_pnl),
                "consecutive_losses": self.consecutive_losses,
            },
        )

    async def evaluate_trade(self, trade: TradeRequest) -> RiskEvaluation:
        """Evaluate a trade request.

        This is the main entry point. Returns an evaluation with:
        - Decision (approved/rejected/reduced)
        - Approved size (may be less than requested)
        - Reasons for the decision
        """
        checks: dict[str, bool] = {}
        reasons: list[str] = []

        # Check 1: Is trading halted?
        if self.is_halted:
            return RiskEvaluation(
                decision=RiskDecision.REJECTED,
                original_size=trade.size,
                approved_size=Decimal("0"),
                reasons=[f"Trading halted: {self.halt_reason}"],
                checks_passed={"not_halted": False},
            )
        checks["not_halted"] = True

        # Check 2: Is agent paused?
        if self.paused_until and datetime.now(timezone.utc) < self.paused_until:
            return RiskEvaluation(
                decision=RiskDecision.REJECTED,
                original_size=trade.size,
                approved_size=Decimal("0"),
                reasons=[f"Trading paused until {self.paused_until}"],
                checks_passed={"not_paused": False},
            )
        checks["not_paused"] = True

        # Check 3: Position limit
        position_value = trade.size * trade.price
        max_position = self.current_portfolio_value * Decimal(str(self.max_single_position_pct / 100))
        checks["position_limit"] = position_value <= max_position
        if not checks["position_limit"]:
            reasons.append(f"Position {position_value} exceeds limit {max_position}")

        # Check 4: Daily loss limit
        drawdown_pct = (
            (self.peak_portfolio_value - self.current_portfolio_value)
            / self.peak_portfolio_value
            * 100
            if self.peak_portfolio_value > 0
            else Decimal("0")
        )
        checks["daily_loss_limit"] = float(drawdown_pct) < self.max_daily_loss_pct
        if not checks["daily_loss_limit"]:
            reasons.append(f"Daily loss {drawdown_pct}% exceeds limit {self.max_daily_loss_pct}%")
            await self._trigger_halt("Daily loss limit exceeded")

        # Check 5: Max drawdown
        checks["max_drawdown"] = float(drawdown_pct) < self.max_drawdown_pct
        if not checks["max_drawdown"]:
            reasons.append(f"Drawdown {drawdown_pct}% exceeds limit {self.max_drawdown_pct}%")
            await self._trigger_halt("Max drawdown exceeded")

        # Determine final decision
        if all(checks.values()):
            return RiskEvaluation(
                decision=RiskDecision.APPROVED,
                original_size=trade.size,
                approved_size=trade.size,
                reasons=["All checks passed"],
                checks_passed=checks,
            )
        elif checks.get("position_limit") is False and all(
            v for k, v in checks.items() if k != "position_limit"
        ):
            # Only position limit failed - reduce size
            reduced_size = max_position / trade.price
            return RiskEvaluation(
                decision=RiskDecision.REDUCED,
                original_size=trade.size,
                approved_size=reduced_size,
                reasons=reasons + [f"Size reduced to {reduced_size}"],
                checks_passed=checks,
            )
        else:
            return RiskEvaluation(
                decision=RiskDecision.REJECTED,
                original_size=trade.size,
                approved_size=Decimal("0"),
                reasons=reasons,
                checks_passed=checks,
            )

    async def record_trade_result(self, pnl: Decimal, is_win: bool) -> None:
        """Record the result of an executed trade."""
        self.daily_pnl += pnl

        if is_win:
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
            if self.consecutive_losses >= self.consecutive_loss_pause:
                await self._trigger_pause(duration_minutes=60)

    async def _trigger_halt(self, reason: str) -> None:
        """Trigger a trading halt."""
        self._log.critical("HALT TRIGGERED", reason=reason)
        self.is_halted = True
        self.halt_reason = reason
        # TODO: Send critical alert via Telegram

    async def _trigger_pause(self, duration_minutes: int) -> None:
        """Trigger a temporary pause."""
        self._log.warning("PAUSE TRIGGERED", duration_minutes=duration_minutes)
        self.paused_until = datetime.now(timezone.utc)
        # TODO: Add timedelta for pause duration
        # TODO: Send warning alert via Telegram

    async def reset_daily_stats(self) -> None:
        """Reset daily statistics (call at UTC midnight)."""
        self._log.info("Resetting daily stats", previous_pnl=str(self.daily_pnl))
        self.daily_pnl = Decimal("0")
        self.consecutive_losses = 0

        # Update peak if current > peak
        if self.current_portfolio_value > self.peak_portfolio_value:
            self.peak_portfolio_value = self.current_portfolio_value

    async def emergency_stop(self) -> None:
        """Emergency stop - halt all trading immediately."""
        self._log.critical("EMERGENCY STOP ACTIVATED")
        self.is_halted = True
        self.halt_reason = "Emergency stop activated by user"
        # TODO: Cancel all pending orders
        # TODO: Optionally close all positions
        # TODO: Send critical alert
