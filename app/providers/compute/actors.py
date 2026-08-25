"""Ray Distributed Actors Definitions."""

from typing import Any, Callable, Dict


class GenericWorkerActor:
    """Ray Actor executing heavy CPU/GPU tasks with isolated state."""

    def __init__(self, actor_id: str):
        self.actor_id = actor_id

    def execute_task(self, func_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "actor_id": self.actor_id,
            "status": "completed",
            "func_name": func_name,
            "result": payload,
        }
