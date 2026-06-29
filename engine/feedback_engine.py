def generate_feedback(choice_label):

    choice = choice_label.lower()

    if "grab" in choice:
        return (
            "I understand that waiting can feel frustrating. "
            "But grabbing might make Maya feel upset."
        )

    elif "ask" in choice:
        return (
            "Great thinking! Asking politely and waiting your turn "
            "helps everyone feel respected."
        )

    elif "teacher" in choice:
        return (
            "Asking an adult can help. It's also good to try "
            "talking kindly with your friend first."
        )

    return (
        "That's an interesting idea. Let's think together about "
        "what might be the kindest choice."
    )