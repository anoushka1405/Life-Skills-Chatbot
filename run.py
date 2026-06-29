"""
run.py

Terminal interface for Buddy.

Run:
    python run.py
"""

from modules.empathy_module import EMPATHY_MODULE
from engine.dialogue_engine import DialogueEngine


def run():

    engine = DialogueEngine(EMPATHY_MODULE)

    print("=" * 60)
    print(f"🌟 Starting module: {EMPATHY_MODULE['title']}")
    print("=" * 60)

    # Start lesson
    print("\n🤖 Buddy:")
    print(engine.start())

    print("\n(Type 'bye' anytime to end the session early.)")

    # Main conversation loop
    while not engine.session_finished():

        user_text = input("\n👤 You: ").strip()

        # Skip empty inputs
        if not user_text:
            print("\n🤖 Buddy:")
            print("Take your time 😊")
            continue

        # Early exit
        if user_text.lower() == "bye":
            print("\n🤖 Buddy:")
            print("Thanks for chatting with me today! 👋")
            break

        # Generate Buddy response
        response = engine.respond(user_text)

        print("\n🤖 Buddy:")
        print(response)

    # Session summary
    print("\n🎉 Session Complete!\n")

    print(engine.end_session())

    print("\n🌟 Weekly Challenge:")
    print(EMPATHY_MODULE["weekly_challenge"])

    print("\n👋 See you next time!")


if __name__ == "__main__":
    run()