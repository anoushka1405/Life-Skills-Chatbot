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


def generate_stage_response(module, history, user_message, stage, opener, personality, memory, is_final_stage=False):

    conversation = "\n".join(
        f"{t['role']}: {t['text']}" for t in history[-5:]
    )

    reflection_instruction = ""
    if is_final_stage:
        reflection_instruction = """
This is the LAST exchange before the lesson ends. Before wrapping up, ask
the child ONE simple reflection question that checks whether they actually
understood the main idea of this lesson — e.g. "Why do you think that
matters?" or "How would you use this with a friend?" Do not just end on
an open question that goes unanswered — make this question the clear
closing checkpoint of the lesson.
"""

    prompt = f"""
You are Buddy, a friendly learning companion for kids.

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

Latest message:
{user_message}

RULES:
- Max 3 sentences
- Simple language
- ONE question max
- Friendly tone
- No repetition
- If the child's answer is vague, confused, says "I don't know", or
  doesn't really engage with the question, do NOT just praise it and move
  on. Gently explain the idea yourself in one simple sentence, then ask
  an easier, more specific follow-up question to check understanding
  before moving forward.
{reflection_instruction}

Return only response.
"""

    response_text = _generate_with_retry(
        prompt,
        fallback_message=(
            "Sorry, I'm thinking a little slowly right now! "
            "Can you tell me that again in a moment?"
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