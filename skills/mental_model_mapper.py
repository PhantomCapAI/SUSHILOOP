import re
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class MentalModelMapperResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict

def mental_model_mapper(input_text: str) -> Dict:
    """
    Identifies and highlights potential mental model mismatches between human users and AI outputs.

    This function combines multiple signals to detect potential mismatches, including:
    - Absolute term density
    - Hedge term density
    - Overgeneral term density
    - Sentence structure and complexity

    The function returns a dictionary with the following keys:
    - blocked: Whether the input text is blocked due to potential mental model mismatch
    - reason: The reason for blocking the input text
    - confidence: A graded confidence score between 0.0 and 1.0 indicating the strength of the signals
    - category: The category of the potential mental model mismatch
    - details: Additional details about the potential mental model mismatch

    :param input_text: The input text to be analyzed
    :return: A dictionary with the analysis results
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Tokenize the input text into sentences
    sentences = re.split(r'[.!?]', input_text)

    # Remove empty sentences
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    # Calculate the absolute term density
    absolute_terms = re.findall(r'\b(always|never|all|none)\b', input_text, re.IGNORECASE)
    absolute_term_density = len(absolute_terms) / len(sentences) if sentences else 0.0

    # Calculate the hedge term density
    hedge_terms = re.findall(r'\b(maybe|perhaps|possibly|probably)\b', input_text, re.IGNORECASE)
    hedge_term_density = len(hedge_terms) / len(sentences) if sentences else 0.0

    # Calculate the overgeneral term density
    overgeneral_terms = re.findall(r'\b(everyone|everything|always|never)\b', input_text, re.IGNORECASE)
    overgeneral_term_density = len(overgeneral_terms) / len(sentences) if sentences else 0.0

    # Calculate the sentence complexity
    sentence_complexity = sum(len(re.findall(r'\b\w+\b', sentence)) for sentence in sentences) / len(sentences) if sentences else 0.0

    # Combine the signals to calculate the confidence score
    raw_score = 0.4 * absolute_term_density + 0.3 * hedge_term_density + 0.2 * overgeneral_term_density + 0.1 * sentence_complexity
    confidence = max(0.0, min(1.0, raw_score))

    # Determine the blocking decision based on the confidence score
    blocked = confidence > 0.7

    # Determine the reason for blocking
    reason = "Potential mental model mismatch detected" if blocked else "No potential mental model mismatch detected"

    # Determine the category of the potential mental model mismatch
    category = "Absolute term density" if absolute_term_density > 0.5 else "Hedge term density" if hedge_term_density > 0.5 else "Overgeneral term density" if overgeneral_term_density > 0.5 else "Sentence complexity"

    # Create the result dictionary
    result = MentalModelMapperResult(
        blocked=blocked,
        reason=reason,
        confidence=confidence,
        category=category,
        details={
            "absolute_term_density": absolute_term_density,
            "hedge_term_density": hedge_term_density,
            "overgeneral_term_density": overgeneral_term_density,
            "sentence_complexity": sentence_complexity
        }
    )

    return result.__dict__

if __name__ == "__main__":
    test_cases = [
        "I always do this.",
        "Maybe I will do this.",
        "Everyone will do this.",
        "This is a simple sentence.",
        "This is a very complex sentence with many clauses and phrases."
    ]

    for test_case in test_cases:
        result = mental_model_mapper(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_mental_model_mapper = mental_model_mapper

def mental_model_mapper(input_text):
    _out = _sushi_raw_mental_model_mapper(input_text)
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
