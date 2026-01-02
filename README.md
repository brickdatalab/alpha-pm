# Alpha-PM

> Autonomous AI-powered prediction market trading platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

Alpha-PM is a multi-agent trading system for prediction markets (Kalshi & Polymarket) that combines:
- **AI-powered analysis** using Claude for market evaluation
- **Copy trading** to follow profitable traders
- **Cross-platform arbitrage** detection
- **Robust risk management** with circuit breakers

## Features

- **Multi-Agent Architecture**: Orchestrator coordinates signals from AI analyst, copy monitor, and arbitrage detector
- **Risk Manager with Veto Power**: Hard limits on positions, daily losses, and drawdowns
- **Autonomous Operation**: Runs 24/7 with Telegram alerts for monitoring
- **Full Audit Trail**: Every trade, signal, and decision is logged to PostgreSQL

## Quick Start

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- [uv](https://github.com/astral-sh/uv) package manager
- Polymarket wallet with USDC
- Telegram bot (for alerts)

### Installation

```bash
# Clone the repository
git clone https://github.com/brickdatalab/alpha-pm.git
cd alpha-pm

# Install dependencies
uv sync

# Copy environment template
cp .env.example .env
# Edit .env with your credentials

# Start database and redis
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Run database migrations
uv run alembic upgrade head

# Start the trading engine
uv run alpha-pm
```

### Configuration

Create a `.env` file with:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://alphapm:alphapm@localhost:5432/alphapm

# Redis
REDIS_URL=redis://localhost:6379/0

# Polymarket (required)
POLYMARKET_PRIVATE_KEY=0x...
POLYMARKET_FUNDER=0x...  # If using proxy wallet

# Kalshi (optional, for Kalshi support)
KALSHI_API_KEY=...
KALSHI_PRIVATE_KEY_PATH=/path/to/kalshi.pem

# AI (for AI analyst)
ANTHROPIC_API_KEY=sk-ant-...

# Telegram (for alerts)
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...

# Risk settings
MAX_DAILY_LOSS_PCT=5
MAX_SINGLE_POSITION_PCT=10
MAX_DRAWDOWN_PCT=15
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      ALPHA-PM                            │
├─────────────────────────────────────────────────────────┤
│  SIGNAL LAYER                                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│  │Copy Monitor │ │ AI Analyst  │ │Arb Detector │        │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘        │
│         └───────────────┼───────────────┘                │
│                         ▼                                │
│              ┌─────────────────────┐                     │
│              │    ORCHESTRATOR     │                     │
│              └──────────┬──────────┘                     │
│                         ▼                                │
│              ┌─────────────────────┐                     │
│              │   RISK MANAGER      │ ← VETO POWER        │
│              └──────────┬──────────┘                     │
│                         ▼                                │
│  ┌─────────────────────────────────────────────────┐    │
│  │              EXECUTION LAYER                     │    │
│  │   ┌─────────────┐      ┌─────────────────┐      │    │
│  │   │   KALSHI    │      │   POLYMARKET    │      │    │
│  │   └─────────────┘      └─────────────────┘      │    │
│  └─────────────────────────────────────────────────┘    │
│                         ▼                                │
│  ┌─────────────────────────────────────────────────┐    │
│  │              DATA LAYER                          │    │
│  │        PostgreSQL  +  Redis                      │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## Strategy Allocation

| Strategy | Default Allocation | Description |
|----------|-------------------|-------------|
| AI Directional | 40% | Claude-analyzed market positions |
| Copy Trading | 35% | Follow profitable traders |
| Arbitrage | 15% | Cross-platform price discrepancies |
| Cash Reserve | 10% | Liquidity for opportunities |

## Risk Management

Alpha-PM includes multiple layers of risk protection:

| Safeguard | Threshold | Action |
|-----------|-----------|--------|
| Max single position | 10% | Block trade |
| Max daily loss | 5% | **HALT all trading** |
| Max drawdown | 15% | **HALT + manual review** |
| Consecutive losses | 5 trades | Pause 1 hour |
| API errors | 3 in 5 min | Halt platform |

## Commands

```bash
# Development
uv run alpha-pm                    # Start trading engine
uv run pytest                      # Run tests
uv run black src tests             # Format code
uv run mypy src                    # Type check

# Database
uv run alembic upgrade head        # Run migrations
uv run alembic downgrade -1        # Rollback last migration

# Docker
docker compose up -d               # Start all services
docker compose logs -f trading     # View logs
docker compose down                # Stop services
```

## Telegram Commands

Once running, control via Telegram:

- `/status` - Current positions and P&L
- `/balance` - Wallet balances
- `/trades` - Recent trades
- `/pause` - Pause trading
- `/resume` - Resume trading
- `/emergencystop` - Close all positions and halt

## Project Structure

```
alpha-pm/
├── src/
│   ├── agents/           # Trading agents
│   │   ├── orchestrator.py
│   │   ├── ai_analyst.py
│   │   ├── copy_monitor.py
│   │   ├── arb_detector.py
│   │   └── risk_manager.py
│   ├── execution/        # Platform executors
│   ├── data/             # Database models
│   ├── monitoring/       # Telegram & metrics
│   └── utils/            # Shared utilities
├── tests/
├── docs/
├── docker-compose.yml
└── pyproject.toml
```

## Development

### Setup

```bash
# Install with dev dependencies
uv sync --group dev

# Install pre-commit hooks
uv run pre-commit install

# Run tests with coverage
uv run pytest --cov=src --cov-report=html
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`uv run pytest`)
5. Format code (`uv run black src tests`)
6. Create a Pull Request

## Disclaimer

**This software is for educational and research purposes only.**

- Trading prediction markets involves substantial risk of financial loss
- Past performance does not guarantee future results
- Only trade with capital you can afford to lose
- The authors are not responsible for any financial losses

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Built with insights from analyzing 13+ prediction market trading systems. See [PROJECT_ANALYSIS.json](docs/PROJECT_ANALYSIS.json) for the full analysis.
