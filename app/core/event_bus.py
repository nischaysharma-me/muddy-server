"""Asynchronous In-Memory Event Bus for Telemetry and Pub/Sub."""

import asyncio
from collections import defaultdict
from typing import Any, Callable, Coroutine, Dict, List, Optional
from app.core.logging import logger

EventHandler = Callable[[str, Dict[str, Any]], Coroutine[Any, Any, None]]


class EventBus:
    """Asynchronous Event Bus for broadcasting pipeline and job lifecycle events."""

    def __init__(self):
        self._subscribers: Dict[str, List[EventHandler]] = defaultdict(list)
        self._global_subscribers: List[EventHandler] = []

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribes an async handler to a specific event type."""
        self._subscribers[event_type].append(handler)

    def subscribe_all(self, handler: EventHandler) -> None:
        """Subscribes an async handler to all event types (e.g. WebSocket broadcaster)."""
        self._global_subscribers.append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Unsubscribes an async handler from an event type."""
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)

    async def emit(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Emits an event asynchronously to all subscribed listeners."""
        handlers = list(self._subscribers.get(event_type, [])) + list(self._global_subscribers)
        if not handlers:
            return

        tasks = []
        for handler in handlers:
            try:
                tasks.append(asyncio.create_task(handler(event_type, payload)))
            except Exception as e:
                logger.error(f"[EventBus] Error creating task for handler {handler}: {e}")

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in results:
                if isinstance(res, Exception):
                    logger.error(f"[EventBus] Subscriber error during event '{event_type}': {res}")


# Global EventBus Singleton
event_bus = EventBus()
