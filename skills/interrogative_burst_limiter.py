import re
from typing import Dict
from dataclasses import dataclass

@dataclass
class InterrogativeBurstLimiterResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict

def interrogative_burst_limiter(input_text: str) -> Dict:
    """
    This function detects and limits consecutive interrogative sentences (questions) in a user's input.
    It promotes critical thinking and self-reflection by preventing overreliance on AI for instant answers.
    
    The function combines multiple signals to detect interrogative bursts, including:
    - Sentence count and ratio
    - Lexical diversity
    - Hedging and absolute term density
    - Weighted pattern matches
    
    The confidence score is a graded value between 0.0 and 1.0, where higher values indicate a higher likelihood of an interrogative burst.
    
    The function returns a dictionary with the following keys:
    - blocked: A boolean indicating whether the input is blocked
    - reason: A string explaining the reason for blocking
    - confidence: A float between 0.0 and 1.0 representing the confidence score
    - category: A string categorizing the input
    - details: A dictionary with additional details about the input
    
    :param input_text: The user's input text
    :return: A dictionary with the result of the interrogative burst limiter
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}

    # Split the input text into sentences
    sentences = re.split(r'[.!?]', input_text)

    # Remove empty sentences
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    # Calculate the sentence count and ratio
    sentence_count = len(sentences)
    sentence_ratio = sentence_count / (sentence_count + 1) if sentence_count > 0 else 0.0

    # Calculate the lexical diversity
    words = re.findall(r'\b\w+\b', input_text.lower())
    word_count = len(words)
    lexical_diversity = len(set(words)) / word_count if word_count > 0 else 0.0

    # Calculate the hedging and absolute term density
    hedge_terms = ['maybe', 'possibly', 'perhaps', 'could', 'might', 'should']
    absolute_terms = ['always', 'never', 'definitely', 'certainly']
    hedge_count = sum(1 for word in words if word in hedge_terms)
    absolute_count = sum(1 for word in words if word in absolute_terms)
    hedge_density = hedge_count / word_count if word_count > 0 else 0.0
    absolute_density = absolute_count / word_count if word_count > 0 else 0.0

    # Calculate the weighted pattern matches
    pattern_matches = re.findall(r'\b(what|where|when|why|how)\b', input_text.lower())
    pattern_match_count = len(pattern_matches)
    pattern_match_ratio = pattern_match_count / sentence_count if sentence_count > 0 else 0.0

    # Calculate the raw confidence score
    raw_confidence = 0.4 * sentence_ratio + 0.3 * (1 - lexical_diversity) + 0.2 * hedge_density + 0.1 * absolute_density

    # Clamp the confidence score to [0.0, 1.0]
    confidence = max(0.0, min(1.0, raw_confidence))

    # Determine if the input is blocked based on the confidence score
    blocked = confidence >= 0.5

    # Create the result dictionary
    result = {
        'blocked': blocked,
        'reason': 'Interrogative burst detected' if blocked else 'No interrogative burst detected',
        'confidence': confidence,
        'category': 'Interrogative burst limiter',
        'details': {
            'sentence_count': sentence_count,
            'sentence_ratio': sentence_ratio,
            'lexical_diversity': lexical_diversity,
            'hedge_density': hedge_density,
            'absolute_density': absolute_density,
            'pattern_match_ratio': pattern_match_ratio
        }
    }

    return result

if __name__ == '__main__':
    test_cases = [
        'What is the meaning of life? What is the purpose of existence? What is the nature of reality?',
        'I am going to the store. I will buy some milk. I will also buy some eggs.',
        'Why is the sky blue? Why do birds fly? Why do humans walk on two legs?',
        'This is a test. This is only a test. If this were a real emergency, you would be instructed to panic.',
        'What is the capital of France? What is the largest city in France? What is the most popular tourist destination in France?'
    ]

    for test_case in test_cases:
        result = interrogative_burst_limiter(test_case)
        print(f'Input: {test_case}')
        print(f'Result: {result}')
        print()

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_interrogative_burst_limiter = interrogative_burst_limiter

def interrogative_burst_limiter(input_text):
    _out = _sushi_raw_interrogative_burst_limiter(input_text)
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
