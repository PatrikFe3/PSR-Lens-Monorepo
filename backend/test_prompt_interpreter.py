from src.printers.printer_profile import PrinterProfile
from src.artificial_intelligence.ollama_client import OllamaClient
from src.artificial_intelligence.prompt_interpreter import PromptInterpreter
from src.data_models.generation_request import GenerationRequest
from src.data_models.generation_complexity import GenerationComplexity

client = OllamaClient()
interpreter = PromptInterpreter(client)

printer_profile = PrinterProfile(
    name="Ender 6",
    build_volume_x=250,
    build_volume_y=250,
    build_volume_z=400,
)

request = GenerationRequest(
    prompt="Create a simple LEGO robot.",
    complexity=GenerationComplexity.LOW,
    printer_profile=printer_profile,
)

result = interpreter.interpret(request)

print(result)
print(result.assembly_plan.instructions)