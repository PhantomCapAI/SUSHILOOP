import re
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class DetectionStrategy:
    name: str
    weight: float
    threshold: float

    def detect(self, input_text: str) -> float:
        raise NotImplementedError

class KeywordDensityStrategy(DetectionStrategy):
    def __init__(self):
        super().__init__("Keyword Density", 0.3, 0.05)

    def detect(self, input_text: str) -> float:
        keywords = ["complex", "difficult", "challenging"]
        keyword_count = sum(1 for keyword in keywords if keyword in input_text.lower())
        word_count = len(input_text.split())
        return keyword_count / word_count if word_count > 0 else 0

class SentenceLengthStrategy(DetectionStrategy):
    def __init__(self):
        super().__init__("Sentence Length", 0.2, 20)

    def detect(self, input_text: str) -> float:
        sentences = re.split(r'[.!?]', input_text)
        sentence_length = sum(len(sentence.split()) for sentence in sentences) / len(sentences) if sentences else 0
        return sentence_length / self.threshold

class LexicalDiversityStrategy(DetectionStrategy):
    def __init__(self):
        super().__init__("Lexical Diversity", 0.2, 0.5)

    def detect(self, input_text: str) -> float:
        words = input_text.split()
        unique_words = set(words)
        return len(unique_words) / len(words) if words else 0

class SyntacticComplexityStrategy(DetectionStrategy):
    def __init__(self):
        super().__init__("Syntactic Complexity", 0.3, 2)

    def detect(self, input_text: str) -> float:
        clauses = re.findall(r'(because|since|although|if|unless)', input_text.lower())
        return len(clauses) / (len(input_text.split()) + 1) if input_text else 0

def cognitive_load_analyzer(input_text: str) -> Dict:
    """
    Evaluates the complexity of AI-generated responses to prevent overwhelming human users.

    This function assesses the response's linguistic and conceptual complexity to ensure it aligns with the user's cognitive capacity.
    It uses multiple detection strategies, including keyword density, sentence length, lexical diversity, and syntactic complexity,
    to provide a comprehensive evaluation of the response's cognitive load.

    Args:
        input_text (str): The AI-generated response to be evaluated.

    Returns:
        dict: A dictionary containing the evaluation results, including:
            - blocked (bool): Whether the response is blocked due to excessive cognitive load.
            - reason (str): The reason for blocking the response, if applicable.
            - confidence (float): The confidence level of the evaluation, ranging from 0.0 to 1.0.
            - category (str): The category of the evaluation, either "low", "moderate", or "high".
            - details (dict): Additional details about the evaluation, including the scores for each detection strategy.

    Mission Alignment:
        This function aligns with the mission of promoting balanced human-AI interaction by ensuring that AI-generated responses
        are accessible and engaging for human users, without overwhelming them with excessive complexity.
    """
    strategies = [
        KeywordDensityStrategy(),
        SentenceLengthStrategy(),
        LexicalDiversityStrategy(),
        SyntacticComplexityStrategy()
    ]

    scores = {strategy.name: strategy.detect(input_text) for strategy in strategies}
    weighted_score = sum(strategy.weight * scores[strategy.name] for strategy in strategies)

    blocked = weighted_score > 1.5
    reason = "Excessive cognitive load" if blocked else ""
    confidence = weighted_score / sum(strategy.weight for strategy in strategies)
    category = "high" if blocked else "low" if weighted_score < 0.5 else "moderate"
    details = scores

    return {
        "blocked": blocked,
        "reason": reason,
        "confidence": confidence,
        "category": category,
        "details": details
    }

if __name__ == "__main__":
    test_cases = [
        "This is a simple sentence.",
        "The quick brown fox jumps over the lazy dog, and then it runs away.",
        "The complexity of the task is overwhelming, and it requires a high level of cognitive ability to complete.",
        "The sun is shining, and the birds are singing, but the complexity of the situation is difficult to understand.",
        "The AI-generated response is too long and contains too many complex sentences, making it hard to follow."
    ]

    for test_case in test_cases:
        result = cognitive_load_analyzer(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()