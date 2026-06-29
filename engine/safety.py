import json
import os
from datetime import datetime

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

FLAGGED_LOG_FILE = "flagged_input_log.json"


def is_concerning(text):
    text = text.lower()
    for phrase in ALERT_WORDS:
        if phrase in text:
            return True
    return False


def log_flagged_input(user_text, learner_name="demo_child", stage="unknown"):
    """
    Writes a flagged message to its own log file, separate from normal
    conversation history, so a teacher/parent can review it later.
    Mirrors the same approach used in the guided engine's safety_screen.py.
    """
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "learner": learner_name,
        "stage": stage,
        "raw_text": user_text,
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