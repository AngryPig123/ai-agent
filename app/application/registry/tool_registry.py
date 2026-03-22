from app.application.tool.base_tool import BaseTool


class ToolRegistry:

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if not tool.name:
            raise ValueError("tool name은 비어 있을 수 없습니다.")
        if tool.name in self._tools:
            raise ValueError(f"이미 등록된 tool입니다: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        return self._tools[name]

    def list_tools(self) -> list[BaseTool]:
        return list(self._tools.values())
