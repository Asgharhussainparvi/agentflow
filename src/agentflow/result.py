from dataclasses import dataclass, field
from typing import Any


@dataclass
class Result:
    output: Any
    success: bool = True
    steps: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
