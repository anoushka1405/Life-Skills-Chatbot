import time

from modules_guided.conflict_resolution import CONFLICT_RESOLUTION_MODULE
from engine_guided.dialogue_engine import DialogueEngine
from engine_guided.session_store import save_session, has_completed_module
from engine_guided.safety_screen import screen_input, log_flagged_input


def run():
    learner_name = input("What's your name? ") or "demo_child"

    if has_completed_module(learner_name, CONFLICT_RESOLUTION_MODULE["title"]):
        print(f"\n🤖 Buddy: Hi {learner_name}! You've already done this lesson before — let's do it again for fun!")

    engine = DialogueEngine(CONFLICT_RESOLUTION_MODULE, learner_name=learner_name)

    print("=" * 50)
    print(f"Starting module: {CONFLICT_RESOLUTION_MODULE['title']}")
    print("=" * 50)

    while True:
        node = engine.current_node()

        print(f"\n🤖 Buddy: {engine.get_buddy_line()}")

        if node.get("next") is None and node["type"] != "decision":
            print("\n--- Session complete! ---")
            break

        if node["type"] in ("story", "reflection"):
            # Auto-advance nodes are pure reactions that don't ask anything —
            # genuinely skip ahead with a brief timed pause, no input wait.
            if node["type"] == "story" and node.get("auto_advance"):
                time.sleep(10)  # real pause, not a disguised input() wait
                engine.submit_response("")
                continue

            user_input = input("(press Enter to continue, or type a reflection answer) > ")

            # --- Safety screening happens on EVERY input, before anything else ---
            screen_result = screen_input(user_input)
            if screen_result["flagged"]:
                log_flagged_input(learner_name, node["id"], user_input, screen_result["matched_terms"])
                # Buddy's response stays calm and pre-written — it does NOT
                # try to engage with the concerning content itself.
                print("\n🤖 Buddy: Thank you for telling me. That sounds important — let's make sure a grown-up you trust knows about this too.")

            engine.submit_response(user_input)
            continue

        if node["type"] == "decision":
            user_text = input("👤 You: ")

            # --- Same screening, applied before classification ---
            screen_result = screen_input(user_text)
            if screen_result["flagged"]:
                log_flagged_input(learner_name, node["id"], user_text, screen_result["matched_terms"])
                print("\n🤖 Buddy: Thank you for telling me. That sounds important — let's make sure a grown-up you trust knows about this too.")
                continue  # don't classify flagged input as a lesson answer — ask again

            result = engine.submit_response(user_text)

            # Light echo-back: reflect the child's own words before the
            # canned reaction plays, so it feels like Buddy heard THEM
            # specifically, not just which button they pressed. This is
            # purely cosmetic — it doesn't change which branch was taken,
            # and never generates new text, just reflects what was typed.
            if result["status"] == "advanced" and user_text.strip():
                print(f'\n🤖 Buddy: Ooh, "{user_text.strip()}" — got it!')

            if result["status"] == "no_match":
                print(f"\n🤖 Buddy: {result['message']}")
            elif result["status"] == "fallback_advanced":
                print(f"\n🤖 Buddy: {result['message']}")

    # ---- Session wrap-up: this is the "session summary log" feature ----
    summary = engine.generate_summary()
    save_session(summary, learner_name=learner_name)

    print("\n" + "=" * 50)
    print("SESSION SUMMARY (this is what a teacher/parent would see)")
    print("=" * 50)
    print(f"Learner:           {learner_name}")
    print(f"Module:            {summary['module']}")
    print(f"Completed:         {summary['completed']}")
    print(f"Choices made:      {summary['choices_made']}")
    print(f"Times needed help: {summary['times_needed_a_retry']}")
    print(f"Reflection answer: {summary['reflection_answer']}")
    print(f"\n(Saved to session_logs.json)")


if __name__ == "__main__":
    run()