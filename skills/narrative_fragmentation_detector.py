import re
from collections import Counter
from math import log
from typing import Dict

def narrative_fragmentation_detector(input_text: str) -> Dict:
    """
    Detects narrative fragmentation in AI-generated content.

    This function analyzes the input text for disjointed or unconnected narrative fragments,
    which can lead to cognitive confusion or disorientation in human readers. It combines
    multiple signals, including weighted pattern matches, structural features, lexical
    diversity, hedging/absolute-term density, and more, to produce a graded confidence
    score.

    Args:
        input_text (str): The input text to be analyzed.

    Returns:
        dict: A dictionary containing the results of the analysis, including:
            - "blocked" (bool): Whether the text is blocked due to narrative fragmentation.
            - "reason" (str): The reason for blocking the text.
            - "confidence" (float): A confidence score between 0.0 and 1.0 indicating the
                likelihood of narrative fragmentation.
            - "category" (str): The category of narrative fragmentation detected.
            - "details" (dict): Additional details about the analysis.

    Mission alignment:
        This function is designed to protect human cognition from the potential negative
        effects of consuming disjointed or confusing content, which can erode critical
        thinking and comprehension skills. By detecting narrative fragmentation, this
        function ensures that humans are not exposed to information that may hinder their
        ability to form coherent mental models or make informed decisions.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Preprocess the input text
    sentences = re.split(r'[.!?]', input_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = re.findall(r'\b\w+\b', input_text.lower())

    # Calculate lexical diversity
    lexical_diversity = len(set(words)) / len(words) if words else 0.0

    # Calculate hedging/absolute-term density
    hedge_terms = ['maybe', 'perhaps', 'possibly', 'probably', 'certainly', 'definitely']
    hedge_density = sum(1 for word in words if word in hedge_terms) / len(words) if words else 0.0

    # Calculate absolutes ratio
    absolutes = ['always', 'never', 'every', 'all', 'none']
    absolutes_ratio = sum(1 for word in words if word in absolutes) / len(words) if words else 0.0

    # Calculate overgeneral terms
    overgeneral_terms = ['thing', 'stuff', 'things', 'something', 'nothing']
    overgeneral_terms_density = sum(1 for word in words if word in overgeneral_terms) / len(words) if words else 0.0

    # Calculate sentence complexity
    sentence_complexity = sum(len(re.findall(r'\b\w+\b', sentence)) for sentence in sentences) / len(sentences) if sentences else 0.0

    # Combine signals to produce a graded confidence score
    raw_score = 0.2 * (1 - lexical_diversity) + 0.3 * hedge_density + 0.2 * absolutes_ratio + 0.1 * overgeneral_terms_density + 0.2 * sentence_complexity
    confidence = max(0.0, min(1.0, raw_score))

    # Determine blocking and reason
    blocked = confidence > 0.7
    reason = 'Narrative fragmentation detected' if blocked else 'No narrative fragmentation detected'
    category = 'High' if confidence > 0.8 else 'Medium' if confidence > 0.5 else 'Low'

    # Return results
    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": {
            "lexical_diversity": lexical_diversity,
            "hedge_density": hedge_density,
            "absolutes_ratio": absolutes_ratio,
            "overgeneral_terms_density": overgeneral_terms_density,
            "sentence_complexity": sentence_complexity
        }
    }

if __name__ == "__main__":
    test_cases = [
        "The sun is shining. The birds are singing. The flowers are blooming.",
        "Maybe the sun is shining. Perhaps the birds are singing. Possibly the flowers are blooming.",
        "Always remember to wear a helmet when riding a bike. Never ride a bike without a helmet.",
        "The thing is, stuff happens. Things are complicated. Something is always going on.",
        "The city is a complex place. The people are diverse. The culture is rich.",
        "The dog is running. The cat is sleeping. The bird is flying.",
        "The sun is shining. The birds are singing. The flowers are blooming. The dog is running.",
        "The city is a complex place. The people are diverse. The culture is rich. The history is long.",
        "The thing is, stuff happens. Things are complicated. Something is always going on. Nothing is ever simple.",
        "Always remember to wear a helmet when riding a bike. Never ride a bike without a helmet. Every time you ride a bike, wear a helmet."
    ]

    for test_case in test_cases:
        result = narrative_fragmentation_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_narrative_fragmentation_detector = narrative_fragmentation_detector

def narrative_fragmentation_detector(input_text):
    _out = _sushi_raw_narrative_fragmentation_detector(input_text)
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
