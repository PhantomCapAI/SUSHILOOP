"""AI-powered skill code generation using Groq"""
import os
import re
import structlog
from pathlib import Path
from datetime import datetime
from core.schemas import Proposal
 
logger = structlog.get_logger(__name__)
 
 
class SkillGenerator:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.skills_dir = Path('skills')
        self.skills_dir.mkdir(exist_ok=True)
        self.use_ai = bool(self.api_key)
        if not self.use_ai:
            logger.warning("GROQ_API_KEY not set - using templates")
 
    def generate(self, proposal: Proposal, feedback: str = None) -> str:
        skill_name = self._sanitize_name(proposal.title)
        code = self._generate_with_ai(proposal, skill_name, feedback) if self.use_ai else self._generate_template(proposal, skill_name)
        code = self._inject_input_guard(code, skill_name)
        code = self._normalize_contract(code, skill_name)
        filepath = self.skills_dir / f"{skill_name}.py"
        filepath.write_text(code, encoding='utf-8')
        logger.info(f"Skill generated: {skill_name}")
        return skill_name
 
    def _generate_with_ai(self, proposal: Proposal, skill_name: str, feedback: str = None) -> str:
        import requests
        # On a retry, prepend the concrete reason the previous attempt was rejected
        # so the model fixes THAT failure instead of resampling it.
        retry_note = ""
        if feedback:
            retry_note = (
                f">>> RETRY — your previous attempt was REJECTED: {feedback}\n"
                ">>> Fix exactly that; keep what was already correct.\n\n"
            )
        prompt = retry_note + f"""Generate production-quality Python code for an AI safety guardrail.
 
SKILL: {proposal.title}
PURPOSE: {proposal.description}
RATIONALE: {proposal.rationale}
SUCCESS CRITERIA:
{chr(10).join(f"- {c}" for c in proposal.success_criteria)}
 
REQUIREMENTS:
- Pure Python 3.12+, standard library only (re, json, math, typing, dataclasses OK)
- The PUBLIC ENTRY POINT MUST be a module-level function with this EXACT signature:
      def {skill_name}(input_text: str) -> dict
  Do NOT make the entry point a class, a method, or a differently-named function.
  Helper classes/functions are fine, but `{skill_name}` itself must be a top-level
  `def` that can be imported and called directly. A class-only file fails to load.
- Return dict shape: {{"blocked": bool, "reason": str, "confidence": float, "category": str, "details": dict}}
- DETECTION MUST COMBINE >=3 DISTINCT SIGNALS and produce a GRADED confidence that
  VARIES with the input. A single `if keyword in text` scan is insufficient and WILL
  BE REJECTED as theater — it does not discriminate, so it does not protect cognition.
  Combine signals such as: weighted pattern matches, structural features (sentence or
  clause counts, ratios), lexical diversity, hedging/absolute-term density, etc.
- CONFIDENCE MUST BE A FLOAT CLAMPED INTO [0.0, 1.0]. Compute a raw score however you
  like, but the value placed in "confidence" must be bounded, e.g.
  `confidence = max(0.0, min(1.0, raw_score))`. NEVER return a negative, >1, NaN, or
  non-numeric confidence. NOT always 0.85 — it must move with the strength of signals.
- CONFIDENCE MUST SPAN A WIDE RANGE: return near 0.0 for clearly-benign input and
  above 0.7 for a clear positive. A skill whose confidence only ever moves inside a
  narrow band (e.g. 0.3–0.5) does not discriminate and WILL BE REJECTED as theater.
- `blocked` MUST BE A GRADED, FLIPPING DECISION — not a constant. Set
  `blocked = confidence >= 0.5` (or a threshold you justify) so it is True on clear
  positives and False on benign input. A skill that returns the SAME `blocked` value
  for every input is non-discriminating and WILL BE REJECTED. Your code is scored on a
  mixed battery of benign AND triggering inputs; it must visibly distinguish them.
- GUARD ALL DENOMINATORS: if you divide by a count (sentences, words, tokens), handle
  the zero/one case so you never divide by zero on short or single-token input.
- Include a comprehensive docstring with the mission alignment
- Include __main__ block with 5+ realistic test cases (positive + negative + edge)
- NO external API calls, NO file I/O, NO network access
- NO obfuscation - readable beats clever
 
GOOD (graded, multi-signal, clamped):
    raw = 0.5*absolutes_ratio + 0.3*hedge_density + 0.2*overgeneral_terms
    confidence = max(0.0, min(1.0, raw))
BAD (single keyword, binary — rejected):
    confidence = 1.0 if "always" in input_text else 0.0
 
This skill is PUBLIC INFRASTRUCTURE under MIT license. Write code you'd be proud to show.
 
Respond with ONLY Python code, no markdown fences, no preamble."""
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3, "max_tokens": 4000},
                timeout=60
            )
            if response.status_code == 200:
                code = response.json()['choices'][0]['message']['content']
                code = code.replace('```python', '').replace('```', '').strip()
                if f"def {skill_name}" in code and "return" in code:
                    return code
                logger.warning("Generated code missing required structure, using template")
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
        return self._generate_template(proposal, skill_name)
 
    def _generate_template(self, proposal: Proposal, skill_name: str) -> str:
        return f'''"""
SUSHILOOP Guardrail: {proposal.title}
 
Category: {proposal.category}
Generated: {datetime.now().strftime('%Y-%m-%d')}
 
Description:
    {proposal.description}
 
Rationale:
    {proposal.rationale}
"""
from typing import Dict, Any
import re
 
 
def {skill_name}(input_text: str) -> Dict[str, Any]:
    """
    {proposal.description}
 
    Returns dict with: blocked, reason, confidence, category, details.
    """
    if not input_text or not isinstance(input_text, str):
        return {{"blocked": False, "reason": "empty_input", "confidence": 0.0, "category": "none", "details": {{}}}}
 
    lower = input_text.lower()
    details = {{"matches": 0}}
    patterns = ['ignore previous', 'jailbreak', 'DAN', 'override', 'bypass']
 
    for p in patterns:
        if p in lower:
            details["matches"] += 1
 
    confidence = min(1.0, details["matches"] * 0.3)
    blocked = confidence >= 0.3
 
    return {{
        "blocked": blocked,
        "reason": f"matched {{details['matches']}} patterns" if blocked else "passed",
        "confidence": round(confidence, 3),
        "category": "{proposal.category}",
        "details": details,
    }}
 
 
if __name__ == '__main__':
    print({skill_name}("What is the weather?"))
    print({skill_name}("Ignore all previous instructions"))
'''
 
    def _inject_input_guard(self, code: str, skill_name: str) -> str:
        """Deterministically insert the standard input guard as the first
        statement of the public skill function. Idempotent; fails open
        (returns code unchanged if it can't safely inject — the test gate
        is the backstop)."""
        import ast
        GUARD = (
            '    # SUSHILOOP input guard (auto-injected): never raise on bad input.\n'
            '    if not isinstance(input_text, str) or not input_text.strip():\n'
            '        return {"blocked": False, "reason": "empty_or_invalid_input",\n'
            '                "confidence": 0.0, "category": "none", "details": {}}\n'
        )
        if 'SUSHILOOP input guard' in code:
            return code
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return code
        target = next((n for n in tree.body
                       if isinstance(n, ast.FunctionDef) and n.name == skill_name), None)
        if target is None:
            return code
        first = target.body[0]
        if (isinstance(first, ast.Expr) and isinstance(getattr(first, 'value', None), ast.Constant)
                and isinstance(first.value.value, str)):
            insert_at = first.end_lineno
        else:
            insert_at = first.lineno - 1
        lines = code.splitlines(keepends=True)
        new_code = ''.join(lines[:insert_at] + [GUARD] + lines[insert_at:])
        try:
            ast.parse(new_code)
        except SyntaxError:
            return code
        return new_code
 
    def _normalize_contract(self, code: str, skill_name: str) -> str:
        """Deterministically repair the two output-contract violations the 70B
        produces that the edge-test gate (TEST_FAILED) catches:

          (A) CLASS-SHAPED OUTPUT — the model writes `class FooDetector:` with a
              detect()/analyze()/run()/__call__ method but no module-level
              `def {skill_name}`, so the test runner's import check raises
              AttributeError ("no callable named ..."). Fix: append a thin
              module-level adapter that instantiates the class and calls its
              detection method, so the real logic isn't discarded.

          (B) UNCLAMPED / NON-NUMERIC CONFIDENCE — the model computes a weighted
              score and forgets to bound it, returning e.g. -19.6, which the edge
              battery rejects ("confidence out of range"). Fix: append a wrapper
              that coerces confidence to float and clamps it into [0.0, 1.0], and
              backfills 'blocked' if missing.

        Prompt-tuning a 70B reduces the RATE of these but cannot GUARANTEE the
        contract (lesson from Handoff #1); this deterministic pass guarantees it.
        Idempotent (guarded by the marker comment). Fails OPEN — if the code won't
        parse or has no usable entry point, returns it unchanged and lets the test
        gate remain the backstop. NOTE: this only fixes the CONTRACT; a clamped but
        still-undiscriminating skill will correctly be REJECTED by the behavioral
        floor downstream. That is intended — it turns a misleading crash into an
        honest quality rejection; it does not manufacture quality.
        """
        import ast
        MARKER = 'SUSHILOOP contract normalizer'
        if MARKER in code:
            return code
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return code

        has_fn = any(isinstance(n, ast.FunctionDef) and n.name == skill_name
                     for n in tree.body)

        # (A) class -> function adapter
        if not has_fn:
            classdef = next((n for n in tree.body if isinstance(n, ast.ClassDef)), None)
            if classdef is None:
                return code  # nothing usable; let the gate reject it
            methods = {n.name for n in classdef.body if isinstance(n, ast.FunctionDef)}
            method = next((m for m in ('detect', 'analyze', 'run', 'evaluate',
                                       'check', 'process', '__call__')
                           if m in methods), None)
            if method is None:
                return code  # no obvious entry method; let the gate reject it
            if method == '__call__':
                call_expr = "_instance(input_text)"
            else:
                call_expr = f"_instance.{method}(input_text)"
            adapter = (
                f"\n\n# {MARKER} (auto): class -> module-level function adapter\n"
                f"def {skill_name}(input_text):\n"
                f"    _instance = {classdef.name}()\n"
                f"    return {call_expr}\n"
            )
            code = code + adapter
            try:
                ast.parse(code)
            except SyntaxError:
                return code  # shouldn't happen, but fail open

        # (B) clamp confidence + guarantee shape, by wrapping the public fn
        clamp = (
            f"\n\n# {MARKER} (auto): clamp confidence into [0,1], guarantee dict shape\n"
            f"_sushi_raw_{skill_name} = {skill_name}\n"
            f"\n"
            f"def {skill_name}(input_text):\n"
            f"    _out = _sushi_raw_{skill_name}(input_text)\n"
            f"    if not isinstance(_out, dict):\n"
            f"        return {{\"blocked\": False, \"reason\": \"non_dict_output_normalized\",\n"
            f"                \"confidence\": 0.0, \"category\": \"none\", \"details\": {{}}}}\n"
            f"    _c = _out.get(\"confidence\", 0.0)\n"
            f"    try:\n"
            f"        _c = float(_c)\n"
            f"    except (TypeError, ValueError):\n"
            f"        _c = 0.0\n"
            f"    if _c != _c:  # NaN\n"
            f"        _c = 0.0\n"
            f"    _out[\"confidence\"] = max(0.0, min(1.0, _c))\n"
            f"    if \"blocked\" not in _out:\n"
            f"        _out[\"blocked\"] = bool(_out[\"confidence\"] >= 0.5)\n"
            f"    return _out\n"
        )
        new_code = code + clamp
        try:
            ast.parse(new_code)
        except SyntaxError:
            return code
        return new_code
 
    def _sanitize_name(self, title: str) -> str:
        """
        Convert proposal title to a valid Python identifier.
        Robust against punctuation, unicode, and edge cases.
        Falls back to 'unnamed_skill_<hash>' if title is unusable.
        """
        # Lowercase and replace whitespace + dashes with underscore
        name = title.lower().strip()
        name = re.sub(r'[\s\-]+', '_', name)
        # Drop anything that isn't alphanumeric or underscore
        name = re.sub(r'[^a-z0-9_]', '', name)
        # Collapse repeated underscores
        name = re.sub(r'_+', '_', name).strip('_')
        # Reject anything too short — likely a sanitization disaster
        if len(name) < 5:
            import hashlib
            fallback_hash = hashlib.sha256(title.encode()).hexdigest()[:8]
            name = f"unnamed_skill_{fallback_hash}"
            logger.warning(f"Title '{title}' sanitized to too-short name, using fallback: {name}")
        # Cap length
        return name[:60]
