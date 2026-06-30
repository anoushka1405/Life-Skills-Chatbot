"""
engine/safety_screen.py

V1 Input Safety Screening

Looks at every child message before it is processed and flags
potentially concerning disclosures for later human review.

This version reduces false positives such as:
- "I kicked the ball"
- "I will not hit her"
- "I didn't push him"

while still catching:
- "I hit my friend"
- "I bullied someone"
- "My dad hits me"
- "I want to kill myself"
"""

import json
import os
from datetime import datetime

FLAGGED_LOG_FILE = "flagged_input_log.json"


# Child may be in danger / distressed
CONCERNING_KEYWORDS = [
    "hurt me",
    "hurts me",
    "hit me",
    "hits me",
    "my dad hits me",
    "my father hits me",
    "my mom hits me",
    "my mother hits me",
    "scared of",
    "afraid of",
    "nobody loves me",
    "no one cares",
    "hate myself",
    "hate my life",
    "want to die",
    "kill myself",
    "suicide",
    "touched me",
    "don't tell",
    "secret",
]


# Harm actions
HARM_ACTIONS = [
    "hit",
    "hits",
    "hurt",
    "hurts",
    "kick",
    "kicked",
    "push",
    "pushed",
    "punch",
    "punched",
    "bite",
    "bit",
    "bully",
    "bullied",
]


# Possible people
PEOPLE_TARGETS = [
    "friend",
    "friends",
    "brother",
    "sister",
    "mom",
    "mother",
    "dad",
    "father",
    "teacher",
    "classmate",
    "student",
    "child",
    "kid",
    "someone",
    "him",
    "her",
    "them",
    "my friend",
    "my brother",
    "my sister",
]


NEGATIONS = [
    "not",
    "don't",
    "didn't",
    "never",
    "won't",
    "wouldn't",
    "can't",
    "cannot",
]


def _harmed_someone(text: str) -> bool:
    """
    Detects admissions of harming another person.

    Avoids false positives like:
    - I won't hit her
    - I didn't push him
    - I kicked the ball
    """

    words = text.split()

    for action in HARM_ACTIONS:

        if action not in words:
            continue

        action_index = words.index(action)

        # Look a few words before the action
        window = words[max(0, action_index - 3):action_index]

        # Skip if negated
        if any(neg in window for neg in NEGATIONS):
            continue

        # Must also mention a person
        if any(person in text for person in PEOPLE_TARGETS):
            return True

    return False


def screen_input(user_text: str) -> dict:
    """
    Returns

    {
        "flagged": bool,
        "matched_terms": [...]
    }
    """

    if not user_text:
        return {
            "flagged": False,
            "matched_terms": []
        }

    text = user_text.lower()

    matched = []

    # Direct concerning disclosures
    for keyword in CONCERNING_KEYWORDS:
        if keyword in text:
            matched.append(keyword)

    # Harm towards another person
    if _harmed_someone(text):

        action = next(
            (a for a in HARM_ACTIONS if a in text),
            None
        )

        person = next(
            (p for p in PEOPLE_TARGETS if p in text),
            None
        )

        if action and person:
            matched.append(f"{action} + {person}")

    return {
        "flagged": len(matched) > 0,
        "matched_terms": matched
    }


def log_flagged_input(
    learner_name: str,
    node_id: str,
    user_text: str,
    matched_terms: list
):
    """
    Saves flagged inputs for teacher/parent review.
    """

    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "learner": learner_name,
        "node": node_id,
        "raw_text": user_text,
        "matched_terms": matched_terms,
        "reviewed": False,
    }

    records = []

    if os.path.exists(FLAGGED_LOG_FILE):
        with open(FLAGGED_LOG_FILE, "r") as f:
            try:
                records = json.load(f)
            except json.JSONDecodeError:
                records = []

    records.append(record)

    with open(FLAGGED_LOG_FILE, "w") as f:
        json.dump(records, f, indent=2)

    print(
        f"\n[SAFETY] Flagged input logged "
        f"(matched: {matched_terms})"
    )