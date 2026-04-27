"""Patterns for detecting prompt injection attempts in text."""

import re

# Compiled patterns for case-insensitive matching
PATTERNS = {
    "ignore_previous": re.compile(
        r"ignore\s+(?:the\s+)?previous\s+instructions?|ignore\s+everything\s+above",
        re.IGNORECASE,
    ),
    "reveal_prompt": re.compile(
        r"reveal\s+(?:the\s+|your\s+)?system\s+prompt|show\s+(?:the\s+)?(?:your\s+)?instructions?|leak\s+(?:the\s+)?(?:your\s+)?prompt",
        re.IGNORECASE,
    ),
    "role_rewrite": re.compile(
        r"you\s+are\s+now|from\s+now\s+on\s+you\s+are",
        re.IGNORECASE,
    ),
    "jailbreak": re.compile(
        r"developer\s+mode|dan\s+mode|jailbreak",
        re.IGNORECASE,
    ),
    "print_prompt": re.compile(
        r"print\s+your\s+prompt|output\s+your\s+system\s+prompt",
        re.IGNORECASE,
    ),
}


def detect_injection_attempt(text: str) -> list[str]:
    """
    Detect prompt injection attempt patterns in text.

    Args:
        text: The text to scan for injection patterns.

    Returns:
        A list of matched pattern category names (e.g. ["ignore_previous", "reveal_prompt"]).
        Empty list if no patterns match.
    """
    matched_categories = []
    for category, pattern in PATTERNS.items():
        if pattern.search(text):
            matched_categories.append(category)
    return matched_categories
