"""
engine/session_store.py

V1's "persistent data layer" — deliberately simple. Instead of Redis/Postgres
(which is the real plan, per the tech stack doc), V1 just appends each
session's summary to a local JSON file. This is enough to prove the CONCEPT
of a session log existing and being readable by a teacher/parent, without
standing up real infrastructure for a one-week demo.

Swapping this for a real database later means changing ONLY this file —
nothing in dialogue_engine.py needs to know or care how storage works.
"""

import json
import os
from datetime import datetime

SESSIONS_FILE = "session_logs.json"


def save_session(summary: dict, learner_name: str = "demo_child") -> None:
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "learner": learner_name,
        **summary,
    }

    sessions = []
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "r") as f:
            try:
                sessions = json.load(f)
            except json.JSONDecodeError:
                sessions = []

    sessions.append(record)

    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f, indent=2)


def load_all_sessions() -> list:
    if not os.path.exists(SESSIONS_FILE):
        return []
    with open(SESSIONS_FILE, "r") as f:
        return json.load(f)


def has_completed_module(learner_name: str, module_title: str) -> bool:
    """
    A tiny taste of the 'cross-session record' feature — checks if this
    learner has already finished this module in a past session.
    """
    sessions = load_all_sessions()
    return any(
        s["learner"] == learner_name and s["module"] == module_title and s["completed"]
        for s in sessions
    )
