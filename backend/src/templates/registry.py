from src.templates.base import Template
from src.templates.parts.brick import Brick
from src.templates.parts.enclosure import Enclosure
from src.templates.parts.link import Link
from src.templates.parts.pedestial import Pedestal
from src.templates.parts.sensor_mount import SensorMount


def default_templates() -> dict[str, Template]:
    """All part templates the backend (and the AI) may use, keyed by name."""
    templates = [Pedestal(), Link(), Enclosure(), SensorMount(), Brick()]
    return {t.name: t for t in templates}
