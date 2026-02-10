import re
from datetime import datetime


# --------------------------------------------------
# BASIC YES / NO
# --------------------------------------------------

def is_yes(text: str) -> bool:
    text = text.lower()
    return any(
        k in text for k in [
            "yes",
            "yeah",
            "yep",
            "ok",
            "okay",
            "sure",
            "fine",
            "correct",
        ]
    )


def is_no(text: str) -> bool:
    text = text.lower()
    return any(
        k in text for k in [
            "no",
            "nope",
            "not",
            "don't",
            "do not",
            "won't",
            "cannot",
            "can't",
        ]
    )


# --------------------------------------------------
# AVAILABILITY / UNAVAILABILITY
# --------------------------------------------------

def is_unavailable(text: str) -> bool:
    """
    Detects user saying they are NOT available on any date
    """
    text = text.lower()
    phrases = [
        "not available",
        "not free",
        "cannot receive",
        "can't receive",
        "won't be available",
        "none of these",
        "no dates work",
        "busy",
        "out of town",
        "not possible",
    ]
    return any(p in text for p in phrases)


# --------------------------------------------------
# DATE EXTRACTION
# --------------------------------------------------

def extract_date(text: str, available_dates: list[str]) -> str | None:
    """
    Match spoken date with available dates
    """
    text = text.lower()

    for date in available_dates:
        if date.lower() in text:
            return date

    # Try loose matching like "25th", "25"
    numbers = re.findall(r"\d{1,2}", text)
    for num in numbers:
        for date in available_dates:
            if num in date:
                return date

    return None


def extract_person_name(text: str) -> str:
    """
    Extracts name from phrases like:
    - "name is Neha"
    - "security is Neha"
    - "neighbor Neha"
    """
    text = text.lower()

    match = re.search(
        r"(name is|security is|neighbor is|is)\s+([a-zA-Z]+)",
        text
    )

    if match:
        return match.group(2).title()

    return ""
