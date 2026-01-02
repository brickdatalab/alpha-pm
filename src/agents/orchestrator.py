"""Orchestrator agent - coordinates all other agents."""

import asyncio
from decimal import Decimal

import structlog

from src.agents.base import BaseAgent
from src.config import settings

logger = structlog.get_logger(__name__)


class Orchestrator(BaseAgent):
    """
    Central coordinator for all trading agents.

    Responsibilities:
    - Spawn and manage child agents
    - Route signals between agents
    - Aggregate decisions from multiple sources
    - Apply strategy allocation weights
    - Delegate final execution to Risk Manager
    """

    name = "orchestrator"

    def __init__(self) -> None:
        super().__init__()
        self._child_agents: list[BaseAgent] = []
        self._strategy_weights = {
            "ai_analyst": Decimal("0.40"),
            "copy_monitor": Decimal("0.35"),
            "arb_detector": Decimal("0.15"),
            "cash_reserve": Decimal("0.10"),
        }

    async def start(self) -> None:
        """Start the orchestrator and all child agents."""
        await super().start()
        logger.info("orchestrator_starting", strategies=list(self._strategy_weights.keys()))
        # TODO: Initialize and start child agents
        # TODO: Set up signal routing pub/sub
        await self._run_main_loop()

    async def stop(self) -> None:
        """Stop all child agents and the orchestrator."""
        logger.info("orchestrator_stopping")
        for agent in reversed(self._child_agents):
            await agent.stop()
        await super().stop()

    async def health_check(self) -> dict:
        """Check health of orchestrator and all child agents."""
        base_health = await super().health_check()
        child_health = {}
        for agent in self._child_agents:
            child_health[agent.name] = await agent.health_check()
        return {
            **base_health,
            "child_agents": child_health,
            "strategy_weights": {k: str(v) for k, v in self._strategy_weights.items()},
        }

    async def _run_main_loop(self) -> None:
        """Main orchestration loop."""
        while self._running:
            try:
                # TODO: Poll for signals from child agents
                # TODO: Aggregate and weight signals
                # TODO: Submit to risk manager for approval
                # TODO: Execute approved trades
                await asyncio.sleep(settings.polling_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception("orchestrator_loop_error", error=str(e))
                await asyncio.sleep(5)  # Back off on error
