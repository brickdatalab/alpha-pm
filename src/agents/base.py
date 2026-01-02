"""Base agent class that all trading agents inherit from."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import structlog

log = structlog.get_logger()


class AgentStatus(Enum):
    """Agent status enum."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class HealthStatus:
    """Health check result."""

    healthy: bool
    status: AgentStatus
    message: str
    last_check: datetime
    details: dict[str, Any] | None = None


class BaseAgent(ABC):
    """Base class for all trading agents.

    All agents must implement:
    - start(): Begin processing
    - stop(): Graceful shutdown
    - health_check(): Return health status
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.status = AgentStatus.STOPPED
        self._log = log.bind(agent=name)

    @abstractmethod
    async def start(self) -> None:
        """Start the agent. Must be implemented by subclasses."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the agent gracefully. Must be implemented by subclasses."""
        pass

    @abstractmethod
    async def health_check(self) -> HealthStatus:
        """Check agent health. Must be implemented by subclasses."""
        pass

    async def pause(self) -> None:
        """Pause the agent (stop generating signals but keep running)."""
        self._log.info("Pausing agent")
        self.status = AgentStatus.PAUSED

    async def resume(self) -> None:
        """Resume a paused agent."""
        if self.status == AgentStatus.PAUSED:
            self._log.info("Resuming agent")
            self.status = AgentStatus.RUNNING

    def is_running(self) -> bool:
        """Check if agent is running."""
        return self.status == AgentStatus.RUNNING

    def is_healthy(self) -> bool:
        """Quick check if agent is in a healthy state."""
        return self.status in (AgentStatus.RUNNING, AgentStatus.PAUSED)
