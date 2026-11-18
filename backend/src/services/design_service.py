"""One entry point for the new system, used by the API and the demo."""
import uuid
from pathlib import Path

from src.ai.orchestrator import DesignAgent
from src.ai.prompt import catalog_brief, design_prompt
from src.ai.schema import design_spec_model
from src.catalog.loader import Catalog, load_catalog
from src.core.settings import get_settings
from src.core.spec import DesignSpec
from src.geometry.kernel import kernel, set_kernel
from src.pipeline.build import BuildResult, build_design, validate_design
from src.templates.registry import default_templates


class DesignService:
    def __init__(self, catalog: Catalog | None = None, templates=None, output_dir=None,
                 printer: str | None = None, material: str | None = None, kernel_name: str | None = None):
        settings = get_settings()
        if kernel_name:
            set_kernel(kernel_name)
        self.kernel = kernel()
        self.catalog = catalog or load_catalog(settings.catalog_dir)
        self.templates = templates or default_templates()
        self.output_dir = Path(output_dir or settings.output_dir)
        self.printer_id = printer or settings.default_printer
        self.material_id = material or settings.default_material

    def _profiles(self, printer=None, material=None):
        return (self.catalog.printers.get(printer or self.printer_id),
                self.catalog.materials.get(material or self.material_id))

    @staticmethod
    def parse_spec(spec) -> DesignSpec:
        return spec if isinstance(spec, DesignSpec) else DesignSpec.model_validate(spec)

    def check(self, spec, printer=None, material=None):
        """Run every check without writing files. Returns the list of (warning) issues."""
        p, m = self._profiles(printer, material)
        return validate_design(self.parse_spec(spec), self.catalog, self.templates, p, m)[3]

    def build(self, spec, design_id: str | None = None, printer=None, material=None) -> BuildResult:
        p, m = self._profiles(printer, material)
        design_id = design_id or uuid.uuid4().hex[:10]
        return build_design(self.parse_spec(spec), self.catalog, self.templates, p, m,
                            self.output_dir / design_id, design_id)

    def agent(self, llm, printer=None, material=None, max_rounds=3, log=None) -> DesignAgent:
        model = design_spec_model(self.catalog, self.templates)
        return DesignAgent(llm, model, lambda spec: self.build(spec, printer=printer, material=material),
                           max_rounds=max_rounds, log=log)

    def prompt_for(self, request: str, printer=None) -> str:
        p, _ = self._profiles(printer)
        return design_prompt(request, p, catalog_brief(self.catalog, self.templates))

    def design_from_prompt(self, request: str, llm=None, ask_user=True, printer=None, material=None,
                           log=None):
        """Natural language -> LLM spec -> checked, built design. Returns (DesignSpec, BuildResult)."""
        if llm is None:
            from src.ai.ollama_client import OllamaClient
            llm = OllamaClient()
        agent = self.agent(llm, printer, material, log=log)
        return agent.design(self.prompt_for(request, printer), ask_user=ask_user)
