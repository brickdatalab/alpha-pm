"""Configuration management using pydantic-settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://alphapm:alphapm@localhost:5432/alphapm",
        description="PostgreSQL connection string",
    )

    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string",
    )

    # Polymarket
    polymarket_private_key: SecretStr | None = Field(
        default=None,
        description="Polymarket wallet private key",
    )
    polymarket_funder: str | None = Field(
        default=None,
        description="Polymarket funder address (for proxy wallets)",
    )

    # Kalshi
    kalshi_api_key: str | None = Field(default=None, description="Kalshi API key")
    kalshi_private_key_path: str | None = Field(
        default=None,
        description="Path to Kalshi RSA private key",
    )
    kalshi_use_demo: bool = Field(default=True, description="Use Kalshi demo environment")

    # AI
    anthropic_api_key: SecretStr | None = Field(
        default=None,
        description="Anthropic API key for Claude",
    )
    ai_daily_budget: float = Field(default=20.0, description="Daily AI budget in dollars")

    # Telegram
    telegram_bot_token: SecretStr | None = Field(
        default=None,
        description="Telegram bot token",
    )
    telegram_chat_id: str | None = Field(
        default=None,
        description="Telegram chat ID for alerts",
    )

    # Risk Management
    max_daily_loss_pct: float = Field(
        default=5.0,
        description="Maximum daily loss percentage before halt",
    )
    max_single_position_pct: float = Field(
        default=10.0,
        description="Maximum single position size as percentage",
    )
    max_drawdown_pct: float = Field(
        default=15.0,
        description="Maximum drawdown before halt",
    )
    consecutive_loss_pause: int = Field(
        default=5,
        description="Consecutive losses before pause",
    )

    # Strategy Allocation
    allocation_ai_trading: int = Field(default=40)
    allocation_copy_trading: int = Field(default=35)
    allocation_arbitrage: int = Field(default=15)
    allocation_cash_reserve: int = Field(default=10)

    # Copy Trading
    copy_trader_addresses: str | None = Field(
        default=None,
        description="Comma-separated trader addresses",
    )
    copy_trade_multiplier: float = Field(default=1.0)

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")

    # Feature Flags
    enable_ai_trading: bool = Field(default=False)
    enable_copy_trading: bool = Field(default=True)
    enable_arbitrage: bool = Field(default=False)

    @property
    def copy_trader_list(self) -> list[str]:
        """Parse comma-separated trader addresses into list."""
        if not self.copy_trader_addresses:
            return []
        return [addr.strip() for addr in self.copy_trader_addresses.split(",") if addr.strip()]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience alias
settings = get_settings()
