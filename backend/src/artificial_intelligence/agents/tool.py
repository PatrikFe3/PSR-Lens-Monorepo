from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class AgentTool:
    name: str
    description: str
    function: Callable[[dict[str, Any]], Any]
    input_schema: dict[str, Any] = field(default_factory=dict)

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.function(arguments)