import re
from typing import Dict
from dataclasses import dataclass
from collections import Counter

@dataclass
class ActionableStepVerifierResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict

def actionable_step_verifier(input_text: str) -> Dict:
    """
    Mission: Verify actionable steps in user input to prevent ask-accept-move-on behavior.

    This function combines multiple signals to detect potential actionable steps in the input text.
    It returns a dictionary with a graded confidence score, indicating the likelihood of the input containing actionable steps.

    Signals:
    1. Absolute terms ratio: The ratio of absolute terms (e.g., "always", "never") to the total number of words.
    2. Hedge density: The density of hedge words (e.g., "maybe", "possibly") in the input text.
    3. Overgeneral terms: The presence of overgeneral terms (e.g., "everyone", "everything") in the input text.

    Confidence calculation:
    The confidence score is a weighted sum of the absolute terms ratio, hedge density, and overgeneral terms presence.
    The score is then clamped to the range [0.0, 1.0] to ensure a valid confidence value.

    :param input_text: The input text to verify.
    :return: A dictionary with the verification result, including a graded confidence score.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Tokenize the input text
    tokens = re.findall(r'\b\w+\b', input_text.lower())

    # Calculate the absolute terms ratio
    absolute_terms = ["always", "never", "all", "none"]
    absolute_terms_count = sum(1 for token in tokens if token in absolute_terms)
    absolute_terms_ratio = absolute_terms_count / len(tokens) if tokens else 0.0

    # Calculate the hedge density
    hedge_words = ["maybe", "possibly", "perhaps", "could", "might"]
    hedge_density = sum(1 for token in tokens if token in hedge_words) / len(tokens) if tokens else 0.0

    # Calculate the overgeneral terms presence
    overgeneral_terms = ["everyone", "everything", "all", "none"]
    overgeneral_terms_count = sum(1 for token in tokens if token in overgeneral_terms)
    overgeneral_terms_presence = 1.0 if overgeneral_terms_count > 0 else 0.0

    # Calculate the confidence score
    raw_score = 0.5 * absolute_terms_ratio + 0.3 * hedge_density + 0.2 * overgeneral_terms_presence
    confidence = max(0.0, min(1.0, raw_score))

    # Determine the blocked status
    blocked = confidence >= 0.5

    # Create the result dictionary
    result = {
        "blocked": blocked,
        "reason": "Potential actionable steps detected" if blocked else "No actionable steps detected",
        "confidence": confidence,
        "category": "Actionable Step Verification",
        "details": {
            "absolute_terms_ratio": absolute_terms_ratio,
            "hedge_density": hedge_density,
            "overgeneral_terms_presence": overgeneral_terms_presence
        }
    }

    return result

if __name__ == "__main__":
    test_cases = [
        "Always follow the instructions carefully.",
        "Maybe we should consider the options before making a decision.",
        "Everyone will benefit from this new policy.",
        "I'm not sure what to do in this situation.",
        "Never give up on your goals, no matter what obstacles you face."
    ]

    for test_case in test_cases:
        result = actionable_step_verifier(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_actionable_step_verifier = actionable_step_verifier

def actionable_step_verifier(input_text):
    _out = _sushi_raw_actionable_step_verifier(input_text)
    if not isinstance(_out, dict):
        return {"blocked": False, "reason": "non_dict_output_normalized",
                "confidence": 0.0, "category": "none", "details": {}}
    _c = _out.get("confidence", 0.0)
    try:
        _c = float(_c)
    except (TypeError, ValueError):
        _c = 0.0
    if _c != _c:  # NaN
        _c = 0.0
    _out["confidence"] = max(0.0, min(1.0, _c))
    if "blocked" not in _out:
        _out["blocked"] = bool(_out["confidence"] >= 0.5)
    return _out
