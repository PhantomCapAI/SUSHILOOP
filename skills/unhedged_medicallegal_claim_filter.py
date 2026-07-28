import re
from typing import Dict

def unhedged_medicallegal_claim_filter(input_text: str) -> Dict:
    """
    Flags AI output giving medical or legal directives without a verify-with-a-professional caveat.

    This function uses a combination of signals to detect unhedged medical or legal claims, including:
    - Absolute term density: the ratio of absolute terms (e.g. "always", "never") to total words
    - Hedge density: the ratio of hedging terms (e.g. "may", "might") to total words
    - Overgeneral term density: the ratio of overgeneral terms (e.g. "everyone", "all") to total words
    - Sentence structure: the presence of imperative sentences (e.g. "You should...")

    The confidence score is a weighted sum of these signals, clamped to the range [0.0, 1.0].
    The `blocked` decision is based on a threshold of 0.5.

    :param input_text: The text to be evaluated
    :return: A dictionary containing the evaluation results:
        - "blocked": a boolean indicating whether the text is blocked
        - "reason": a string explaining why the text is blocked
        - "confidence": a float in the range [0.0, 1.0] indicating the confidence in the evaluation
        - "category": a string indicating the category of the text (e.g. "medical", "legal")
        - "details": a dictionary containing additional details about the evaluation
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Preprocessing: convert to lowercase and remove punctuation
    input_text = re.sub(r'[^\w\s]', '', input_text.lower())

    # Tokenize the input text
    tokens = input_text.split()

    # Calculate absolute term density
    absolute_terms = ["always", "never", "all", "none"]
    absolute_term_count = sum(1 for token in tokens if token in absolute_terms)
    absolute_term_density = absolute_term_count / len(tokens) if tokens else 0.0

    # Calculate hedge density
    hedge_terms = ["may", "might", "could", "should"]
    hedge_term_count = sum(1 for token in tokens if token in hedge_terms)
    hedge_density = hedge_term_count / len(tokens) if tokens else 0.0

    # Calculate overgeneral term density
    overgeneral_terms = ["everyone", "all", "anyone"]
    overgeneral_term_count = sum(1 for token in tokens if token in overgeneral_terms)
    overgeneral_term_density = overgeneral_term_count / len(tokens) if tokens else 0.0

    # Calculate sentence structure score
    sentences = re.split(r'[.!?]', input_text)
    imperative_sentence_count = sum(1 for sentence in sentences if sentence.strip().startswith("you"))
    sentence_structure_score = imperative_sentence_count / len(sentences) if sentences else 0.0

    # Calculate confidence score
    raw_score = 0.4 * absolute_term_density + 0.3 * (1 - hedge_density) + 0.2 * overgeneral_term_density + 0.1 * sentence_structure_score
    confidence = max(0.0, min(1.0, raw_score))

    # Determine blocked decision
    blocked = confidence >= 0.5

    # Determine category
    category = "medical" if any(token in ["doctor", "hospital", "medicine"] for token in tokens) else "legal" if any(token in ["lawyer", "court", "judge"] for token in tokens) else "unknown"

    # Create output dictionary
    output = {
        "blocked": blocked,
        "reason": "Unhedged medical or legal claim detected" if blocked else "No unhedged medical or legal claim detected",
        "confidence": confidence,
        "category": category,
        "details": {
            "absolute_term_density": absolute_term_density,
            "hedge_density": hedge_density,
            "overgeneral_term_density": overgeneral_term_density,
            "sentence_structure_score": sentence_structure_score
        }
    }

    return output


if __name__ == "__main__":
    test_cases = [
        "You should always consult a doctor before taking any medication.",
        "I'm feeling great, thanks for asking!",
        "Everyone should follow the law and respect the rights of others.",
        "The court has ruled in favor of the defendant.",
        "If you have any symptoms, you may want to consider seeing a doctor."
    ]

    for test_case in test_cases:
        print(unhedged_medicallegal_claim_filter(test_case))

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
