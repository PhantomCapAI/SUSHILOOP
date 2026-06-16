import re
import json
import math
from typing import Dict
from dataclasses import dataclass
from collections import Counter

@dataclass
class Sentence:
    text: str
    absolutes: int
    hedges: int
    overgeneral_terms: int

def multifaceted_perspective_analyzer(input_text: str) -> Dict:
    """
    Analyzes AI-generated content to detect the presence of diverse, credible sources 
    and evaluates the depth of discussion on a topic, ensuring that users are exposed 
    to well-rounded perspectives.

    Args:
    input_text (str): The text to be analyzed.

    Returns:
    dict: A dictionary containing the results of the analysis, including a boolean 
    indicating whether the text is blocked, a reason for the block, a confidence 
    score, a category, and additional details.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Tokenize the input text into sentences
    sentences = re.split(r'[.!?]', input_text)

    # Remove empty strings
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    # Initialize counters
    total_absolutes = 0
    total_hedges = 0
    total_overgeneral_terms = 0
    sentence_count = len(sentences)

    # Analyze each sentence
    sentence_data = []
    for sentence in sentences:
        # Count absolutes (e.g., "always", "never")
        absolutes = len(re.findall(r'\b(always|never|every|all)\b', sentence, re.IGNORECASE))
        total_absolutes += absolutes

        # Count hedges (e.g., "maybe", "possibly")
        hedges = len(re.findall(r'\b(maybe|possibly|perhaps|could)\b', sentence, re.IGNORECASE))
        total_hedges += hedges

        # Count overgeneral terms (e.g., "everyone", "nobody")
        overgeneral_terms = len(re.findall(r'\b(everyone|nobody|everybody|noone)\b', sentence, re.IGNORECASE))
        total_overgeneral_terms += overgeneral_terms

        # Store sentence data
        sentence_data.append(Sentence(sentence, absolutes, hedges, overgeneral_terms))

    # Calculate ratios
    if sentence_count > 0:
        absolutes_ratio = total_absolutes / sentence_count
        hedge_density = total_hedges / sentence_count if sentence_count > 0 else 0
        overgeneral_terms_ratio = total_overgeneral_terms / sentence_count
    else:
        absolutes_ratio = 0
        hedge_density = 0
        overgeneral_terms_ratio = 0

    # Calculate confidence score
    raw_score = 0.5 * absolutes_ratio + 0.3 * hedge_density + 0.2 * overgeneral_terms_ratio
    confidence = max(0.0, min(1.0, raw_score))

    # Determine block status
    blocked = confidence > 0.7

    # Create result dictionary
    result = {
        "blocked": blocked,
        "reason": "Potential echo chamber or biased information detected" if blocked else "No issues detected",
        "confidence": confidence,
        "category": "Multifaceted Perspective Analyzer",
        "details": {
            "absolutes_ratio": absolutes_ratio,
            "hedge_density": hedge_density,
            "overgeneral_terms_ratio": overgeneral_terms_ratio,
            "sentence_count": sentence_count,
            "total_absolutes": total_absolutes,
            "total_hedges": total_hedges,
            "total_overgeneral_terms": total_overgeneral_terms,
        }
    }

    return result

if __name__ == "__main__":
    test_cases = [
        "The sun is always shining in California.",
        "Maybe it will rain tomorrow, but I'm not sure.",
        "Everyone loves ice cream, and nobody dislikes it.",
        "The new policy has been met with widespread criticism, but some people support it.",
        "The company's financial reports show a significant increase in revenue, but the CEO is cautious about the future.",
    ]

    for test_case in test_cases:
        result = multifaceted_perspective_analyzer(test_case)
        print(json.dumps(result, indent=4))

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_multifaceted_perspective_analyzer = multifaceted_perspective_analyzer

def multifaceted_perspective_analyzer(input_text):
    _out = _sushi_raw_multifaceted_perspective_analyzer(input_text)
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
