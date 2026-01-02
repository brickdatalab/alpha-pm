"""Arbitrage Detector agent - finds cross-platform arbitrage opportunities."""

import asyncio
from dataclasses import dataclass
from decimal import Decimal

import structlog

from src.agents.base import BaseAgent
from src.config import settings

logger = structlog.get_logger(__name__)


@dataclass
class ArbOpportunity:
    """A detected arbitrage opportunity."""

    market_title: str
    kalshi_market_id: str | None
    polymarket_market_id: str | None

    # Prices (in cents, 0-100)
    kalshi_yes_price: Decimal | None
    kalshi_no_price: Decimal | None
    polymarket_yes_price: Decimal | None
    polymarket_no_price: Decimal | None

    # Calculated edge
    edge_pct: Decimal
    arb_type: str  # "cross_platform" | "same_platform"

    # Execution details
    recommended_size: Decimal
    estimated_profit: Decimal
    expires_at: str | None


class ArbDetector(BaseAgent):
    """
    Cross-platform arbitrage detector.

    Looks for:
    - Cross-platform arb: Kalshi YES + Polymarket NO (or vice versa)
    - Same-platform arb: Spread opportunities within a single platform
    - Fee-adjusted calculations (Kalshi ~7% vs Polymarket 0%)

    Strategy allocation: 15% of portfolio
    """

    name = "arb_detector"

    def __init__(self) -> None:
        super().__init__()
        self._market_mappings: dict[str, dict] = {}  # Maps equivalent markets across platforms
        self._min_edge_pct = Decimal("2.0")  # Minimum edge after fees to consider
        self._kalshi_fee_pct = Decimal("7.0")  # Kalshi fee rate

    async def start(self) -> None:
        """Start arbitrage detection."""
        await super().start()
        logger.info("arb_detector_starting", min_edge=str(self._min_edge_pct))

        # TODO: Load market mappings from database
        # TODO: Connect to price feeds
        await self._run_detection_loop()

    async def stop(self) -> None:
        """Stop detection."""
        logger.info("arb_detector_stopping")
        await super().stop()

    async def health_check(self) -> dict:
        """Check arb detector health."""
        base_health = await super().health_check()
        return {
            **base_health,
            "mapped_markets": len(self._market_mappings),
            "min_edge_pct": str(self._min_edge_pct),
        }

    async def find_opportunities(self) -> list[ArbOpportunity]:
        """
        Scan all mapped markets for arbitrage opportunities.

        Returns list of opportunities sorted by edge (highest first).
        """
        opportunities = []

        for mapping_id, mapping in self._market_mappings.items():
            opp = await self._check_market_pair(mapping)
            if opp and opp.edge_pct >= self._min_edge_pct:
                opportunities.append(opp)

        return sorted(opportunities, key=lambda x: x.edge_pct, reverse=True)

    async def _check_market_pair(self, mapping: dict) -> ArbOpportunity | None:
        """Check a specific market pair for arbitrage."""
        # TODO: Fetch current prices from both platforms
        # TODO: Calculate cross-platform arbitrage
        # TODO: Account for fees on each side
        # TODO: Check liquidity depth
        return None

    def _calculate_edge(
        self,
        buy_price: Decimal,
        sell_price: Decimal,
        buy_platform: str,
        sell_platform: str,
    ) -> Decimal:
        """Calculate edge after fees."""
        # Kalshi fee: ceil(0.07 * P * (1-P)) per contract
        # Polymarket: 0% fees

        gross_edge = sell_price - buy_price

        # Apply platform-specific fees
        if buy_platform == "kalshi":
            buy_fee = (self._kalshi_fee_pct / 100) * buy_price * (100 - buy_price) / 100
            gross_edge -= buy_fee
        if sell_platform == "kalshi":
            sell_fee = (self._kalshi_fee_pct / 100) * sell_price * (100 - sell_price) / 100
            gross_edge -= sell_fee

        return gross_edge

    async def _run_detection_loop(self) -> None:
        """Main detection loop."""
        while self._running:
            try:
                opportunities = await self.find_opportunities()
                if opportunities:
                    logger.info(
                        "arb_detector_opportunities_found",
                        count=len(opportunities),
                        best_edge=str(opportunities[0].edge_pct),
                    )
                    # TODO: Submit opportunities as signals to orchestrator
                await asyncio.sleep(settings.polling_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception("arb_detector_loop_error", error=str(e))
                await asyncio.sleep(5)
