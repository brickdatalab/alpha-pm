"""Execution layer for platform-specific trading."""

from src.execution.base import BaseExecutor, OrderRequest, OrderResult, OrderStatus
from src.execution.polymarket import PolymarketExecutor
from src.execution.kalshi import KalshiExecutor

__all__ = [
    "BaseExecutor",
    "OrderRequest",
    "OrderResult",
    "OrderStatus",
    "PolymarketExecutor",
    "KalshiExecutor",
]
