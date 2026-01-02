"""Base executor class for platform-specific trading."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class OrderStatus(Enum):
    """Order status enum."""

    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class OrderSide(Enum):
    """Order side enum."""

    BUY = "buy"
    SELL = "sell"


@dataclass
class Order:
    """Order representation."""

    id: str
    market_id: str
    side: OrderSide
    price: Decimal
    size: Decimal
    status: OrderStatus
    filled_size: Decimal = Decimal("0")
    filled_price: Decimal | None = None


@dataclass
class Position:
    """Position representation."""

    market_id: str
    side: OrderSide
    size: Decimal
    avg_entry_price: Decimal
    current_price: Decimal | None = None
    unrealized_pnl: Decimal | None = None


@dataclass
class Balance:
    """Account balance."""

    available: Decimal
    locked: Decimal  # In pending orders
    total: Decimal


class BaseExecutor(ABC):
    """Base class for platform executors.

    Each platform (Kalshi, Polymarket) implements this interface.
    """

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the platform."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the platform."""
        pass

    @abstractmethod
    async def get_balance(self) -> Balance:
        """Get account balance."""
        pass

    @abstractmethod
    async def get_positions(self) -> list[Position]:
        """Get all open positions."""
        pass

    @abstractmethod
    async def place_order(
        self,
        market_id: str,
        side: OrderSide,
        size: Decimal,
        price: Decimal,
    ) -> Order:
        """Place an order."""
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order. Returns True if successful."""
        pass

    @abstractmethod
    async def get_order(self, order_id: str) -> Order:
        """Get order status."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if connection is healthy."""
        pass
