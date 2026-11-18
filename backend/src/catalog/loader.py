from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from src.catalog.models import HardwareSpec, InterfaceSpec
from src.catalog.registry import Registry
from src.manufacturing.profiles import MaterialSpec, PrinterSpec


@dataclass(frozen=True)
class Catalog:
    hardware: Registry[HardwareSpec]
    interfaces: Registry[InterfaceSpec]
    printers: Registry[PrinterSpec]
    materials: Registry[MaterialSpec]

    def summary(self) -> dict[str, list[str]]:
        return {
            'hardware': self.hardware.ids(),
            'interfaces': self.interfaces.ids(),
            'printers': self.printers.ids(),
            'materials': self.materials.ids(),
        }


def load_catalog(root: Path | str | None = None) -> Catalog:
    """Load ``catalogs/{hardware,interfaces,printers,materials}/*.yaml``."""
    if root is None:
        from src.core.settings import get_settings
        root = get_settings().catalog_dir
    root = Path(root)
    return Catalog(
        hardware=Registry(HardwareSpec, root / 'hardware'),
        interfaces=Registry(InterfaceSpec, root / 'interfaces'),
        printers=Registry(PrinterSpec, root / 'printers'),
        materials=Registry(MaterialSpec, root / 'materials'),
    )


@lru_cache(maxsize=4)
def cached_catalog(root: str | None = None) -> Catalog:
    return load_catalog(root)
