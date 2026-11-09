from dataclasses import dataclass

from data_models import generation_complexity
from printers.printer_profile import PrinterProfile


@dataclass
class GenerationRequest:
    prompt: str
    complexity: generation_complexity
    printer_profile: PrinterProfile