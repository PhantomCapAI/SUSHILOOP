import re
import math
from typing import Dict
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class QueryHistory:
    timestamp: datetime
    text: str

def calculate_absolutes_ratio(text: str) -> float:
    """Calculate the ratio of absolute terms in the input text."""
    absolute_terms = re.findall(r'\b(always|never|every|all)\b', text, re.IGNORECASE)
    words = re.findall(r'\b\w+\b', text)
    return len(absolute_terms) / len(words) if words else 0.0

def calculate_hedge_density(text: str) -> float:
    """Calculate the density of hedge terms in the input text."""
    hedge_terms = re.findall(r'\b(maybe|perhaps|possibly|likely|unlikely)\b', text, re.IGNORECASE)
    words = re.findall(r'\b\w+\b', text)
    return len(hedge_terms) / len(words) if words else 0.0

def calculate_overgeneral_terms(text: str) -> float:
    """Calculate the ratio of overgeneral terms in the input text."""
    overgeneral_terms = re.findall(r'\b(everyone|everything|always|never)\b', text, re.IGNORECASE)
    words = re.findall(r'\b\w+\b', text)
    return len(overgeneral_terms) / len(words) if words else 0.0

def calculate_lexical_diversity(text: str) -> float:
    """Calculate the lexical diversity of the input text."""
    words = re.findall(r'\b\w+\b', text)
    unique_words = set(words)
    return len(unique_words) / len(words) if words else 0.0

def rapid_fire_query_limiter(input_text: str) -> Dict:
    """
    Detects and limits consecutive queries to the AI model within a short time frame.

    This function combines multiple signals to detect rapid-fire queries and imposes a cooldown period.
    It encourages humans to pause, reflect, and consider their own thoughts and opinions.

    Args:
        input_text (str): The input text to be evaluated.

    Returns:
        Dict: A dictionary containing the result of the evaluation.
            - "blocked" (bool): Whether the query is blocked.
            - "reason" (str): The reason for blocking the query.
            - "confidence" (float): The confidence level of the detection.
            - "category" (str): The category of the detection.
            - "details" (dict): Additional details about the detection.
    """
    # SUSHILOOP input guard (auto-injected): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    # Initialize query history
    query_history = []

    # Load query history from memory (for demonstration purposes only)
    # In a real-world application, this data would be stored in a database or file
    query_history.append(QueryHistory(datetime.now() - timedelta(minutes=3), "What is the meaning of life?"))
    query_history.append(QueryHistory(datetime.now() - timedelta(minutes=2), "What is the purpose of existence?"))
    query_history.append(QueryHistory(datetime.now() - timedelta(minutes=1), "What is the nature of reality?"))

    # Calculate signals
    absolutes_ratio = calculate_absolutes_ratio(input_text)
    hedge_density = calculate_hedge_density(input_text)
    overgeneral_terms = calculate_overgeneral_terms(input_text)
    lexical_diversity = calculate_lexical_diversity(input_text)

    # Calculate confidence
    raw_score = 0.5 * absolutes_ratio + 0.3 * hedge_density + 0.2 * overgeneral_terms
    confidence = max(0.0, min(1.0, raw_score))

    # Check for rapid-fire queries
    recent_queries = [query for query in query_history if (datetime.now() - query.timestamp).total_seconds() / 60 < 5]
    if len(recent_queries) >= 3:
        # Imposes a 10-minute cooldown period
        cooldown_period = 10
        last_query = max(recent_queries, key=lambda query: query.timestamp)
        time_since_last_query = (datetime.now() - last_query.timestamp).total_seconds() / 60
        if time_since_last_query < cooldown_period:
            return {
                "blocked": True,
                "reason": "Rapid-fire query detected",
                "confidence": confidence,
                "category": "Rapid Fire Query",
                "details": {
                    "absolutes_ratio": absolutes_ratio,
                    "hedge_density": hedge_density,
                    "overgeneral_terms": overgeneral_terms,
                    "lexical_diversity": lexical_diversity,
                    "time_since_last_query": time_since_last_query
                }
            }

    # Allow humans to override the limit with a manual confirmation step
    # For demonstration purposes only, this is a simple text-based confirmation
    # In a real-world application, this would be a more robust confirmation mechanism
    override = input("Override rapid-fire query limit? (yes/no): ")
    if override.lower() == "yes":
        return {
            "blocked": False,
            "reason": "Override confirmed",
            "confidence": confidence,
            "category": "Rapid Fire Query",
            "details": {
                "absolutes_ratio": absolutes_ratio,
                "hedge_density": hedge_density,
                "overgeneral_terms": overgeneral_terms,
                "lexical_diversity": lexical_diversity
            }
        }

    return {
        "blocked": False,
        "reason": "No rapid-fire query detected",
        "confidence": confidence,
        "category": "Rapid Fire Query",
        "details": {
            "absolutes_ratio": absolutes_ratio,
            "hedge_density": hedge_density,
            "overgeneral_terms": overgeneral_terms,
            "lexical_diversity": lexical_diversity
        }
    }

if __name__ == "__main__":
    test_cases = [
        "What is the meaning of life?",
        "What is the purpose of existence?",
        "What is the nature of reality?",
        "This is a test query",
        "Another test query"
    ]

    for test_case in test_cases:
        result = rapid_fire_query_limiter(test_case)
        print(result)

# SUSHILOOP contract normalizer (auto): clamp confidence into [0,1], guarantee dict shape
_sushi_raw_rapid_fire_query_limiter = rapid_fire_query_limiter

def rapid_fire_query_limiter(input_text):
    _out = _sushi_raw_rapid_fire_query_limiter(input_text)
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
