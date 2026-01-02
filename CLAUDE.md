# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Alpha-PM is an autonomous AI-powered prediction market trading platform. It uses a multi-agent architecture to trade on Kalshi and Polymarket through copy trading, AI analysis, and cross-platform arbitrage.

**Primary Goal:** Maximize portfolio value through intelligent, autonomous trading.

## Architecture

```
SIGNAL LAYER
├── Copy Monitor (follows profitable traders)
├── AI Analyst (Claude-powered market analysis)
└── Arb Detector (cross-platform price gaps)
        ↓
   ORCHESTRATOR (central decision hub)
        ↓
   RISK MANAGER (*** VETO POWER ***)
        ↓
   EXECUTION (Kalshi + Polymarket executors)
        ↓
   DATA LAYER (PostgreSQL + Redis)
```

## Commands

```bash
# Development setup
uv sync                              # Install dependencies
uv sync --group dev                  # Include dev dependencies

# Run the trading engine
uv run alpha-pm                      # Start main application
uv run python -m src.main            # Alternative

# Database
uv run alembic upgrade head          # Run migrations
uv run alembic revision --autogenerate -m "description"  # Create migration

# Testing
uv run pytest                        # Run all tests
uv run pytest tests/unit             # Unit tests only
uv run pytest -k "test_name"         # Run specific test
uv run pytest --cov=src              # With coverage

# Code quality
uv run black src tests               # Format code
uv run ruff check src tests          # Lint
uv run mypy src                      # Type check

# Docker
docker compose up -d                 # Start services (postgres, redis)
docker compose down                  # Stop services
docker compose logs -f trading       # View logs
```

## Project Structure

```
src/
├── main.py              # Application entry point
├── config.py            # Configuration (pydantic-settings)
├── agents/              # Trading agents
│   ├── orchestrator.py  # Central decision hub
│   ├── ai_analyst.py    # Claude-powered analysis
│   ├── copy_monitor.py  # Copy trading signals
│   ├── arb_detector.py  # Arbitrage detection
│   └── risk_manager.py  # Risk layer (VETO POWER)
├── execution/           # Platform executors
│   ├── kalshi.py        # Kalshi API client
│   ├── polymarket.py    # Polymarket CLOB client
│   └── order_router.py  # Routes to correct platform
├── data/                # Data layer
│   ├── models.py        # SQLAlchemy models
│   ├── repositories.py  # Data access layer
│   └── migrations/      # Alembic migrations
├── monitoring/          # Observability
│   ├── telegram_bot.py  # Alerts and commands
│   ├── metrics.py       # Performance tracking
│   └── health.py        # Health checks
└── utils/               # Shared utilities
    ├── logging.py       # Structured logging
    └── rate_limiter.py  # API rate limiting
```

## Key Design Patterns

### Agent Pattern
All agents inherit from `BaseAgent` and implement:
- `async def start()` - Begin processing
- `async def stop()` - Graceful shutdown
- `async def health_check()` - Return health status

### Risk Manager Veto
The Risk Manager can block ANY trade. It checks:
1. Position limits (max 10% per position)
2. Daily loss limit (5% triggers halt)
3. Circuit breakers (5 consecutive losses = pause)
4. Pre-trade validation

### Configuration
All config via environment variables, loaded by `src/config.py`:
```python
from src.config import settings
print(settings.database_url)
```

## Environment Variables

Required:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `POLYMARKET_PRIVATE_KEY` - Wallet private key
- `POLYMARKET_FUNDER` - Funder address (if using proxy wallet)
- `TELEGRAM_BOT_TOKEN` - For alerts
- `TELEGRAM_CHAT_ID` - Where to send alerts
- `ANTHROPIC_API_KEY` - For AI analyst

Optional:
- `KALSHI_API_KEY` - Kalshi API key (for Kalshi support)
- `KALSHI_PRIVATE_KEY_PATH` - Path to RSA private key
- `LOG_LEVEL` - Default: INFO

## Database Models

Key tables:
- `trades` - All executed trades with P&L
- `positions` - Current open positions
- `signals` - Generated trading signals
- `metrics_daily` - Daily performance metrics
- `alerts` - System alerts

## Testing Strategy

- Unit tests: Test individual functions/methods
- Integration tests: Test with real DB (use test database)
- Always mock external APIs (Polymarket, Kalshi, Claude)

## Risk Limits (Non-Negotiable)

| Limit | Value | Action |
|-------|-------|--------|
| Max single position | 10% | Block trade |
| Max daily loss | 5% | HALT all trading |
| Max drawdown | 15% | HALT + alert |
| Consecutive losses | 5 | PAUSE 1 hour |

## Development Workflow

1. Create feature branch from `main`
2. Write tests first (TDD)
3. Implement feature
4. Run `black`, `ruff`, `mypy`
5. All tests must pass
6. Create PR with description

## Common Tasks

### Add a new agent
1. Create `src/agents/new_agent.py`
2. Inherit from `BaseAgent`
3. Register in `src/agents/__init__.py`
4. Add to orchestrator's agent list

### Add a new platform
1. Create `src/execution/new_platform.py`
2. Implement `BaseExecutor` interface
3. Add to order router
4. Add platform-specific config

### Add database table
1. Add model to `src/data/models.py`
2. Run `alembic revision --autogenerate -m "add table_name"`
3. Run `alembic upgrade head`
