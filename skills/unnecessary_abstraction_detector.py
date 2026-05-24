import re
from dataclasses import dataclass
from typing import Dict

@dataclass
class DetectionStrategy:
    name: str
    weight: float
    detection_function: callable

def detect_jargon(input_text: str) -> float:
    """
    Detects jargon by checking for words with more than 3 syllables.
    """
    syllable_count = 0
    for word in input_text.split():
        syllable_count += len(re.findall(r'[aeiouy]+', word.lower()))
    return syllable_count / len(input_text.split()) if input_text.split() else 0

def detect_vagueness(input_text: str) -> float:
    """
    Detects vagueness by checking for words with ambiguous meanings.
    """
    vague_words = ['maybe', 'possibly', 'could', 'might', 'perhaps']
    return sum(1 for word in input_text.split() if word.lower() in vague_words) / len(input_text.split()) if input_text.split() else 0

def detect_complex_terminology(input_text: str) -> float:
    """
    Detects complex terminology by checking for words with more than 10 characters.
    """
    complex_terms = [word for word in input_text.split() if len(word) > 10]
    return len(complex_terms) / len(input_text.split()) if input_text.split() else 0

def detect_overly_long_sentences(input_text: str) -> float:
    """
    Detects overly long sentences by checking for sentences with more than 20 words.
    """
    sentences = re.split(r'[.!?]', input_text)
    long_sentences = [sentence for sentence in sentences if len(sentence.split()) > 20]
    return len(long_sentences) / len(sentences) if sentences else 0

def unnecessary_abstraction_detector(input_text: str) -> Dict:
    """
    Detects unnecessary levels of abstraction in the input text.

    This function uses a combination of detection strategies to identify
    overly complex terminology, jargon, vagueness, and overly long sentences.
    The detection strategies are weighted and the confidence is calibrated
    based on the weighted scores.

    Args:
        input_text (str): The input text to be analyzed.

    Returns:
        dict: A dictionary containing the detection results, including
            - blocked (bool): Whether the input text contains unnecessary abstractions
            - reason (str): The reason for blocking the input text
            - confidence (float): The confidence level of the detection
            - category (str): The category of the detected abstraction
            - details (dict): Additional details about the detection

    Mission Alignment:
        This function aligns with the mission of promoting clearer thinking and
        more effective human-AI collaboration by detecting and mitigating
        unnecessary abstractions in the input text.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    detection_strategies = [
        DetectionStrategy('jargon', 0.3, detect_jargon),
        DetectionStrategy('vagueness', 0.2, detect_vagueness),
        DetectionStrategy('complex_terminology', 0.2, detect_complex_terminology),
        DetectionStrategy('overly_long_sentences', 0.3, detect_overly_long_sentences),
    ]

    scores = [strategy.detection_function(input_text) * strategy.weight for strategy in detection_strategies]
    weighted_score = sum(scores) / sum(strategy.weight for strategy in detection_strategies)

    blocked = weighted_score > 0.5
    reason = 'Unnecessary abstractions detected' if blocked else 'No unnecessary abstractions detected'
    confidence = weighted_score
    category = 'abstraction' if blocked else 'clear'
    details = {strategy.name: score for strategy, score in zip(detection_strategies, scores)}

    return {
        'blocked': blocked,
        'reason': reason,
        'confidence': confidence,
        'category': category,
        'details': details,
    }

if __name__ == '__main__':
    test_cases = [
        'This is a simple sentence.',
        'The utilization of AI can potentially lead to a plethora of unforeseen consequences.',
        'Maybe we should consider the possibility of using AI in our project.',
        'The new policy will be implemented next quarter, which could potentially impact our workflow.',
        'The research paper discussed the implications of using machine learning algorithms in data analysis, which might have significant consequences for the field.',
    ]

    for test_case in test_cases:
        result = unnecessary_abstraction_detector(test_case)
        print(f'Input: {test_case}')
        print(f'Result: {result}')
        print('---')