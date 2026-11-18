from dataclasses import dataclass, field
from collections.abc import Callable
from typing import Any


@dataclass(frozen=True)
class AgentTool:
    name: str
    description: str
    function: Callable[[dict[str, Any]], Any]
    input_schema: dict[str, Any] = field(default_factory=dict)

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.function(arguments)