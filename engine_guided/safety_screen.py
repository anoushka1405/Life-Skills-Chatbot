"""
engine/safety_screen.py

V1's "Input Safety Screening + Concerning-Input Detection & Escalation" feature.

Job of this file: look at EVERY piece of text a child types, before it goes
anywhere else (before the classifier even sees it), and check whether it
suggests something concerning — distress, mentions of being hurt, unsafe
situations, etc.

Important design choices, matching what's in the mentor prep doc:
- This is rule/keyword based in V1, NOT an AI judgment call. Simple and
  auditable — you can read this file top to bottom and know exactly what
  it does and doesn't catch.
- It does NOT try to respond to the concerning content itself. Its only
  job is to flag it and log it for a human to review. Buddy's own response
  stays calm and pre-written, handled separately in run.py.
- It is deliberately biased toward OVER-flagging rather than under-flagging
  — a false alarm costs a human a few minutes reviewing a harmless message;
  a missed real concern costs much more. So the keyword list here is
  intentionally broad.
"""

import json
import os
from datetime import datetime

FLAGGED_LOG_FILE = "flagged_input_log.json"

# NOTE: this is a starter list for V1, not a clinical or exhaustive one.
# A real deployment should have this reviewed and expanded by people with
# real child-safety expertise — this is intentionally a first pass.
CONCERNING_KEYWORDS = [
    "hurt me", "hurts me", "hit me", "hits me", "scared of",
    "afraid of", "nobody loves me", "want to die", "kill myself",
    "no one cares", "hate myself", "hate my life",
    "touched me", "secret", "don't tell",
]


def screen_input(user_text: str) -> dict:
    """
    Checks a single piece of child input for concerning content.
    Returns a dict: {"flagged": bool, "matched_terms": [...]}

    This does NOT block the conversation from continuing — it just
    reports back so the caller can log it and let a human know.
    """
    if not user_text:
        return {"flagged": False, "matched_terms": []}

    text = user_text.lower()
    matched = [kw for kw in CONCERNING_KEYWORDS if kw in text]

    return {"flagged": len(matched) > 0, "matched_terms": matched}


def log_flagged_input(learner_name: str, node_id: str, user_text: str, matched_terms: list) -> None:
    """
    Writes a flagged event to a separate log file from the normal session
    log. In a real deployment, this would write to a restricted database
    table with a reviewed/unreviewed status (see mentor prep doc, Part 5) —
    for V1, a clearly separate JSON file is enough to prove the concept:
    flagged content is captured distinctly from ordinary session data.
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

    # In a real deployment this is where a notification would also fire —
    # e.g. alerting a teacher dashboard or a support queue. V1 intentionally
    # does NOT have that pipeline yet (flagged honestly in the mentor prep
    # doc as a gap that must be closed before any real deployment).
    print(f"\n[SAFETY] Flagged input logged for review (terms matched: {matched_terms})")
