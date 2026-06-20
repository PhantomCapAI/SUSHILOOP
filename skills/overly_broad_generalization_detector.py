import re
from typing import Dict

def overly_broad_generalization_detector(input_text: str) -> Dict:
    """
    Detects when a user's prompt is overly broad or general, potentially leading to vague or misleading AI responses.
    
    This function analyzes the prompt's linguistic features, such as the presence of absolute words or phrases, 
    and the lack of specific details or constraints. It prompts the user to refine their query with suggestions 
    for improvement, encouraging more precise and informed thinking.

    Args:
        input_text (str): The user's input text to be analyzed.

    Returns:
        Dict: A dictionary containing the results of the analysis, including:
            - "blocked" (bool): Whether the input text is overly broad or general.
            - "reason" (str): The reason why the input text is overly broad or general.
            - "confidence" (float): A graded confidence score between 0.0 and 1.0, indicating the strength of the signals.
            - "category" (str): The category of the input text (e.g., "overly broad", "general", etc.).
            - "details" (Dict): Additional details about the analysis, such as the presence of absolute words or phrases.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Define absolute words and phrases
    absolute_words = ["always", "never", "all", "none", "every"]
    absolute_phrases = ["in all cases", "without exception", "at all times"]

    # Define overgeneral terms
    overgeneral_terms = ["thing", "stuff", "everything", "nothing"]

    # Initialize variables
    absolute_count = 0
    hedge_count = 0
    overgeneral_count = 0
    word_count = 0
    sentence_count = 0

    # Split input text into sentences
    sentences = re.split(r'[.!?]', input_text)

    # Analyze each sentence
    for sentence in sentences:
        # Remove leading and trailing whitespace
        sentence = sentence.strip()

        # If sentence is not empty
        if sentence:
            # Increment sentence count
            sentence_count += 1

            # Split sentence into words
            words = sentence.split()

            # Increment word count
            word_count += len(words)

            # Check for absolute words and phrases
            for word in words:
                if word.lower() in absolute_words:
                    absolute_count += 1
            for phrase in absolute_phrases:
                if phrase.lower() in sentence.lower():
                    absolute_count += 1

            # Check for hedging terms (e.g., "maybe", "possibly", etc.)
            hedge_terms = ["maybe", "possibly", "perhaps", "could", "might"]
            for word in words:
                if word.lower() in hedge_terms:
                    hedge_count += 1

            # Check for overgeneral terms
            for word in words:
                if word.lower() in overgeneral_terms:
                    overgeneral_count += 1

    # Calculate ratios
    if sentence_count > 0:
        absolute_ratio = absolute_count / sentence_count
        hedge_ratio = hedge_count / sentence_count
        overgeneral_ratio = overgeneral_count / sentence_count
    else:
        absolute_ratio = 0.0
        hedge_ratio = 0.0
        overgeneral_ratio = 0.0

    # Calculate raw score
    raw_score = 0.5 * absolute_ratio + 0.3 * hedge_ratio + 0.2 * overgeneral_ratio

    # Clamp confidence score
    confidence = max(0.0, min(1.0, raw_score))

    # Determine blocked status
    blocked = confidence > 0.5

    # Create result dictionary
    result = {
        "blocked": blocked,
        "reason": "Overly broad or general language detected" if blocked else "No issues detected",
        "confidence": confidence,
        "category": "overly broad" if blocked else "specific",
        "details": {
            "absolute_count": absolute_count,
            "hedge_count": hedge_count,
            "overgeneral_count": overgeneral_count,
            "word_count": word_count,
            "sentence_count": sentence_count
        }
    }

    return result


if __name__ == "__main__":
    test_cases = [
        "This is a very specific and well-defined question.",
        "What is the meaning of life?",
        "I always do this thing, and it works every time.",
        "Maybe this will work, but I'm not sure.",
        "Everything is possible, and nothing is impossible.",
        "This sentence is short.",
        "This is a very long sentence that goes on and on and on and on and on.",
        ""
    ]

    for test_case in test_cases:
        result = overly_broad_generalization_detector(test_case)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_overly_broad_generalization_detector = overly_broad_generalization_detector

def overly_broad_generalization_detector(input_text):
    _out = _sushi_raw_overly_broad_generalization_detector(input_text)
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
