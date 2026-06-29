"""
engine/dialogue_engine.py

This is the brain that walks through a module, node by node.

Job of this file:
- Keep track of "where we are" in the conversation (current node, retry count)
- Decide what Buddy says next
- When the kid answers, ask the classifier what they meant
- If matched: move to the next node
- If not matched: gently re-prompt (up to a limit), then move forward anyway
  so the conversation never gets stuck in a loop
"""

from engine_guided.classifier import classify_intent

MAX_RETRIES = 2  # how many times we re-prompt before giving up and moving on


class DialogueEngine:
    def __init__(self, module: dict):
        self.module = module
        self.nodes = module["nodes"]
        self.current_node_id = module["start_node"]
        self.retry_count = 0
        self.history = []  # log of everything that happened, for the session summary later

    def current_node(self) -> dict:
        return self.nodes[self.current_node_id]

    def is_finished(self) -> bool:
        node = self.current_node()
        return node.get("next") is None and node["type"] != "decision"

    def get_buddy_line(self) -> str:
        """What Buddy should say for the current node."""
        return self.current_node()["text"]

    def submit_response(self, user_text: str) -> dict:
        """
        Called when the kid responds to a 'decision' node.
        Returns a dict describing what happened, so the caller (our CLI, for now)
        knows what to print.
        """
        node = self.current_node()

        if node["type"] != "decision":
            # Story/reflection nodes don't need a real answer to branch on —
            # we just log whatever was said (useful for reflection!) and move on.
            self.history.append({"node": node["id"], "said": user_text})
            self._advance(node.get("next"))
            return {"status": "advanced"}

        match = classify_intent(user_text, node["options"])

        if match is not None:
            self.history.append({
                "node": node["id"],
                "said": user_text,
                "matched_option": match["label"]
            })
            self.retry_count = 0
            self._advance(match["next"])
            return {"status": "advanced"}

        # No match — this is the "confirm and repeat" behavior
        self.retry_count += 1
        self.history.append({"node": node["id"], "said": user_text, "matched_option": None})

        if self.retry_count > MAX_RETRIES:
            # Give up gracefully — move to the first option's path so the
            # session doesn't get stuck forever.
            self.retry_count = 0
            fallback_next = node["options"][0]["next"]
            self._advance(fallback_next)
            return {
                "status": "fallback_advanced",
                "message": "That's okay! Let's keep going together."
            }

        return {
            "status": "no_match",
            "message": "Hmm, I didn't quite catch that. Could you try saying it a different way?"
        }

    def _advance(self, next_node_id):
        self.current_node_id = next_node_id

    def generate_summary(self) -> dict:
        """
        Builds the end-of-session summary — what we'd show a teacher/parent.
        Pulled straight from self.history, which we've been quietly building
        this whole time as the conversation progressed.
        """
        decisions_made = [
            h for h in self.history if h.get("matched_option") is not None
        ]
        # Only count it as a "struggle" if this history entry came from an
        # actual decision node that failed to match — NOT story/reflection
        # nodes, which never have a matched_option key at all and shouldn't
        # be counted as a failed attempt.
        times_struggled = sum(
            1 for h in self.history
            if "matched_option" in h and h["matched_option"] is None
        )
        reflection_entries = [
            h["said"] for h in self.history
            if self.nodes.get(h["node"], {}).get("type") == "reflection" and h["said"]
        ]

        return {
            "module": self.module["title"],
            "completed": self.is_finished(),
            "choices_made": [
                {"at": h["node"], "chose": h["matched_option"]} for h in decisions_made
            ],
            "times_needed_a_retry": times_struggled,
            "reflection_answer": reflection_entries[0] if reflection_entries else None,
        }
