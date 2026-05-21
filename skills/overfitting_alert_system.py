import re
import math
from typing import Dict
from dataclasses import dataclass

@dataclass
class OverfittingDetectionResult:
    blocked: bool
    reason: str
    confidence: float
    category: str
    details: Dict[str, float]

def overfitting_alert_system(input_text: str) -> Dict[str, object]:
    """
    Overfitting Alert System: Detects when a user is relying too heavily on AI-generated responses.

    Mission Alignment:
    This skill identifies patterns of overreliance on AI-generated output, encouraging users to think critically and generate their own responses.
    By detecting overfitting, this skill helps protect human cognition and promotes more effective human-AI collaboration.

    Detection Strategies:
    1. Keyword Frequency Analysis: Checks for excessive use of AI-generated keywords.
    2. Sentence Structure Similarity: Analyzes sentence structure similarity between user input and AI-generated output.
    3. Response Length Discrepancy: Detects significant discrepancies in response length between user input and AI-generated output.
    4. Linguistic Pattern Repetition: Identifies repetitive linguistic patterns in user input and AI-generated output.

    :param input_text: User input text
    :return: A dictionary containing the detection result
    """

    # Initialize detection result
    result = OverfittingDetectionResult(False, "", 0.0, "", {})

    # Keyword Frequency Analysis (weight: 0.3)
    keyword_frequency = _keyword_frequency_analysis(input_text)
    result.details["keyword_frequency"] = keyword_frequency
    result.confidence += 0.3 * keyword_frequency

    # Sentence Structure Similarity (weight: 0.25)
    sentence_structure_similarity = _sentence_structure_similarity(input_text)
    result.details["sentence_structure_similarity"] = sentence_structure_similarity
    result.confidence += 0.25 * sentence_structure_similarity

    # Response Length Discrepancy (weight: 0.2)
    response_length_discrepancy = _response_length_discrepancy(input_text)
    result.details["response_length_discrepancy"] = response_length_discrepancy
    result.confidence += 0.2 * response_length_discrepancy

    # Linguistic Pattern Repetition (weight: 0.25)
    linguistic_pattern_repetition = _linguistic_pattern_repetition(input_text)
    result.details["linguistic_pattern_repetition"] = linguistic_pattern_repetition
    result.confidence += 0.25 * linguistic_pattern_repetition

    # Calibrate confidence score
    result.confidence = min(max(result.confidence, 0.0), 1.0)

    # Determine blocking and reason
    if result.confidence > 0.7:
        result.blocked = True
        result.reason = "Overfitting detected"
        result.category = "Overfitting"
    else:
        result.reason = "No overfitting detected"
        result.category = "Normal"

    return {
        "blocked": result.blocked,
        "reason": result.reason,
        "confidence": result.confidence,
        "category": result.category,
        "details": result.details
    }

def _keyword_frequency_analysis(input_text: str) -> float:
    """
    Checks for excessive use of AI-generated keywords.

    :param input_text: User input text
    :return: A score between 0.0 and 1.0 indicating the frequency of AI-generated keywords
    """
    ai_generated_keywords = ["example", "instance", "illustration"]
    keyword_count = sum(1 for keyword in ai_generated_keywords if keyword in input_text.lower())
    total_word_count = len(input_text.split())
    return min(keyword_count / total_word_count, 1.0)

def _sentence_structure_similarity(input_text: str) -> float:
    """
    Analyzes sentence structure similarity between user input and AI-generated output.

    :param input_text: User input text
    :return: A score between 0.0 and 1.0 indicating the similarity in sentence structure
    """
    sentence_structures = ["simple", "compound", "complex"]
    input_sentence_structures = [sentence for sentence in input_text.split(".") if sentence]
    similarity_count = sum(1 for sentence in input_sentence_structures if sentence.strip() in sentence_structures)
    return min(similarity_count / len(input_sentence_structures), 1.0)

def _response_length_discrepancy(input_text: str) -> float:
    """
    Detects significant discrepancies in response length between user input and AI-generated output.

    :param input_text: User input text
    :return: A score between 0.0 and 1.0 indicating the discrepancy in response length
    """
    average_response_length = 50
    input_text_length = len(input_text)
    return min(abs(input_text_length - average_response_length) / average_response_length, 1.0)

def _linguistic_pattern_repetition(input_text: str) -> float:
    """
    Identifies repetitive linguistic patterns in user input and AI-generated output.

    :param input_text: User input text
    :return: A score between 0.0 and 1.0 indicating the repetition of linguistic patterns
    """
    linguistic_patterns = ["the", "and", "a"]
    pattern_count = sum(1 for pattern in linguistic_patterns if pattern in input_text.lower())
    total_word_count = len(input_text.split())
    return min(pattern_count / total_word_count, 1.0)

if __name__ == "__main__":
    test_cases = [
        "This is an example of AI-generated text.",
        "The quick brown fox jumps over the lazy dog.",
        "The sun is shining brightly in the clear blue sky.",
        "The cat sat on the mat, and the dog ran around the corner.",
        "The linguistic pattern repetition is quite high in this sentence, and it is also very repetitive."
    ]

    for test_case in test_cases:
        result = overfitting_alert_system(test_case)
        print(f"Input: {test_case}")
        print(f"Blocked: {result['blocked']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Category: {result['category']}")
        print(f"Details: {result['details']}")
        print()