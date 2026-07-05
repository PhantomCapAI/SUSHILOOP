import re
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class DetectionResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict[str, float]

def overemphasized_minority_detector(input_text: str) -> Dict[str, object]:
    """
    Detects when a minority viewpoint is overrepresented in the AI's output, 
    potentially indicating bias towards a particular group or perspective.

    This function analyzes the frequency of minority viewpoints in the output 
    and raises a flag if they exceed a certain threshold.

    Args:
    input_text (str): The text to be analyzed.

    Returns:
    Dict[str, object]: A dictionary containing the detection result, 
    including whether the text is blocked, the reason, confidence level, 
    category, and details.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Define keywords related to minority viewpoints
    minority_keywords = ["minority", "underrepresented", "marginalized"]
    absolute_terms = ["always", "never", "all", "none"]
    hedge_terms = ["maybe", "possibly", "could", "might"]

    # Initialize counters
    minority_count = 0
    absolute_count = 0
    hedge_count = 0
    sentence_count = 0
    word_count = 0

    # Split the input text into sentences
    sentences = re.split(r'[.!?]', input_text)

    # Analyze each sentence
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            sentence_count += 1

            # Split the sentence into words
            words = sentence.split()
            word_count += len(words)

            # Count minority keywords
            for word in words:
                if word.lower() in minority_keywords:
                    minority_count += 1

            # Count absolute terms
            for word in words:
                if word.lower() in absolute_terms:
                    absolute_count += 1

            # Count hedge terms
            for word in words:
                if word.lower() in hedge_terms:
                    hedge_count += 1

    # Calculate ratios
    if sentence_count == 0:
        minority_ratio = 0.0
        absolute_ratio = 0.0
        hedge_ratio = 0.0
    else:
        minority_ratio = minority_count / sentence_count
        absolute_ratio = absolute_count / sentence_count
        hedge_ratio = hedge_count / sentence_count

    if word_count == 0:
        lexical_diversity = 0.0
    else:
        lexical_diversity = len(set(re.findall(r'\b\w+\b', input_text))) / word_count

    # Calculate confidence
    raw_confidence = 0.4 * minority_ratio + 0.3 * absolute_ratio + 0.2 * hedge_ratio + 0.1 * (1 - lexical_diversity)
    confidence = max(0.0, min(1.0, raw_confidence))

    # Determine if the text is blocked
    blocked = confidence >= 0.5

    # Create the detection result
    result = DetectionResult(
        blocked=blocked,
        reason="Overemphasized minority viewpoint" if blocked else "No overemphasized minority viewpoint",
        confidence=confidence,
        category="bias",
        details={
            "minority_ratio": minority_ratio,
            "absolute_ratio": absolute_ratio,
            "hedge_ratio": hedge_ratio,
            "lexical_diversity": lexical_diversity
        }
    )

    return {
        "blocked": result.blocked,
        "reason": result.reason,
        "confidence": result.confidence,
        "category": result.category,
        "details": result.details
    }

if __name__ == "__main__":
    test_cases = [
        "The minority group is always right.",
        "The underrepresented community is never heard.",
        "The marginalized people are all suffering.",
        "The majority is always in power.",
        "The system is fair and balanced.",
        "The government is maybe corrupt.",
        "The company is possibly biased.",
        "The media is all propaganda.",
        "The world is a complex place.",
        "The truth is never simple."
    ]

    for test_case in test_cases:
        result = overemphasized_minority_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_overemphasized_minority_detector = overemphasized_minority_detector

def overemphasized_minority_detector(input_text):
    _out = _sushi_raw_overemphasized_minority_detector(input_text)
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
