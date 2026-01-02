"""Main entry point for Alpha-PM trading engine."""

import asyncio
import signal
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog

from src.config import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer() if settings.log_level == "DEBUG" else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        getattr(structlog, settings.log_level)
    ),
)

log = structlog.get_logger()


class TradingEngine:
    """Main trading engine that coordinates all agents."""

    def __init__(self) -> None:
        self.running = False
        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        """Start the trading engine."""
        log.info("Starting Alpha-PM trading engine", version="0.1.0")

        # Validate configuration
        self._validate_config()

        self.running = True

        # TODO: Initialize components
        # - Database connection
        # - Redis connection
        # - Platform executors (Polymarket, Kalshi)
        # - Agents (Orchestrator, Risk Manager, etc.)
        # - Telegram bot

        log.info("Trading engine started successfully")

        # Wait for shutdown signal
        await self._shutdown_event.wait()

    async def stop(self) -> None:
        """Gracefully stop the trading engine."""
        log.info("Stopping trading engine...")
        self.running = False

        # TODO: Graceful shutdown
        # - Stop accepting new signals
        # - Wait for pending orders
        # - Persist state
        # - Close connections

        self._shutdown_event.set()
        log.info("Trading engine stopped")

    def _validate_config(self) -> None:
        """Validate required configuration."""
        errors = []

        if settings.enable_copy_trading and not settings.polymarket_private_key:
            errors.append("POLYMARKET_PRIVATE_KEY required for copy trading")

        if settings.enable_ai_trading and not settings.anthropic_api_key:
            errors.append("ANTHROPIC_API_KEY required for AI trading")

        if not settings.telegram_bot_token or not settings.telegram_chat_id:
            log.warning("Telegram not configured - alerts will be disabled")

        if errors:
            for error in errors:
                log.error(error)
            raise ValueError(f"Configuration errors: {', '.join(errors)}")


@asynccontextmanager
async def lifespan() -> AsyncGenerator[TradingEngine, None]:
    """Manage trading engine lifecycle."""
    engine = TradingEngine()

    # Setup signal handlers
    loop = asyncio.get_event_loop()

    def signal_handler() -> None:
        log.info("Received shutdown signal")
        asyncio.create_task(engine.stop())

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)

    try:
        yield engine
    finally:
        await engine.stop()


async def run() -> None:
    """Run the trading engine."""
    async with lifespan() as engine:
        await engine.start()


def main() -> None:
    """Main entry point."""
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        log.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        log.exception("Fatal error", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
