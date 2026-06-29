import random

MONEY_SCENARIOS = [

    "💰 Scenario:\n\n"
    "You have ₹100. You want candy today, but you are also saving for a toy. What would you do?",

    "🐷 Scenario:\n\n"
    "You receive ₹200 as a birthday gift. Would you spend it all, save some, or do both? Why?",

    "🎁 Scenario:\n\n"
    "Your friend spent all their allowance immediately and now regrets it. What advice would you give?",

    "🪙 Scenario:\n\n"
    "You found ₹50 on the playground. What do you think is the right thing to do?",

    "🛍️ Scenario:\n\n"
    "You really want a new video game, but you already have several games at home. How would you decide whether to buy it?",

    "🍎 Scenario:\n\n"
    "You can buy chips today or save your money for a book next week. How would you choose?",

    "🏦 Scenario:\n\n"
    "You have been saving money for many weeks and finally reached your goal. How do you think you would feel?"
]


def get_random_scenario(module_title):

    if "money" in module_title.lower():
        return random.choice(MONEY_SCENARIOS)

    return (
        "Imagine a situation related to today's lesson. "
        "What would you do?"
    )