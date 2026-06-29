"""
modules/conflict_resolution.py

This file defines ONE learning module as a Python dictionary.
A module is a tree of "nodes". Each node is one beat of the conversation.

Structure of a node:
{
    "id": "...",              # unique name for this node (so other nodes can point to it)
    "type": "story" | "decision" | "reflection",   # what kind of beat this is
    "text": "...",            # what Buddy says
    "auto_advance": True/False,  # for "story" nodes only: if True, the
        # runner moves straight to the next node without pausing for
        # input — use this for pure reactions that don't ask anything.
        # Defaults to False (pause) if not set, so existing modules
        # without this field still behave exactly as before.
    "options": [               # the valid things a child can respond with (only for "decision" nodes)
        {
            "label": "...",        # short label for this choice (shown as a button, or matched against speech)
            "matches": [...],       # words/phrases that count as picking this option (for rule-based matching)
            "next": "..."           # which node id to go to if this option is picked
        },
        ...
    ],
    "next": "..."   # for "story" and "reflection" nodes: just go straight to this next node, no choice needed
}

NOTE: any "{name}" in a node's "text" gets automatically replaced with the
real learner's name by the engine (see engine_guided/dialogue_engine.py).
"""

CONFLICT_RESOLUTION_MODULE = {
    "id": "conflict_resolution_sharing",
    "title": "Sharing the Crayons",
    "start_node": "intro",
    "nodes": {

        "intro": {
            "id": "intro",
            "type": "story",
            "text": "Hi {name}! I'm your life skills companion! Today we are learning about sharing!",
            "next": "teach_concept"
        },

        "teach_concept": {
            "id": "teach_concept",
            "type": "story",
            "text": "So, sharing means letting a friend use something too, even if you really want it all to yourself. And taking turns means everyone gets a turn, one after another — nobody gets left out!",
            "auto_advance": True,
            "next": "teach_why"
        },

        "teach_why": {
            "id": "teach_why",
            "type": "story",
            "text": "When we share and take turns, our friends feel happy, and they want to play with us again! Okay, now let's see this in action...",
            "auto_advance": True,
            "next": "scenario"
        },

        "scenario": {
            "id": "scenario",
            "type": "decision",
            "text": "Okay so — you're coloring with your friend Maya, and ooh, that RED crayon looks so good. But Maya's using it right now and won't hand it over. Uh oh! What do you do?",
            "options": [
                {
                    "label": "Grab the crayon",
                    "matches": ["grab", "take it", "snatch", "pull it"],
                    "next": "grab_response"
                },
                {
                    "label": "Ask Maya nicely and wait for a turn",
                    "matches": ["ask", "wait", "nicely", "please", "turn"],
                    "next": "ask_response"
                },
                {
                    "label": "Tell the teacher",
                    "matches": ["teacher", "tell someone", "tell an adult"],
                    "next": "teacher_response"
                }
            ]
        },

        "grab_response": {
            "id": "grab_response",
            "type": "story",
            "text": "Ooh, yikes! 😬 If we grab, Maya might feel surprised and a little sad — and next time, she might not want to share her crayons with us. Let's try a different way!",
            "auto_advance": True,
            "next": "scenario_retry"
        },

        "ask_response": {
            "id": "ask_response",
            "type": "story",
            "text": "Yes!! 🌟 That's such a kind move. When we ask nicely and wait our turn, everyone feels good — and Maya will probably want to share with you again and again!",
            "auto_advance": True,
            "next": "reflection"
        },

        "teacher_response": {
            "id": "teacher_response",
            "type": "story",
            "text": "That's a good idea to keep in your back pocket! But first, let's see what happens if YOU try talking to Maya yourself — like a real crayon negotiator. Ready?",
            "auto_advance": True,
            "next": "scenario_retry"
        },

        "scenario_retry": {
            "id": "scenario_retry",
            "type": "decision",
            "text": "Okay, Maya's still got the crayon. What's a friendly way you could ask her for a turn?",
            "options": [
                {
                    "label": "Ask Maya nicely and wait for a turn",
                    "matches": ["ask", "wait", "nicely", "please", "turn", "share"],
                    "next": "ask_response"
                }
            ]
        },

        "reflection": {
            "id": "reflection",
            "type": "reflection",
            "text": "You did awesome today! 🎉 If a friend ever has something you really want, what's one thing you could try?",
            "next": "end"
        },

        "end": {
            "id": "end",
            "type": "story",
            "text": "Thanks for hanging out and sharing with me today, {name}! 💛 You're getting really good at this — see you next time, friend!",
            "auto_advance": True,
            "next": None
        }
    }
}