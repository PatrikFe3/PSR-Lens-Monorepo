from src.artificial_intelligence.ollama_client import OllamaClient
from src.artificial_intelligence.prompt_interpreter import PromptInterpreter
from src.artificial_intelligence.agents.generation_agent import GenerationAgent

from src.data_models.generation_request import GenerationRequest
from src.data_models.generation_complexity import GenerationComplexity

from src.printers.printer_profile import (
    PrinterProfile,
    validate_model_fits,
)

from src.services.export_service import export_stl
from src.config.paths import MODELS_DIR

printer = PrinterProfile(
    name="Creality Ender 6",
    build_volume_x=250.0,
    build_volume_y=250.0,
    build_volume_z=400.0,
    nozzle_diameter=0.4,
)

request = GenerationRequest(
    prompt="Create a simple Lego robot with a body, head and arms.",
    complexity=GenerationComplexity.LOW,
    printer_profile=printer,
)

ollama_client = OllamaClient()
prompt_interpreter = PromptInterpreter(ollama_client)

generation_agent = GenerationAgent(
    tool_registry=None,
    decision_function=None,
    prompt_interpreter=prompt_interpreter,
)

result = generation_agent.generate(request)

bounding_box = result.model.BoundingBox()

length = bounding_box.xlen
width = bounding_box.ylen
height = bounding_box.zlen

print("\n--- GENERATED MODEL ---")
print(f"Components: {len(result.components)}")
print(f"Length: {length:.2f} mm")
print(f"Width: {width:.2f} mm")
print(f"Height: {height:.2f} mm")

validate_model_fits(
    length=length,
    width=width,
    height=height,
    printer=printer,
)

output_path = MODELS_DIR / "generated_robot.stl"

export_stl(
    model=result.model,
    output_path=output_path,
)

print(f"\nSTL successfully exported to: {output_path}")