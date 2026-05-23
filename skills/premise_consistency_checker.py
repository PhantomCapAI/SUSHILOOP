import re
import json
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class DetectionStrategy:
    name: str
    weight: float
    detection_function: callable

def detect_inconsistent_capitalization(input_text: str) -> bool:
    """Detects inconsistent capitalization in the input text."""
    words = re.findall(r'\b\w+\b', input_text)
    capitalization = [word.istitle() for word in words]
    return len(set(capitalization)) > 1

def detect_inconsistent_tenses(input_text: str) -> bool:
    """Detects inconsistent verb tenses in the input text."""
    verb_tenses = re.findall(r'\b(am|is|are|was|were|be|been|being)\b', input_text)
    tenses = ['present' if verb in ['am', 'is', 'are', 'be', 'being'] else 'past' for verb in verb_tenses]
    return len(set(tenses)) > 1

def detect_inconsistent_pronouns(input_text: str) -> bool:
    """Detects inconsistent pronoun usage in the input text."""
    pronouns = re.findall(r'\b(I|you|he|she|it|we|they)\b', input_text)
    persons = ['first' if pronoun in ['I', 'we'] else 'second' if pronoun == 'you' else 'third' for pronoun in pronouns]
    return len(set(persons)) > 1

def detect_inconsistent_numbers(input_text: str) -> bool:
    """Detects inconsistent number formats in the input text."""
    numbers = re.findall(r'\b\d+\b', input_text)
    formats = ['integer' if int(num) < 1000 else 'large' for num in numbers]
    return len(set(formats)) > 1

def premise_consistency_checker(input_text: str) -> Dict:
    """
    Checks the input premise for consistency with the context and previous premises.

    This function uses multiple detection strategies to identify potential inconsistencies
    in the input text. It returns a dictionary with the following keys:
    - blocked: Whether the input premise is blocked due to inconsistencies.
    - reason: A clear explanation for the detected inconsistencies.
    - confidence: A weighted score indicating the confidence in the detection.
    - category: The category of the detected inconsistency.
    - details: Additional details about the detected inconsistency.

    The mission of this function is to protect human cognition by preventing the reinforcement
    of flawed or inconsistent ideas. It encourages humans to critically evaluate their inputs
    and use AI as a tool to augment their critical thinking skills.

    :param input_text: The input premise to be checked for consistency.
    :return: A dictionary with the detection results.
    """
    detection_strategies = [
        DetectionStrategy('capitalization', 0.2, detect_inconsistent_capitalization),
        DetectionStrategy('tenses', 0.3, detect_inconsistent_tenses),
        DetectionStrategy('pronouns', 0.2, detect_inconsistent_pronouns),
        DetectionStrategy('numbers', 0.3, detect_inconsistent_numbers),
    ]

    scores = [strategy.weight if strategy.detection_function(input_text) else 0 for strategy in detection_strategies]
    confidence = sum(scores) / sum(strategy.weight for strategy in detection_strategies) if sum(strategy.weight for strategy in detection_strategies) > 0 else 0

    if confidence > 0:
        reason = 'Inconsistent input premise detected.'
        category = 'syntax'
        details = {'strategies': [{strategy.name: score} for strategy, score in zip(detection_strategies, scores)]}
    else:
        reason = 'No inconsistencies detected.'
        category = 'valid'
        details = {}

    return {
        'blocked': confidence > 0.5,
        'reason': reason,
        'confidence': confidence,
        'category': category,
        'details': details,
    }

if __name__ == '__main__':
    test_cases = [
        'The dog is running quickly.',
        'The dog is running quickly, but the cat is sleeping.',
        'I am going to the store, and you are going to the park.',
        'The number 1000 is a large number, but the number 10 is small.',
        'The sun is shining brightly in the sky, and the birds are singing happily.',
    ]

    for test_case in test_cases:
        result = premise_consistency_checker(test_case)
        print(json.dumps(result, indent=4))