# Decides what we are going to do with request.
from src.data_models.prompt_interpretation import PromptInterpretation
from src.artificial_intelligence.agents.tool_call import ToolCall

class GenerationPlanner:

    def create_plan(
            self,
            interpretation: PromptInterpretation,
    ) -> ToolCall:
        pass