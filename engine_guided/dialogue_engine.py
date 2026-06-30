from engine.llm_helper import generate_stage_response, generate_summary
from engine.safety import (
    is_concerning,
    log_flagged_input
)
from engine.scenario_generator import get_random_scenario

import random


class DialogueEngine:

    def __init__(self, module):

        self.module = module
        self.history = []
        self.stage = 0
        self._wrap_up_done = False  # tracks whether we've actually responded
            # to the final "wrap_up" stage yet — without this, the session
            # could never genuinely end, since the stage index is capped at
            # the last stage rather than incrementing past it.

        # ✅ structured MONEY lesson flow
        self.stages = [
            "introduction",
            "wants_vs_needs",
            "saving",
            "spending",
            "scenario",
            "reflection",
            "wrap_up"
        ]

        # personality traits
        self.personality = {
            "warmth": 0.7,
            "energy": 0.6,
            "formality": 0.2
        }

        # memory
        self.memory = {
            "user_mood": "neutral",
            "engagement_level": "medium",
            "last_topic": None
        }

        self.soft_openers = [
            "That's a great thought 😊",
            "I like how you're thinking 💭",
            "Let's explore that together 🤝",
            "Hmm, interesting!"
        ]

    # ----------------------------
    # START SESSION
    # ----------------------------
    def start(self):

        opening = self.module["opening_message"]

        self.history.append({
            "role": "Buddy",
            "text": opening
        })

        return opening

    # ----------------------------
    # MEMORY UPDATE
    # ----------------------------
    def update_memory(self, text):

        t = text.lower()
        words = len(text.split())

        # mood tracking
        if any(w in t for w in ["good", "happy", "great", "fun", "awesome"]):
            self.memory["user_mood"] = "positive"

        elif any(w in t for w in ["confused", "hard", "don't know", "sad"]):
            self.memory["user_mood"] = "confused"

        # engagement tracking
        if words > 8:
            self.memory["engagement_level"] = "high"
        elif words < 3:
            self.memory["engagement_level"] = "low"
        else:
            self.memory["engagement_level"] = "medium"

        # personality adjustment
        if any(w in t for w in ["yes", "ok", "sure"]):
            self.personality["warmth"] = min(1.0, self.personality["warmth"] + 0.05)

        if words < 3:
            self.personality["energy"] = max(0.4, self.personality["energy"] - 0.02)

    # ----------------------------
    # STAGE CONTROL (FIXED)
    # ----------------------------
    def advance_stage(self, user_text):

        words = len(user_text.split())

        # don't move if too short
        if words < 2:
            return

        # don't rush confused child
        if self.memory["user_mood"] == "confused":
            return

        # normal progression (clean + predictable)
        self.stage += 1

        # cap stage
        self.stage = min(self.stage, len(self.stages) - 1)

    # ----------------------------
    # RESPONSE ENGINE
    # ----------------------------
    def respond(self, user_text):

        current_stage = self.stages[self.stage]

        # ------------------------
        # SAFETY CHECK
        # ------------------------
        if is_concerning(user_text):

            log_flagged_input(
                user_text=user_text,
                learner_name=getattr(self, "learner_name", "demo_child"),
                stage=current_stage,
                source="keyword"
            )

            return (
                "Thank you for sharing that with me 💙\n"
                "I'm really glad you told me. A trusted adult can help you best with this."
            )

        # ------------------------
        # MEMORY UPDATE
        # ------------------------
        self.update_memory(user_text)

        self.history.append({
            "role": "Child",
            "text": user_text
        })

        stage = self.stages[self.stage]

        # ------------------------
        # SCENARIO STAGE
        # ------------------------
        if stage == "scenario":

            scenario = get_random_scenario(
                self.module.get("title", "")
            )

            response = (
                random.choice(self.soft_openers)
                + "\n\n"
                + scenario
            )

        # ------------------------
        # REFLECTION FIX (IMPORTANT)
        # ------------------------
        elif stage == "reflection":

            response = (
                "Let’s reflect on what we learned today 😊\n\n"
                "1) What is the difference between a want and a need?\n"
                "2) Why is saving money important?\n\n"
                "Take your time and think!"
            )

        # ------------------------
        # NORMAL STAGES
        # ------------------------
        else:

            response = generate_stage_response(
                module=self.module,
                history=self.history,
                user_message=user_text,
                stage=stage,
                opener=random.choice(self.soft_openers),
                personality=self.personality,
                memory=self.memory,
                is_final_stage=(stage == "wrap_up")
            )

        self.history.append({
            "role": "Buddy",
            "text": response
        })

        # If we just responded WHILE at the final stage, the session has
        # genuinely concluded — mark it so session_finished() can detect
        # this correctly (the stage index alone can't tell us, since it's
        # capped at the last stage rather than incrementing past it).
        if stage == "wrap_up":
            self._wrap_up_done = True

        # ------------------------
        # ADVANCE FLOW
        # ------------------------
        self.advance_stage(user_text)

        return response

    # ----------------------------
    # SESSION END
    # ----------------------------
    def session_finished(self):
        return self._wrap_up_done

    def end_session(self):
        return generate_summary(self.history, self.module)