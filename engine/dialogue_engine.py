from engine.llm_helper import generate_stage_response, generate_summary
from engine.safety import is_concerning, log_flagged_input
import random


class DialogueEngine:

    def __init__(self, module):

        self.module = module
        self.history = []
        self.stage = 0

        self.stages = [
            "introduction",
            "personal_experience",
            "teach_concept",
            "scenario",
            "scenario_discussion",
            "reflection",
            "wrap_up"
        ]

        # 🧠 personality
        self.personality = {
            "warmth": 0.7,
            "energy": 0.6,
            "formality": 0.2
        }

        # 🧠 FIXED memory (no missing keys anymore)
        self.memory = {
            "user_mood": "neutral",
            "engagement_level": "medium",
            "last_topic": None
        }

        self.soft_openers = [
            "That’s a great thought 😊",
            "I like how you're thinking 💭",
            "Let’s explore that together 🤝",
            "Hmm interesting!"
        ]

    def update_memory(self, text):

        t = text.lower()

        # mood tracking
        if any(w in t for w in ["good", "nice", "fun", "happy"]):
            self.memory["user_mood"] = "positive"

        elif any(w in t for w in ["confused", "don't know", "hard"]):
            self.memory["user_mood"] = "confused"

        # engagement tracking (FIX for your crash)
        if len(text.split()) > 8:
            self.memory["engagement_level"] = "high"
        elif len(text.split()) < 3:
            self.memory["engagement_level"] = "low"
        else:
            self.memory["engagement_level"] = "medium"

        # personality adjustment
        if any(w in t for w in ["yes", "ok", "sure"]):
            self.personality["warmth"] = min(1.0, self.personality["warmth"] + 0.05)

        if len(text.split()) < 3:
            self.personality["energy"] = max(0.4, self.personality["energy"] - 0.02)

    def start(self):

        opening = self.module["opening_message"]

        self.history.append({"role": "Buddy", "text": opening})

        return opening

    def respond(self, user_text):

        if is_concerning(user_text):
            log_flagged_input(
                user_text,
                learner_name=getattr(self, "learner_name", "demo_child"),
                stage=self.stages[min(self.stage, len(self.stages) - 1)]
            )
            return (
                "Thank you for telling me that. "
                "Please talk to a trusted adult 💙"
            )

        self.update_memory(user_text)

        self.history.append({"role": "Child", "text": user_text})

        stage = self.stages[min(self.stage, len(self.stages) - 1)]

        response = generate_stage_response(
            module=self.module,
            history=self.history,
            user_message=user_text,
            stage=stage,
            opener=random.choice(self.soft_openers),
            personality=self.personality,
            memory=self.memory,
            is_final_stage=(stage in ("reflection", "wrap_up"))
        )

        self.history.append({"role": "Buddy", "text": response})

        self.stage += 1

        return response

    def session_finished(self):
        return self.stage >= len(self.stages)

    def end_session(self):
        return generate_summary(self.history, self.module)