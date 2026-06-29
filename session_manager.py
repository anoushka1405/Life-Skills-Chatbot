from engine.dialogue_engine import DialogueEngine
from modules.money_module import MONEY_MODULE
from datetime import datetime, timedelta

_sessions = {}
_last_access = {}

SESSION_TIMEOUT_MINUTES = 30


def get_engine(session_id: str) -> DialogueEngine:

    cleanup_old_sessions()

    if session_id not in _sessions:
        _sessions[session_id] = DialogueEngine(
            MONEY_MODULE
        )

    _last_access[session_id] = datetime.now()

    return _sessions[session_id]


def clear_session(session_id: str):

    _sessions.pop(session_id, None)
    _last_access.pop(session_id, None)


def cleanup_old_sessions():

    now = datetime.now()

    expired = []

    for sid, last_seen in _last_access.items():

        if now - last_seen > timedelta(
            minutes=SESSION_TIMEOUT_MINUTES
        ):
            expired.append(sid)

    for sid in expired:
        clear_session(sid)