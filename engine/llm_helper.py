import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

_client = None


def _get_client():
    """
    Lazily creates the Gemini client on first real use, instead of at
    import time. This means importing this file (or anything that imports
    it) doesn't crash just because no API key is set yet — the crash only
    happens if you actually try to generate a response without a key,
    which is a much clearer failure point.
    """
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to your .env file "
                "before starting a real conversation."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def _generate_with_retry(prompt, model="gemini-2.5-flash", max_retries=3, fallback_message=None):
    """
    Wraps the actual API call with retry-on-rate-limit handling.

    The free AI Studio tier has a per-minute request cap. If we hit it
    (a 429 error), the right move isn't to crash the demo — it's to wait
    a moment and try again, a couple of times, before giving up gracefully.

    fallback_message: what to return if we exhaust all retries, so the
    conversation can still continue instead of throwing an unhandled error
    mid-demo.
    """
    delay = 2  # seconds, doubles each retry (2s, 4s, 8s)

    for attempt in range(max_retries):
        try:
            response = _get_client().models.generate_content(
                model=model,
                contents=prompt
            )
            return response.text.strip()

        except errors.APIError as e:
            is_rate_limit = getattr(e, "code", None) == 429

            if is_rate_limit and attempt < max_retries - 1:
                print(f"[llm_helper] Rate limited, retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                delay *= 2
                continue

            print(f"[llm_helper] Gemini call failed after {attempt + 1} attempt(s): {e}")
            if fallback_message:
                return fallback_message
            raise


def generate_stage_response(
    module,
    history,
    user_message,
    stage,
    opener,
    personality,
    memory,
    is_final_stage=False
):

    conversation = "\n".join(
        f"{t['role']}: {t['text']}" for t in history[-5:]
    )

    # Stage-specific guidance
    stage_instruction = ""

    if stage == "introduction":
        stage_instruction = """
Introduce today's topic warmly.
Ask about the child's own experiences.
Keep it playful and welcoming.
"""

    elif stage == "personal_experience":
        stage_instruction = """
Encourage the child to share experiences.
Validate their feelings and ideas.
Ask one simple follow-up question.
"""

    elif stage == "teach_concept":

        if module["title"].lower() == "money smarts":
            stage_instruction = """
Teach one simple money idea.

Explain:
- needs vs wants
- saving money
- thoughtful spending

Use age-appropriate examples.

Example:
'Food is usually a need. A toy is usually a want.'
"""

        else:
            stage_instruction = """
Teach one simple idea related to today's lesson.
Use examples children understand.
"""

    elif stage == "scenario_discussion":

        if module["title"].lower() == "money smarts":
            stage_instruction = """
Discuss the money scenario.

Help the child think through:
- saving
- spending
- fairness
- responsibility

Do not say answers are wrong.
Guide them gently.
"""

        else:
            stage_instruction = """
Discuss the scenario and encourage reasoning.
"""

    elif stage == "reflection":
        stage_instruction = """
Ask the child to reflect on today's lesson.

Encourage them to think about:
- one new thing they learned
- one smart choice they could make
- how they might use this idea in real life

Keep responses warm and encouraging.
"""

    elif stage == "wrap_up":
        stage_instruction = """
Congratulate the child.

Mention one positive quality they showed, such as:
- thoughtful thinking
- responsibility
- kindness
- careful decision making

End with excitement for future learning.
"""

    reflection_instruction = ""

    if is_final_stage:
        reflection_instruction = """
This is the LAST exchange before the lesson ends.

Ask ONE simple reflection question that checks understanding.

Examples:
- What is one thing you learned today?
- How could you use this idea in real life?

Keep it simple and child-friendly.
"""

    prompt = f"""
You are Buddy, a friendly learning companion for children aged 5-12.

Lesson: {module['title']}
Stage: {stage}

OPENING:
{opener}

PERSONALITY:
Warmth: {personality['warmth']}
Energy: {personality['energy']}

USER MEMORY:
Mood: {memory['user_mood']}
Engagement: {memory['engagement_level']}

Conversation:
{conversation}

Latest child message:
{user_message}

STAGE INSTRUCTIONS:
{stage_instruction}

RULES:
- Maximum 3 sentences.
- Use simple language.
- Friendly and encouraging tone.
- Ask at most ONE question.
- Avoid repeating yourself.
- Celebrate effort, not correctness.
- If the child seems confused, explain simply and ask an easier question.
- Speak directly to the child.

{reflection_instruction}

Return ONLY Buddy's response.
"""

    response_text = _generate_with_retry(
        prompt,
        fallback_message=(
            "I'm thinking a little slowly right now 😊 "
            "Could you tell me that again?"
        )
    )

    return response_text

def generate_summary(history, module):

    convo = "\n".join(f"{t['role']}: {t['text']}" for t in history)

    prompt = f"""
Summarize:

Lesson: {module['title']}

Conversation:
{convo}

IMPORTANT: Only state that the child understood or learned something if
the conversation actually shows them engaging with that idea. If the
conversation ended early or a key question was never really answered,
say so honestly in the summary instead of assuming the lesson landed.

Return:
- 3 bullet points (grounded in what was ACTUALLY discussed, not assumed)
- 1 honest note on how well the child engaged with the core idea
- 1 encouragement
- A short badge name relevant to this specific lesson (e.g. "{module['title']} Star")
"""

    return _generate_with_retry(
        prompt,
        fallback_message=(
            "Great session today! (Summary unavailable right now — "
            "please check back in a moment.)"
        )
    )