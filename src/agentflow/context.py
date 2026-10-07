from dataclasses import dataclass, field
from typing import Any


@dataclass
class Context:
    task: str
    state: dict[str, Any] = field(default_factory=dict)
    steps: int = 0

    def set(self, key: str, value: Any) -> None:
        self.state[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)
