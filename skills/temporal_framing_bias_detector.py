import re
from dataclasses import dataclass
from typing import Dict

@dataclass
class TemporalFramingBias:
    """Data class to hold the results of the temporal framing bias detection."""
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict

def temporal_framing_bias_detector(input_text: str) -> Dict:
    """
    Detects instances of temporal framing bias in the given input text.

    Temporal framing bias occurs when information is presented in a way that influences users' decisions by manipulating the time frame in which information is presented.
    This function uses a combination of weighted pattern matches, structural features, lexical diversity, hedging/absolute-term density, and other signals to detect temporal framing bias.

    Args:
        input_text (str): The input text to be analyzed for temporal framing bias.

    Returns:
        Dict: A dictionary containing the results of the temporal framing bias detection, including a boolean indicating whether the text is blocked, a reason for the block, a confidence score, a category, and additional details.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Initialize the results data class
    results = TemporalFramingBias(False, "", 0.0, "temporal_framing_bias", {})

    # Tokenize the input text into sentences
    sentences = re.split(r'[.!?]', input_text)

    # Remove empty sentences
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    # Calculate the ratio of sentences with absolute terms
    absolute_terms = ["always", "never", "every", "all"]
    absolute_term_count = sum(1 for sentence in sentences for term in absolute_terms if term in sentence.lower())
    absolute_terms_ratio = absolute_term_count / len(sentences) if sentences else 0.0

    # Calculate the density of hedging terms
    hedging_terms = ["maybe", "possibly", "could", "might"]
    hedging_term_count = sum(1 for sentence in sentences for term in hedging_terms if term in sentence.lower())
    hedging_terms_density = hedging_term_count / len(sentences) if sentences else 0.0

    # Calculate the ratio of overgeneral terms
    overgeneral_terms = ["everyone", "nobody", "everything", "nothing"]
    overgeneral_term_count = sum(1 for sentence in sentences for term in overgeneral_terms if term in sentence.lower())
    overgeneral_terms_ratio = overgeneral_term_count / len(sentences) if sentences else 0.0

    # Calculate the lexical diversity
    words = re.findall(r'\b\w+\b', input_text.lower())
    unique_words = set(words)
    lexical_diversity = len(unique_words) / len(words) if words else 0.0

    # Calculate the raw confidence score
    raw_confidence = 0.4 * absolute_terms_ratio + 0.3 * hedging_terms_density + 0.2 * overgeneral_terms_ratio + 0.1 * (1 - lexical_diversity)

    # Clamp the confidence score to [0.0, 1.0]
    confidence = max(0.0, min(1.0, raw_confidence))

    # Update the results data class
    results.blocked = confidence > 0.7
    results.reason = "Temporal framing bias detected" if results.blocked else "No temporal framing bias detected"
    results.confidence = confidence
    results.details = {
        "absolute_terms_ratio": absolute_terms_ratio,
        "hedging_terms_density": hedging_terms_density,
        "overgeneral_terms_ratio": overgeneral_terms_ratio,
        "lexical_diversity": lexical_diversity
    }

    # Return the results as a dictionary
    return {
        "blocked": results.blocked,
        "reason": results.reason,
        "confidence": results.confidence,
        "category": results.category,
        "details": results.details
    }

if __name__ == "__main__":
    test_cases = [
        "The new policy will always be beneficial.",
        "Maybe the new policy will be beneficial.",
        "The new policy will be beneficial for everyone.",
        "The new policy has been beneficial for the past year.",
        "There is no evidence that the new policy will be beneficial.",
        "The new policy has been beneficial, but it may not always be the case."
    ]

    for test_case in test_cases:
        results = temporal_framing_bias_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {results['blocked']}")
        print(f"Reason: {results['reason']}")
        print(f"Confidence: {results['confidence']}")
        print(f"Category: {results['category']}")
        print(f"Details: {results['details']}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_temporal_framing_bias_detector = temporal_framing_bias_detector

def temporal_framing_bias_detector(input_text):
    _out = _sushi_raw_temporal_framing_bias_detector(input_text)
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
