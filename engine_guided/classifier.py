"""
engine/classifier.py

Job of this file: given the kid's raw text input, and the list of valid
options for the CURRENT node, figure out which option (if any) they meant.

V1 approach: rule-based matching only, fully offline, no API key, no cost.
Two passes:
  Pass 1: exact keyword/phrase matching (same as before).
  Pass 2: fuzzy matching using Python's built-in difflib, which catches
          typos and near-misses (e.g. "techer" -> "teacher") without
          needing any AI model call.

This is intentionally NOT calling any LLM. An AI-assisted fallback is a
designed future upgrade (see mentor prep doc / tech stack), swappable in
later without changing how this function is called from the rest of the
engine — but it's not needed or used for this version.
"""

import difflib


def _rule_based_match(user_text: str, options: list) -> dict | None:
    """Pass 1: does the kid's text directly CONTAIN one of the known phrases?"""
    text = user_text.lower().strip()
    best_match = None
    best_score = 0

    for option in options:
        score = 0
        for phrase in option["matches"]:
            if phrase.lower() in text:
                score += len(phrase.split())
        if score > best_score:
            best_score = score
            best_match = option

    return best_match


def _fuzzy_match(user_text: str, options: list) -> dict | None:
    """
    Pass 2: word-by-word fuzzy matching to catch typos.
    Splits the kid's answer into words, and checks each word against every
    known matching phrase for a "close enough" match (handles small typos,
    missing/extra letters, etc.) — without needing an AI model at all.

    Tuning notes (measured against real test cases, not guessed):
    - cutoff=0.82: chosen because "wait" vs "what" scores exactly 0.75
      (a false positive caught during testing — a confused kid's "what
      to do" was being misread as "wait" / ask nicely) while real typos
      score well above that — "techer"/"teacher" 0.92, "nicly"/"nicely"
      0.91, "grb"/"grab" 0.86. 0.82 cleanly separates the two.
    - FILLER_WORDS are excluded entirely, even from exact matching —
      words like "it" or "to" appear in almost any sentence and shouldn't
      count as evidence on their own when checked in isolation from the
      rest of their original phrase (e.g. "it" from "take it").
    """
    words = user_text.lower().split()
    if not words:
        return None

    FILLER_WORDS = {"it", "to", "an", "a", "the", "for"}
    FUZZY_CUTOFF = 0.82

    best_match = None
    best_score = 0

    for option in options:
        score = 0
        for phrase in option["matches"]:
            phrase_words = phrase.lower().split()
            for pw in phrase_words:
                if pw in FILLER_WORDS:
                    continue
                if difflib.get_close_matches(pw, words, n=1, cutoff=FUZZY_CUTOFF):
                    score += 1
        if score > best_score:
            best_score = score
            best_match = option

    return best_match


def classify_intent(user_text: str, options: list) -> dict | None:
    if not user_text:
        return None

    # Pass 1: exact phrase containment - cheapest, most confident
    match = _rule_based_match(user_text, options)
    if match is not None:
        return match

    # Pass 2: only runs if Pass 1 found nothing - catches typos
    return _fuzzy_match(user_text, options)