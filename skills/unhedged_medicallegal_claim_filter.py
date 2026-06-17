import re
from typing import Dict
from dataclasses import dataclass
from math import log

@dataclass
class SentenceFeatures:
    """Features extracted from a sentence."""
    absolutes: int  # Number of absolute terms (e.g., "always", "never")
    hedges: int  # Number of hedging terms (e.g., "may", "might")
    overgeneral_terms: int  # Number of overgeneral terms (e.g., "all", "every")

def extract_features(sentence: str) -> SentenceFeatures:
    """Extract features from a sentence."""
    absolutes = len(re.findall(r"\b(always|never|must|should|will)\b", sentence, re.IGNORECASE))
    hedges = len(re.findall(r"\b(may|might|could|would|should)\b", sentence, re.IGNORECASE))
    overgeneral_terms = len(re.findall(r"\b(all|every|each|any)\b", sentence, re.IGNORECASE))
    return SentenceFeatures(absolutes, hedges, overgeneral_terms)

def unhedged_medicallegal_claim_filter(input_text: str) -> Dict:
    """
    Flags AI output giving medical or legal directives without a verify-with-a-professional caveat.

    This function combines multiple signals to detect unhedged medical or legal claims:
    1. Absolute terms (e.g., "always", "never")
    2. Hedging terms (e.g., "may", "might")
    3. Overgeneral terms (e.g., "all", "every")

    The confidence score is a weighted sum of these signals, clamped to [0.0, 1.0].

    Args:
        input_text (str): The input text to analyze.

    Returns:
        Dict: A dictionary containing the results:
            - "blocked" (bool): Whether the input text is blocked.
            - "reason" (str): The reason for blocking (if applicable).
            - "confidence" (float): The confidence score in [0.0, 1.0].
            - "category" (str): The category of the claim (medical or legal).
            - "details" (Dict): Additional details about the claim.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    sentences = re.split(r"[.!?]", input_text)
    total_absolutes = 0
    total_hedges = 0
    total_overgeneral_terms = 0
    for sentence in sentences:
        features = extract_features(sentence)
        total_absolutes += features.absolutes
        total_hedges += features.hedges
        total_overgeneral_terms += features.overgeneral_terms

    # Compute ratios
    num_sentences = len(sentences)
    if num_sentences == 0:
        absolutes_ratio = 0.0
        hedge_density = 0.0
    else:
        absolutes_ratio = total_absolutes / num_sentences
        hedge_density = total_hedges / num_sentences if num_sentences > 0 else 0.0

    # Compute overgeneral term ratio
    num_words = len(input_text.split())
    if num_words == 0:
        overgeneral_terms_ratio = 0.0
    else:
        overgeneral_terms_ratio = total_overgeneral_terms / num_words

    # Compute confidence score
    raw_score = 0.5 * absolutes_ratio + 0.3 * (1 - hedge_density) + 0.2 * overgeneral_terms_ratio
    confidence = max(0.0, min(1.0, raw_score))

    # Determine category
    medical_keywords = ["medical", "health", "treatment", "disease"]
    legal_keywords = ["legal", "law", "court", "case"]
    if any(keyword in input_text.lower() for keyword in medical_keywords):
        category = "medical"
    elif any(keyword in input_text.lower() for keyword in legal_keywords):
        category = "legal"
    else:
        category = "unknown"

    # Determine blocking
    blocked = confidence > 0.7

    return {
        "blocked": blocked,
        "reason": "Unhedged medical or legal claim" if blocked else "No issue detected",
        "confidence": confidence,
        "category": category,
        "details": {
            "absolutes_ratio": absolutes_ratio,
            "hedge_density": hedge_density,
            "overgeneral_terms_ratio": overgeneral_terms_ratio,
        },
    }

if __name__ == "__main__":
    test_cases = [
        "You should always consult a doctor before taking any medication.",
        "The court will always rule in favor of the plaintiff.",
        "This treatment is effective for all patients.",
        "The law requires every citizen to pay taxes.",
        "This is a general statement and not specific to any individual.",
        "The company will never disclose your personal information.",
    ]

    for test_case in test_cases:
        result = unhedged_medicallegal_claim_filter(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_unhedged_medicallegal_claim_filter = unhedged_medicallegal_claim_filter

def unhedged_medicallegal_claim_filter(input_text):
    _out = _sushi_raw_unhedged_medicallegal_claim_filter(input_text)
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
