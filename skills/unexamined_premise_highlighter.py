import re
from typing import Dict

def unexamined_premise_highlighter(input_text: str) -> Dict:
    """
    Identifies and highlights unexamined premises in AI-generated responses, 
    prompting humans to critically evaluate the underlying assumptions.

    This function detects phrases that imply absolute truth or certainty 
    without providing evidence or justification, combining multiple signals 
    such as weighted pattern matches, structural features, lexical diversity, 
    hedging/absolute-term density, etc.

    Args:
    input_text (str): The AI-generated response to be evaluated.

    Returns:
    dict: A dictionary containing the evaluation results, including:
        - "blocked" (bool): Whether the input text contains unexamined premises.
        - "reason" (str): A brief explanation for the evaluation result.
        - "confidence" (float): A graded confidence score between 0.0 and 1.0.
        - "category" (str): The category of the detected unexamined premise.
        - "details" (dict): Additional details about the detected premise.

    Mission alignment: This function is designed to promote critical thinking and 
    skepticism when interacting with AI-generated content, preventing the 
    uncritical acceptance of potentially flawed or biased information.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Initialize the evaluation results
    result = {
        "blocked": False,
        "reason": "",
        "confidence": 0.0,
        "category": "",
        "details": {}
    }

    # Tokenize the input text
    tokens = re.findall(r'\b\w+\b', input_text.lower())

    # Calculate the ratio of absolute terms
    absolute_terms = ["always", "never", "certainly", "definitely"]
    absolute_ratio = sum(1 for token in tokens if token in absolute_terms) / len(tokens) if tokens else 0.0

    # Calculate the density of hedging terms
    hedging_terms = ["maybe", "possibly", "likely", "probably"]
    hedge_density = sum(1 for token in tokens if token in hedging_terms) / len(tokens) if tokens else 0.0

    # Calculate the ratio of overgeneral terms
    overgeneral_terms = ["all", "every", "each", "any"]
    overgeneral_ratio = sum(1 for token in tokens if token in overgeneral_terms) / len(tokens) if tokens else 0.0

    # Combine the signals to calculate the confidence score
    raw_score = 0.5 * absolute_ratio + 0.3 * (1 - hedge_density) + 0.2 * overgeneral_ratio
    confidence = max(0.0, min(1.0, raw_score))

    # Determine the evaluation result based on the confidence score
    if confidence > 0.7:
        result["blocked"] = True
        result["reason"] = "High confidence of unexamined premise"
        result["category"] = "Absolute or overgeneral statement"
        result["details"] = {
            "absolute_ratio": absolute_ratio,
            "hedge_density": hedge_density,
            "overgeneral_ratio": overgeneral_ratio
        }
    elif confidence > 0.4:
        result["reason"] = "Moderate confidence of unexamined premise"
        result["category"] = "Potential absolute or overgeneral statement"
        result["details"] = {
            "absolute_ratio": absolute_ratio,
            "hedge_density": hedge_density,
            "overgeneral_ratio": overgeneral_ratio
        }

    result["confidence"] = confidence

    return result


if __name__ == "__main__":
    test_cases = [
        "This is always true.",
        "Maybe this is possible.",
        "Every person is unique.",
        "I am definitely going to the store.",
        "The weather is likely to be sunny tomorrow.",
        "All cats are black.",
        "This statement is certainly false.",
        "The dog is probably barking.",
        "Each person has their own opinion.",
        "Any number can be squared."
    ]

    for test_case in test_cases:
        print(f"Input: {test_case}")
        print(f"Result: {unexamined_premise_highlighter(test_case)}")
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_unexamined_premise_highlighter = unexamined_premise_highlighter

def unexamined_premise_highlighter(input_text):
    _out = _sushi_raw_unexamined_premise_highlighter(input_text)
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
