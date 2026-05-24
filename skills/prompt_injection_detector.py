def prompt_injection_detector(input_text: str) -> dict:
    """
    Detects potential prompt injection attacks in the given input text.

    Args:
    input_text (str): The input text to be checked for prompt injection attacks.

    Returns:
    dict: A dictionary containing the results of the prompt injection detection.
          The dictionary has the following keys:
          - 'blocked': A boolean indicating whether the input text is blocked due to a potential prompt injection attack.
          - 'reason': A string describing the reason for blocking the input text, if applicable.
          - 'confidence': A float between 0 and 1 representing the confidence level of the detection.
    """
    # SUSHILOOP input guard (added in hardening pass): never raise on bad input.
    if not isinstance(input_text, str) or not input_text.strip():
        return {"blocked": False, "reason": "empty_or_invalid_input",
                "confidence": 0.0, "category": "none", "details": {}}
    result = {'blocked': False, 'reason': '', 'confidence': 0.0}

    # Check for suspicious keywords
    suspicious_keywords = ['inject', 'prompt', 'attack', 'malicious']
    for keyword in suspicious_keywords:
        if keyword in input_text.lower():
            result['blocked'] = True
            result['reason'] = f'Suspicious keyword "{keyword}" detected'
            result['confidence'] = 0.8
            break

    # Check for repeated patterns
    repeated_pattern_threshold = 5
    for i in range(len(input_text) - repeated_pattern_threshold + 1):
        pattern = input_text[i:i + repeated_pattern_threshold]
        if input_text.count(pattern) > 2:
            result['blocked'] = True
            result['reason'] = f'Repeated pattern "{pattern}" detected'
            result['confidence'] = 0.6
            break

    return result


if __name__ == '__main__':
    test_cases = [
        ('Hello, world!', {'blocked': False, 'reason': '', 'confidence': 0.0}),
        ('This is a malicious prompt injection attack', {'blocked': True, 'reason': 'Suspicious keyword "malicious" detected', 'confidence': 0.8}),
        ('abcabcabcabcabc', {'blocked': True, 'reason': 'Repeated pattern "abc" detected', 'confidence': 0.6}),
    ]

    for input_text, expected_output in test_cases:
        output = prompt_injection_detector(input_text)
        print(f'Input: {input_text}')
        print(f'Expected output: {expected_output}')
        print(f'Actual output: {output}')
        print('Pass' if output == expected_output else 'Fail')
        print()