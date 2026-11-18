import json
from dataclasses import dataclass
from typing import Callable
from src.core.issues import Issue

@dataclass(frozen=True)
class Stage:
    name: str
    run: Callable[..., list[Issue]]
    stop_on_error: bool = True

def run_stages(stages: list[Stage], **state) -> list[Issue]:
    issues: list[Issue] = []
    for stage in stages:
        found = stage.run(**state) or []
        issues += found
        if stage.stop_on_error and any(i.severity == 'error' for i in found):
            break
    return issues

def issues_for_ai(issues: list[Issue]) -> str:
    keep = ('code', 'part', 'site', 'message', 'hint')
    return json.dumps(
        [
            {k: getattr(i, k) for k in keep if getattr(i, k)}
            for i in issues if i.severity == 'error'
        ],
        indent=1,
    )