import re
from typing import Dict
from dataclasses import dataclass

@dataclass
class EmotiveLanguageAmplifierDetectorResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict[str, float]

def emotive_language_amplifier_detector(input_text: str) -> Dict:
    """
    Detects when AI-generated text overly amplifies emotive language, potentially manipulating human emotions and decision-making.

    Args:
        input_text (str): The input text to analyze.

    Returns:
        Dict: A dictionary containing the detection result, including whether the text is blocked, the reason, confidence, category, and details.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    # Define emotive language patterns
    emotive_patterns = [
        r"\b(amazing|awesome|incredible|unbelievable|outstanding)\b",
        r"\b(terrible|awful|horrible|disastrous|catastrophic)\b",
        r"\b(everyone|always|never|no one|nothing)\b",
    ]

    # Define absolute terms
    absolute_terms = ["always", "never", "everyone", "no one", "nothing"]

    # Define hedge terms
    hedge_terms = ["maybe", "possibly", "could", "might", "perhaps"]

    # Initialize counts
    emotive_count = 0
    absolute_count = 0
    hedge_count = 0
    sentence_count = 0
    word_count = 0

    # Split input text into sentences
    sentences = re.split(r"[.!?]", input_text)

    # Analyze each sentence
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            sentence_count += 1
            words = sentence.split()
            word_count += len(words)

            # Count emotive language patterns
            for pattern in emotive_patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                emotive_count += len(matches)

            # Count absolute terms
            for term in absolute_terms:
                if term in sentence.lower():
                    absolute_count += 1

            # Count hedge terms
            for term in hedge_terms:
                if term in sentence.lower():
                    hedge_count += 1

    # Calculate ratios
    if sentence_count > 0:
        emotive_ratio = emotive_count / sentence_count
        absolute_ratio = absolute_count / sentence_count
        hedge_ratio = hedge_count / sentence_count
    else:
        emotive_ratio = 0.0
        absolute_ratio = 0.0
        hedge_ratio = 0.0

    if word_count > 0:
        absolute_term_density = absolute_count / word_count
        hedge_term_density = hedge_count / word_count
    else:
        absolute_term_density = 0.0
        hedge_term_density = 0.0

    # Calculate confidence
    raw_confidence = 0.4 * emotive_ratio + 0.3 * absolute_term_density + 0.3 * hedge_term_density
    confidence = max(0.0, min(1.0, raw_confidence))

    # Determine blocking
    blocked = confidence >= 0.5

    # Create result
    result = EmotiveLanguageAmplifierDetectorResult(
        blocked=blocked,
        reason="Emotive language amplification detected" if blocked else "No emotive language amplification detected",
        confidence=confidence,
        category="emotive_language_amplifier",
        details={
            "emotive_ratio": emotive_ratio,
            "absolute_term_density": absolute_term_density,
            "hedge_term_density": hedge_term_density,
        },
    )

    return result.__dict__

if __name__ == "__main__":
    test_cases = [
        "This is an amazing product that everyone will love!",
        "The new policy is terrible and will affect everyone negatively.",
        "Maybe this product is not as great as everyone says.",
        "The company always delivers high-quality products.",
        "The weather is nice today.",
    ]

    for test_case in test_cases:
        result = emotive_language_amplifier_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_emotive_language_amplifier_detector = emotive_language_amplifier_detector

def emotive_language_amplifier_detector(input_text):
    _out = _sushi_raw_emotive_language_amplifier_detector(input_text)
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
