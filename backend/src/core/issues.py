from dataclasses import asdict, dataclass, field
from typing import Literal


@dataclass(frozen=True)
class Issue:
    code: str
    severity: Literal['error', 'warning']
    message: str
    part: str | None = None
    site: str | None = None
    hint: str | None = None
    data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def has_errors(issues: list[Issue]) -> bool:
    return any(i.severity == 'error' for i in issues)


class DesignError(Exception):
    def __init__(self, issues: list[Issue]):
        self.issues = list(issues)
        super().__init__('; '.join(i.message for i in self.issues))