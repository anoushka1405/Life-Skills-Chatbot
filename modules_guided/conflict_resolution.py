"""
modules/conflict_resolution.py

This file defines ONE learning module as a Python dictionary.
A module is a tree of "nodes". Each node is one beat of the conversation.

Structure of a node:
{
    "id": "...",              # unique name for this node (so other nodes can point to it)
    "type": "story" | "decision" | "reflection",   # what kind of beat this is
    "text": "...",            # what Buddy says
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
"""

CONFLICT_RESOLUTION_MODULE = {
    "id": "conflict_resolution_sharing",
    "title": "Sharing the Crayons",
    "start_node": "intro",
    "nodes": {

        "intro": {
            "id": "intro",
            "type": "story",
            "text": "Hi! I'm Buddy. Today let's talk about something that happens to everyone — sharing! Ready?",
            "next": "scenario"
        },

        "scenario": {
            "id": "scenario",
            "type": "decision",
            "text": "You and your friend Maya are coloring. You really want the red crayon, but Maya is using it and won't give it to you. What do you do?",
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
            "text": "Hmm, if we grab things, Maya might feel upset, and she may not want to share with us next time. Let's see what else we could try.",
            "next": "scenario_retry"
        },

        "ask_response": {
            "id": "ask_response",
            "type": "story",
            "text": "That's a great choice! Asking nicely and waiting for a turn helps everyone feel good, and Maya will probably want to share with you again.",
            "next": "reflection"
        },

        "teacher_response": {
            "id": "teacher_response",
            "type": "story",
            "text": "That can help sometimes! But first, it's often good to try talking to your friend yourself, like asking nicely. Let's try that.",
            "next": "scenario_retry"
        },

        "scenario_retry": {
            "id": "scenario_retry",
            "type": "decision",
            "text": "So, Maya still has the red crayon. What's a kind way to ask her for a turn?",
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
            "text": "Great job today! What's one thing you learned about sharing that you could try with a friend this week?",
            "next": "end"
        },

        "end": {
            "id": "end",
            "type": "story",
            "text": "Thanks for talking with me today! See you next time, Buddy out!",
            "next": None
        }
    }
}
