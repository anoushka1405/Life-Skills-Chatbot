import json
import os
from datetime import datetime

# High-priority disclosures (self-harm / victim disclosures)
ALERT_WORDS = [
    "kill myself",
    "hurt myself",
    "suicide",
    "nobody loves me",
    "abuse",
    "i am scared at home",
    "hurt me",
    "hits me",
    "hate myself",
    "don't tell",
]

# Harm actions
HARM_ACTIONS = [
    "hit",
    "hits",
    "hurt",
    "hurts",
    "kick",
    "kicked",
    "punch",
    "punched",
    "bite",
    "bit",
    "bully",
    "bullied",
    "push",
    "pushed"
]

# Possible victims/people
PEOPLE_TARGETS = [
    "friend",
    "friends",
    "sister",
    "brother",
    "mom",
    "mother",
    "dad",
    "father",
    "teacher",
    "classmate",
    "him",
    "her",
    "someone",
    "kid",
    "child",
    "student",
    "my friend",
    "my sister",
    "my brother"
]

FLAGGED_LOG_FILE = "flagged_input_log.json"


def harmed_someone(text: str) -> bool:
    """
    Detects statements where the child may have harmed another person.

    Example:
    ✅ "I kicked my friend"
    ✅ "I punched him"
    ❌ "I kicked the ball"
    ❌ "I hit the baseball"
    """

    text = text.lower()

    has_action = any(action in text for action in HARM_ACTIONS)
    has_person = any(person in text for person in PEOPLE_TARGETS)

    return has_action and has_person


def is_concerning(text: str) -> bool:
    """
    Main safety checker.
    """

    text_lower = text.lower()

    # Check self-harm / victim disclosures first
    for phrase in ALERT_WORDS:
        if phrase in text_lower:
            return True

    # Check aggression toward others
    if harmed_someone(text_lower):
        return True

    return False


def is_concerning_semantic(text: str) -> bool:
    """
    Semantic layer disabled for now.
    Keeping this function prevents changes elsewhere in the codebase.
    """

    return False


def log_flagged_input(
    user_text,
    learner_name="demo_child",
    stage="unknown",
    source="keyword"
):
    """
    Logs flagged disclosures for adult review.
    """

    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "learner": learner_name,
        "stage": stage,
        "raw_text": user_text,
        "flagged_by": source,
        "reviewed": False
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