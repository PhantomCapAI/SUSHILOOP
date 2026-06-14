import re
from math import log
from typing import Dict

def rapid_fire_inquiry_limiter(input_text: str) -> Dict:
    """
    This function implements the Rapid Fire Inquiry Limiter skill, which detects and limits 
    consecutive, similar inquiries from a user within a short time frame. It promotes a 
    more balanced and reflective interaction between humans and AI by encouraging users 
    to pause, reflect, and consolidate their understanding before asking follow-up questions.

    The function combines multiple signals to compute a graded confidence score, which 
    indicates the likelihood that the input text is a rapid-fire inquiry. The signals 
    include:

    1. Absolute term density: The ratio of absolute terms (e.g., "always", "never") to 
       the total number of words in the input text.
    2. Hedge term density: The ratio of hedge terms (e.g., "maybe", "possibly") to 
       the total number of words in the input text.
    3. Overgeneral term density: The ratio of overgeneral terms (e.g., "everyone", 
       "everything") to the total number of words in the input text.
    4. Lexical diversity: The ratio of unique words to the total number of words in the 
       input text.
    5. Sentence complexity: The average number of clauses per sentence in the input text.

    The function returns a dictionary with the following keys:
    - "blocked": A boolean indicating whether the input text is blocked as a rapid-fire inquiry.
    - "reason": A string explaining why the input text is blocked (if applicable).
    - "confidence": A float between 0.0 and 1.0 indicating the likelihood that the input text is a rapid-fire inquiry.
    - "category": A string categorizing the input text (e.g., "rapid-fire inquiry", "legitimate question").
    - "details": A dictionary with additional details about the input text, including the computed signal values.

    :param input_text: The input text to be evaluated.
    :return: A dictionary with the evaluation results.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Preprocess the input text
    input_text = input_text.lower()
    words = re.findall(r'\b\w+\b', input_text)
    sentences = re.split(r'[.!?]', input_text)

    # Compute signal values
    absolute_terms = re.findall(r'\b(always|never|all|none)\b', input_text)
    hedge_terms = re.findall(r'\b(maybe|possibly|perhaps|probably)\b', input_text)
    overgeneral_terms = re.findall(r'\b(everyone|everything|all|any)\b', input_text)
    unique_words = set(words)
    clauses = sum(1 for sentence in sentences for _ in re.findall(r'\b(and|or|but)\b', sentence))

    # Compute signal ratios
    absolute_ratio = len(absolute_terms) / len(words) if words else 0.0
    hedge_ratio = len(hedge_terms) / len(words) if words else 0.0
    overgeneral_ratio = len(overgeneral_terms) / len(words) if words else 0.0
    lexical_diversity = len(unique_words) / len(words) if words else 0.0
    sentence_complexity = clauses / len(sentences) if sentences else 0.0

    # Compute the confidence score
    raw_score = 0.2 * absolute_ratio + 0.2 * hedge_ratio + 0.2 * overgeneral_ratio + 0.2 * (1 - lexical_diversity) + 0.2 * sentence_complexity
    confidence = max(0.0, min(1.0, raw_score))

    # Determine the block status and reason
    blocked = confidence > 0.7
    reason = "Rapid-fire inquiry detected" if blocked else "Legitimate question"

    # Return the evaluation results
    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": "rapid-fire inquiry" if blocked else "legitimate question",
        "details": {
            "absolute_ratio": absolute_ratio,
            "hedge_ratio": hedge_ratio,
            "overgeneral_ratio": overgeneral_ratio,
            "lexical_diversity": lexical_diversity,
            "sentence_complexity": sentence_complexity
        }
    }

if __name__ == "__main__":
    test_cases = [
        "What is the meaning of life?",
        "What is the meaning of life? What is the purpose of existence?",
        "I always wonder about the universe and its secrets.",
        "Maybe I'll ask another question later.",
        "Everyone knows that AI is the future.",
        "This is a test case with multiple sentences. It has several clauses, and it's quite complex.",
        "What is the capital of France? What is the capital of Germany? What is the capital of Italy?",
        "I'm not sure what to ask, but I'll try something.",
        "This is a rapid-fire inquiry with multiple questions: What is the meaning of life? What is the purpose of existence? What is the nature of reality?"
    ]

    for test_case in test_cases:
        result = rapid_fire_inquiry_limiter(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_rapid_fire_inquiry_limiter = rapid_fire_inquiry_limiter

def rapid_fire_inquiry_limiter(input_text):
    _out = _sushi_raw_rapid_fire_inquiry_limiter(input_text)
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
