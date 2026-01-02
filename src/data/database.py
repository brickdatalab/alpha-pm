"""MongoDB database client using motor (async driver)."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import structlog

from src.config import settings

logger = structlog.get_logger(__name__)

# Global client instance
_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_db() -> AsyncIOMotorDatabase:
    """
    Connect to MongoDB Atlas.

    Returns the database instance for use throughout the application.
    """
    global _client, _db

    if _db is not None:
        return _db

    logger.info("mongodb_connecting", uri=settings.mongodb_uri[:30] + "...")

    _client = AsyncIOMotorClient(settings.mongodb_uri)

    # Extract database name from URI or use default
    # URI format: mongodb+srv://user:pass@cluster.mongodb.net/database?options
    db_name = "alphapm"
    if "/" in settings.mongodb_uri:
        # Try to extract database name from URI
        uri_parts = settings.mongodb_uri.split("/")
        if len(uri_parts) > 3:
            db_part = uri_parts[-1].split("?")[0]
            if db_part:
                db_name = db_part

    _db = _client[db_name]

    # Verify connection
    await _client.admin.command("ping")
    logger.info("mongodb_connected", database=db_name)

    # Create indexes for common queries
    await _create_indexes()

    return _db


async def disconnect_db() -> None:
    """Disconnect from MongoDB."""
    global _client, _db

    if _client is not None:
        _client.close()
        _client = None
        _db = None
        logger.info("mongodb_disconnected")


async def get_db() -> AsyncIOMotorDatabase:
    """Get the database instance, connecting if necessary."""
    if _db is None:
        return await connect_db()
    return _db


async def _create_indexes() -> None:
    """Create indexes for better query performance."""
    if _db is None:
        return

    # Trades collection indexes
    await _db.trades.create_index("created_at")
    await _db.trades.create_index("platform")
    await _db.trades.create_index("market_id")
    await _db.trades.create_index("status")
    await _db.trades.create_index([("platform", 1), ("market_id", 1)])

    # Positions collection indexes
    await _db.positions.create_index([("platform", 1), ("market_id", 1)], unique=True)

    # Signals collection indexes
    await _db.signals.create_index("created_at")
    await _db.signals.create_index("source")
    await _db.signals.create_index("acted_on")

    # Metrics collection indexes
    await _db.metrics_daily.create_index("date", unique=True)

    # Alerts collection indexes
    await _db.alerts.create_index("created_at")
    await _db.alerts.create_index("level")
    await _db.alerts.create_index("acknowledged")

    # Tracked traders collection indexes
    await _db.tracked_traders.create_index("address", unique=True)
    await _db.tracked_traders.create_index("platform")
    await _db.tracked_traders.create_index("active")

    logger.info("mongodb_indexes_created")


# Collection name constants
class Collections:
    """MongoDB collection names."""

    TRADES = "trades"
    POSITIONS = "positions"
    SIGNALS = "signals"
    METRICS_DAILY = "metrics_daily"
    ALERTS = "alerts"
    TRACKED_TRADERS = "tracked_traders"
