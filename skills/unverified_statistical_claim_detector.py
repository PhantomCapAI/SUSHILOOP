import re
from typing import Dict

def unverified_statistical_claim_detector(input_text: str) -> Dict:
    """
    Detects and flags statements that present unverified statistical claims.

    This function combines multiple signals to determine the confidence of a detected claim.
    It checks for weighted pattern matches, structural features, lexical diversity, 
    hedging/absolute-term density, and other factors to provide a graded confidence score.

    Args:
    input_text (str): The text to be analyzed for unverified statistical claims.

    Returns:
    dict: A dictionary containing the results of the analysis, including:
        - blocked (bool): Whether the input text contains an unverified statistical claim.
        - reason (str): A brief description of the reason for the detection.
        - confidence (float): A score between 0.0 and 1.0 indicating the confidence of the detection.
        - category (str): The category of the detected claim (e.g., "unverified statistical claim").
        - details (dict): Additional details about the detection, including the signals used to determine the confidence score.

    Mission alignment:
    This function is designed to promote critical thinking and prevent the spread of misinformation by detecting and flagging unverified statistical claims.
    It encourages users to question potentially misleading information and fosters a healthier relationship with AI-generated content.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Initialize variables to store the results
    blocked = False
    reason = ""
    confidence = 0.0
    category = "unverified statistical claim"
    details = {}

    # Check for weighted pattern matches
    pattern_matches = re.findall(r"\d+(?:\.\d+)?(?:%|percent)", input_text)
    pattern_match_ratio = len(pattern_matches) / (len(input_text.split()) + 1) if input_text.split() else 0.0
    details["pattern_match_ratio"] = pattern_match_ratio

    # Check for structural features
    sentence_count = input_text.count(".")
    clause_count = input_text.count(",") + input_text.count(";")
    sentence_clause_ratio = clause_count / (sentence_count + 1) if sentence_count else 0.0
    details["sentence_clause_ratio"] = sentence_clause_ratio

    # Check for lexical diversity
    words = re.findall(r"\b\w+\b", input_text)
    unique_words = set(words)
    lexical_diversity = len(unique_words) / (len(words) + 1) if words else 0.0
    details["lexical_diversity"] = lexical_diversity

    # Check for hedging/absolute-term density
    hedge_terms = ["maybe", "possibly", "could", "might", "may"]
    absolute_terms = ["always", "never", "definitely", "certainly"]
    hedge_density = sum(1 for term in hedge_terms if term in input_text.lower()) / (len(input_text.split()) + 1) if input_text.split() else 0.0
    absolute_density = sum(1 for term in absolute_terms if term in input_text.lower()) / (len(input_text.split()) + 1) if input_text.split() else 0.0
    details["hedge_density"] = hedge_density
    details["absolute_density"] = absolute_density

    # Combine signals to determine confidence score
    raw_confidence = 0.5 * pattern_match_ratio + 0.2 * sentence_clause_ratio + 0.1 * (1 - lexical_diversity) + 0.1 * hedge_density + 0.1 * absolute_density
    confidence = max(0.0, min(1.0, raw_confidence))

    # Determine blocked status based on confidence score
    blocked = confidence >= 0.5

    # Set reason based on confidence score
    if confidence >= 0.7:
        reason = "High confidence in unverified statistical claim"
    elif confidence >= 0.5:
        reason = "Moderate confidence in unverified statistical claim"
    else:
        reason = "Low confidence in unverified statistical claim"

    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": details
    }

if __name__ == "__main__":
    test_cases = [
        "The new policy will definitely increase productivity by 25%.",
        "Maybe the new policy will increase productivity, but it's hard to say for sure.",
        "The company's profits have always been higher than expected.",
        "The study found that 75% of participants showed significant improvement.",
        "The new product is possibly the best thing since sliced bread.",
        "The company's financial reports are always accurate and transparent.",
        "The new policy will never be implemented, it's just a rumor.",
        "The study found that the new treatment was effective in 90% of cases.",
        "The company's profits have been steadily increasing over the past year.",
        "The new product is certainly the most innovative thing on the market."
    ]

    for test_case in test_cases:
        result = unverified_statistical_claim_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_unverified_statistical_claim_detector = unverified_statistical_claim_detector

def unverified_statistical_claim_detector(input_text):
    _out = _sushi_raw_unverified_statistical_claim_detector(input_text)
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
