"""The AI design loop: ask the LLM for a spec, build it, feed failures back, retry."""
from pydantic import ValidationError
from src.ai.prompt import revision_prompt
from src.core.issues import DesignError, Issue
from src.core.spec import DesignSpec
from src.validation.pipeline import issues_for_ai


class NeedsInput(Exception):
    def __init__(self, spec):
        self.spec = spec
        self.questions = list(getattr(spec, 'questions', []) or [])
        super().__init__('; '.join(self.questions) or 'The design needs user input.')


class DesignAgent:
    def __init__(self, llm, spec_model, build, max_rounds=3, log=None):
        self._llm, self._model, self._build, self._max = llm, spec_model, build, max_rounds
        self._log = log or (lambda *_: None)
        self.history: list[dict] = []

    def _ask(self, prompt):
        raw = self._llm.generate(prompt, self._model.model_json_schema())
        try:
            return self._model.model_validate_json(raw), raw, []
        except ValidationError as err:
            return None, raw, [Issue('bad_spec', 'error', e['msg'], site='.'.join(map(str, e['loc'])),
                                     hint='Follow the JSON schema exactly.')
                               for e in err.errors()]

    def design(self, original_prompt, ask_user=True):
        prompt, issues = original_prompt, []
        for round_no in range(1, self._max + 1):
            spec, raw, issues = self._ask(prompt)
            if spec is not None:
                if ask_user and spec.questions:
                    raise NeedsInput(spec)
                design = DesignSpec.model_validate(spec.model_dump())
                try:
                    result = self._build(design)
                    self.history.append({'round': round_no, 'ok': True})
                    self._log(f'round {round_no}: design built')
                    return design, result
                except DesignError as err:
                    issues = err.issues
            self.history.append({'round': round_no, 'ok': False, 'issues': [i.code for i in issues]})
            self._log(f'round {round_no}: {len(issues)} issue(s): {", ".join(i.code for i in issues)}')
            prompt = revision_prompt(original_prompt, raw, issues_for_ai(issues))
        raise DesignError(issues)
