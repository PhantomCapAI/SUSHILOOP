import re
from typing import Dict
from dataclasses import dataclass

@dataclass
class DetectionResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict[str, str]

def pasted_credential_catcher(input_text: str) -> Dict[str, str]:
    """
    Detects API keys, tokens, and passwords accidentally pasted into prompts before they reach the model.

    This function combines multiple signals to detect potential credentials in the input text.
    It returns a dictionary with the detection result, including a confidence score that varies with the input.

    :param input_text: The input text to be checked for potential credentials.
    :return: A dictionary with the detection result, including a confidence score.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Initialize the detection result
    result = DetectionResult(False, "", 0.0, "", {})

    # Define regular expression patterns for common credential formats
    patterns = [
        r"[a-zA-Z0-9_\-]{16,}",  # API key or token
        r"[a-zA-Z0-9_\-]{8,16}",  # password
        r"[a-zA-Z0-9_\-]{32,}",  # long API key or token
    ]

    # Initialize the raw confidence score
    raw_confidence = 0.0

    # Check for pattern matches
    pattern_matches = 0
    for pattern in patterns:
        matches = re.findall(pattern, input_text)
        pattern_matches += len(matches)
    if pattern_matches > 0:
        raw_confidence += 0.3 * (pattern_matches / (1 + pattern_matches))

    # Check for structural features
    sentences = input_text.count(".") + input_text.count("!") + input_text.count("?")
    if sentences > 0:
        sentence_length = len(input_text) / sentences
        raw_confidence += 0.2 * (1 - (sentence_length / (1 + sentence_length)))

    # Check for lexical diversity
    words = input_text.split()
    unique_words = set(words)
    if len(words) > 0:
        lexical_diversity = len(unique_words) / len(words)
        raw_confidence += 0.2 * lexical_diversity

    # Check for hedging/absolute-term density
    hedging_terms = ["maybe", "possibly", "could", "might"]
    absolute_terms = ["always", "never", "definitely", "certainly"]
    hedging_density = sum(1 for term in hedging_terms if term in input_text.lower()) / (1 + len(hedging_terms))
    absolute_density = sum(1 for term in absolute_terms if term in input_text.lower()) / (1 + len(absolute_terms))
    raw_confidence += 0.1 * (1 - hedging_density) * absolute_density

    # Clamp the confidence score
    confidence = max(0.0, min(1.0, raw_confidence))

    # Set the detection result
    result.blocked = confidence >= 0.5
    result.reason = "Potential credential detected" if result.blocked else "No credential detected"
    result.confidence = confidence
    result.category = "credential" if result.blocked else "benign"
    result.details = {"pattern_matches": str(pattern_matches), "sentences": str(sentences), "lexical_diversity": str(lexical_diversity)}

    # Return the detection result as a dictionary
    return {
        "blocked": result.blocked,
        "reason": result.reason,
        "confidence": result.confidence,
        "category": result.category,
        "details": result.details,
    }

if __name__ == "__main__":
    test_cases = [
        "This is a benign input.",
        "My API key is 1234567890abcdef.",
        "The password is maybe password123.",
        "This input contains multiple sentences. It has a high lexical diversity.",
        "The API key is always abcdefghijklmnop.",
    ]

    for test_case in test_cases:
        print(pasted_credential_catcher(test_case))

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_pasted_credential_catcher = pasted_credential_catcher

def pasted_credential_catcher(input_text):
    _out = _sushi_raw_pasted_credential_catcher(input_text)
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
