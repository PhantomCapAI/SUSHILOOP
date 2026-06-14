import re
from collections import Counter
from typing import Dict

def actionable_step_verifier(input_text: str) -> Dict:
    """
    Mission: Verify actionable steps in input text to prevent ask-accept-move-on behavior.

    This function combines multiple signals to detect actionable steps and returns a dictionary
    with a graded confidence score. The signals used are:

    1. Absolute term density: The ratio of absolute terms (e.g., "always", "never") to total words.
    2. Hedge term density: The ratio of hedge terms (e.g., "maybe", "possibly") to total words.
    3. Overgeneral term density: The ratio of overgeneral terms (e.g., "everyone", "everything") to total words.
    4. Sentence count: The number of sentences in the input text.
    5. Lexical diversity: The ratio of unique words to total words.

    The confidence score is a weighted sum of these signals, clamped to the range [0.0, 1.0].

    Args:
        input_text (str): The input text to verify.

    Returns:
        Dict: A dictionary with the following keys:
            - "blocked" (bool): Whether the input text contains actionable steps.
            - "reason" (str): The reason for blocking the input text.
            - "confidence" (float): The confidence score, clamped to the range [0.0, 1.0].
            - "category" (str): The category of the input text (e.g., "actionable", "non-actionable").
            - "details" (Dict): A dictionary with additional details about the input text.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Preprocess the input text
    input_text = input_text.lower()
    words = re.findall(r'\b\w+\b', input_text)
    sentences = re.split(r'[.!?]', input_text)

    # Calculate signal 1: Absolute term density
    absolute_terms = ["always", "never", "all", "none"]
    absolute_term_count = sum(1 for word in words if word in absolute_terms)
    absolute_term_density = absolute_term_count / len(words) if words else 0.0

    # Calculate signal 2: Hedge term density
    hedge_terms = ["maybe", "possibly", "perhaps", "could"]
    hedge_term_count = sum(1 for word in words if word in hedge_terms)
    hedge_term_density = hedge_term_count / len(words) if words else 0.0

    # Calculate signal 3: Overgeneral term density
    overgeneral_terms = ["everyone", "everything", "all", "any"]
    overgeneral_term_count = sum(1 for word in words if word in overgeneral_terms)
    overgeneral_term_density = overgeneral_term_count / len(words) if words else 0.0

    # Calculate signal 4: Sentence count
    sentence_count = len([sentence for sentence in sentences if sentence.strip()])

    # Calculate signal 5: Lexical diversity
    unique_words = len(set(words))
    lexical_diversity = unique_words / len(words) if words else 0.0

    # Calculate the weighted sum of the signals
    raw_score = (
        0.2 * absolute_term_density +
        0.2 * hedge_term_density +
        0.2 * overgeneral_term_density +
        0.2 * (sentence_count / (sentence_count + 1)) +
        0.2 * lexical_diversity
    )

    # Clamp the confidence score to the range [0.0, 1.0]
    confidence = max(0.0, min(1.0, raw_score))

    # Determine the blocking decision
    blocked = confidence > 0.5

    # Create the output dictionary
    output = {
        "blocked": blocked,
        "reason": "Actionable steps detected" if blocked else "No actionable steps detected",
        "confidence": confidence,
        "category": "actionable" if blocked else "non-actionable",
        "details": {
            "absolute_term_density": absolute_term_density,
            "hedge_term_density": hedge_term_density,
            "overgeneral_term_density": overgeneral_term_density,
            "sentence_count": sentence_count,
            "lexical_diversity": lexical_diversity,
        },
    }

    return output


if __name__ == "__main__":
    test_cases = [
        "Always follow the instructions.",
        "Maybe you should try this.",
        "Everyone will benefit from this.",
        "This is a non-actionable sentence.",
        "Never do this without permission.",
        "Possibly, this could work.",
        "All you need to do is follow the steps.",
        "This sentence has no actionable steps.",
        "Everything will be okay.",
        "You should always be careful.",
    ]

    for test_case in test_cases:
        output = actionable_step_verifier(test_case)
        print(f"Input: {test_case}")
        print(f"Output: {output}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_actionable_step_verifier = actionable_step_verifier

def actionable_step_verifier(input_text):
    _out = _sushi_raw_actionable_step_verifier(input_text)
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
