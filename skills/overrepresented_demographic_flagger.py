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

def overrepresented_demographic_flagger(input_text: str) -> Dict[str, object]:
    """
    Detects and flags instances where a particular demographic is overrepresented in the AI-generated content.

    This function analyzes the frequency of demographic mentions and compares it to a pre-defined threshold.
    It combines multiple signals, including weighted pattern matches, structural features, lexical diversity,
    hedging/absolute-term density, and produces a graded confidence that varies with the input.

    Args:
        input_text (str): The input text to be analyzed.

    Returns:
        Dict[str, object]: A dictionary containing the detection result, including whether the input is blocked,
            the reason for blocking, the confidence level, the category of the detection, and additional details.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Define demographic keywords and their corresponding weights
    demographic_keywords = {
        "age": ["young", "old", "senior", "junior"],
        "gender": ["male", "female", "man", "woman"],
        "race": ["white", "black", "asian", "hispanic"],
        "religion": ["christian", "muslim", "jewish", "hindu"]
    }

    # Initialize detection result
    result = DetectionResult(False, "", 0.0, "demographic", {})

    # Tokenize the input text
    tokens = re.findall(r"\b\w+\b", input_text.lower())

    # Calculate the frequency of demographic mentions
    demographic_mentions = {}
    for category, keywords in demographic_keywords.items():
        mentions = sum(1 for token in tokens if token in keywords)
        demographic_mentions[category] = mentions / len(tokens) if tokens else 0.0

    # Calculate the weighted pattern matches
    weighted_matches = sum(0.2 * mentions for mentions in demographic_mentions.values())

    # Calculate the structural features (sentence and clause counts, ratios)
    sentences = re.findall(r"[.!?]", input_text)
    sentence_count = len(sentences)
    clause_count = len(re.findall(r"[,;]", input_text))
    sentence_ratio = sentence_count / (sentence_count + clause_count) if sentence_count + clause_count > 0 else 0.0

    # Calculate the lexical diversity (unique tokens / total tokens)
    unique_tokens = len(set(tokens))
    lexical_diversity = unique_tokens / len(tokens) if tokens else 0.0

    # Calculate the hedging/absolute-term density
    hedge_terms = ["maybe", "possibly", "probably", "definitely"]
    hedge_density = sum(1 for token in tokens if token in hedge_terms) / len(tokens) if tokens else 0.0

    # Combine the signals and calculate the confidence
    raw_confidence = 0.3 * weighted_matches + 0.2 * sentence_ratio + 0.2 * lexical_diversity + 0.3 * hedge_density
    confidence = max(0.0, min(1.0, raw_confidence))

    # Determine whether the input is blocked based on the confidence level
    blocked = confidence >= 0.5

    # Update the detection result
    result.blocked = blocked
    result.reason = "Overrepresented demographic mentions" if blocked else "No overrepresented demographic mentions"
    result.confidence = confidence
    result.category = "demographic"
    result.details = {
        "demographic_mentions": demographic_mentions,
        "weighted_matches": weighted_matches,
        "sentence_ratio": sentence_ratio,
        "lexical_diversity": lexical_diversity,
        "hedge_density": hedge_density
    }

    return {
        "blocked": result.blocked,
        "reason": result.reason,
        "confidence": result.confidence,
        "category": result.category,
        "details": result.details
    }

if __name__ == "__main__":
    test_cases = [
        "The old man was very wise.",
        "The company has a diverse workforce with people of all ages, genders, and races.",
        "The new policy will benefit all citizens, regardless of their religion or socioeconomic status.",
        "The team consists of only young, white males.",
        "The city is a melting pot of cultures, with people from all over the world living together in harmony."
    ]

    for test_case in test_cases:
        result = overrepresented_demographic_flagger(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_overrepresented_demographic_flagger = overrepresented_demographic_flagger

def overrepresented_demographic_flagger(input_text):
    _out = _sushi_raw_overrepresented_demographic_flagger(input_text)
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
