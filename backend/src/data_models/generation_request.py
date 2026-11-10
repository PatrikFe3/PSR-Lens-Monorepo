from dataclasses import dataclass

from src.data_models import generation_complexity
from src.printers.printer_profile import PrinterProfile


@dataclass
class GenerationRequest:
    prompt: str
    complexity: generation_complexity
    printer_profile: PrinterProfile