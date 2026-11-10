from src.artificial_intelligence.agents.tool import AgentTool

class ToolRegistry:

    def __init__(self):
        self._tools: dict[str, AgentTool] = {}

    def register(self, tool: AgentTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered.")

        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> AgentTool:
        tool = self._tools.get(name)

        if tool is None:
            raise ValueError(f"Tool '{name}' is not registered.")

        return tool

    def get_available_tools(self) -> list[AgentTool]:
        return list(self._tools.values())