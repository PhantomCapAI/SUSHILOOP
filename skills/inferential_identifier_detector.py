import re
from typing import Dict

def inferential_identifier_detector(input_text: str) -> Dict:
    """
    Detects and flags instances where AI-generated text inadvertently reveals personally identifiable information (PII) 
    through subtle inferential patterns, such as mentioning specific locations or relationships that could be used to 
    identify an individual.

    Args:
        input_text (str): The text to be analyzed for potential PII compromises.

    Returns:
        Dict: A dictionary containing the results of the analysis, including a boolean indicating whether the text 
        is blocked, a reason for the blockage, a confidence score, a category, and additional details.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Initialize the result dictionary
    result = {"blocked": False, "reason": "", "confidence": 0.0, "category": "", "details": {}}

    # Define keywords and patterns that may indicate PII
    keywords = ["name", "address", "phone", "email", "location"]
    patterns = [r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"]

    # Calculate the keyword density
    keyword_count = sum(1 for keyword in keywords if keyword in input_text.lower())
    keyword_density = keyword_count / (len(input_text.split()) + 1) if input_text.split() else 0.0

    # Calculate the pattern density
    pattern_count = sum(1 for pattern in patterns if re.search(pattern, input_text))
    pattern_density = pattern_count / (len(input_text.split()) + 1) if input_text.split() else 0.0

    # Calculate the sentence count and ratio
    sentences = re.split(r"[.!?]", input_text)
    sentence_count = len([sentence for sentence in sentences if sentence.strip()])
    sentence_ratio = sentence_count / (len(input_text.split()) + 1) if input_text.split() else 0.0

    # Calculate the lexical diversity
    words = re.findall(r"\b\w+\b", input_text.lower())
    word_set = set(words)
    lexical_diversity = len(word_set) / (len(words) + 1) if words else 0.0

    # Calculate the hedging and absolute term density
    hedging_terms = ["maybe", "possibly", "perhaps"]
    absolute_terms = ["always", "never", "definitely"]
    hedging_count = sum(1 for term in hedging_terms if term in input_text.lower())
    absolute_count = sum(1 for term in absolute_terms if term in input_text.lower())
    hedging_density = hedging_count / (len(input_text.split()) + 1) if input_text.split() else 0.0
    absolute_density = absolute_count / (len(input_text.split()) + 1) if input_text.split() else 0.0

    # Calculate the raw confidence score
    raw_confidence = 0.2 * keyword_density + 0.2 * pattern_density + 0.2 * sentence_ratio + 0.2 * lexical_diversity + 0.1 * hedging_density + 0.1 * absolute_density

    # Clamp the confidence score to [0.0, 1.0]
    confidence = max(0.0, min(1.0, raw_confidence))

    # Determine the blockage decision
    result["blocked"] = confidence >= 0.5

    # Update the result dictionary
    result["reason"] = "Potential PII compromise detected" if result["blocked"] else "No PII compromise detected"
    result["confidence"] = confidence
    result["category"] = "PII" if result["blocked"] else "benign"
    result["details"] = {
        "keyword_density": keyword_density,
        "pattern_density": pattern_density,
        "sentence_ratio": sentence_ratio,
        "lexical_diversity": lexical_diversity,
        "hedging_density": hedging_density,
        "absolute_density": absolute_density,
    }

    return result


if __name__ == "__main__":
    test_cases = [
        "My name is John and I live in New York.",
        "The company is located at 123 Main Street, Anytown, USA.",
        "You can contact me at john@example.com or 555-1234.",
        "The weather is nice today.",
        "The product is always available and never out of stock.",
    ]

    for test_case in test_cases:
        print(inferential_identifier_detector(test_case))

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_inferential_identifier_detector = inferential_identifier_detector

def inferential_identifier_detector(input_text):
    _out = _sushi_raw_inferential_identifier_detector(input_text)
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
