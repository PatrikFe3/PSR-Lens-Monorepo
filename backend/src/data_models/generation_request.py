from dataclasses import dataclass

from src.data_models.generation_complexity import GenerationComplexity
from src.printers.printer_profile import PrinterProfile


@dataclass
class GenerationRequest:
    prompt: str
    complexity: GenerationComplexity
    printer_profile: PrinterProfile