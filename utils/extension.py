import os
from dotenv import load_dotenv
from groq import Groq
from utils.auth import get_user_profile_smart

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ==========================================================
# SYSTEM PROMPTS
# ==========================================================

ASTRO_EXPERT_PROMPT = """
You are an expert Indian astrologer.
You answer ONLY astrology-related questions such as:
- Horoscope
- Kundali
- Zodiac / Rashi
- Marriage compatibility
- Career astrology
- Planetary doshas
- Nakshatra analysis

If the question is astrology-related, give a helpful response.
"""

ASTRO_CLASSIFIER_PROMPT = """
You are a strict classifier.

Task:
Decide whether the user's question is related to astrology.

Astrology includes:
- Horoscope
- Kundali
- Zodiac / Rashi
- Birth charts
- Planets, doshas, nakshatras
- Marriage, career, health via astrology

Respond ONLY in JSON format like this:
{
  "is_astrology": true | false
}

Do NOT explain anything.
"""

# 🔴 Corrected: Output ONLY improved prompt text
PROMPT_IMPROVER_PROMPT = """
Rewrite the user input into a clearer, more specific,
well-structured astrology-related prompt.

STRICT RULES:
- Output ONLY the rewritten prompt
- Do NOT add introductions, explanations, labels, or formatting
- Do NOT ask questions
- Keep it concise and focused
"""

# ==========================================================
# LLM HELPER
# ==========================================================

def llm_chat(messages, temperature=0.5, max_tokens=200):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()

# ==========================================================
# ASTROLOGY CLASSIFIER
# ==========================================================
def build_astro_prompt(user_question: str, profile: dict | None) -> str:
    """
    Attaches user profile context to the prompt ONLY if available.
    Keeps prompt clean and professional.
    """
    if not profile:
        return user_question

    context_lines = []

    if profile.get("dob"):
        context_lines.append(f"Date of Birth: {profile['dob']}")
    if profile.get("tob"):
        context_lines.append(f"Time of Birth: {profile['tob']}")
    if profile.get("place"):
        context_lines.append(f"Place of Birth: {profile['place']}")
    if profile.get("rashi"):
        context_lines.append(f"Rashi: {profile['rashi']}")
    if profile.get("gender"):
        context_lines.append(f"Gender: {profile['gender']}")

    context_block = "\n".join(context_lines)

    return f"""
User Question:
{user_question}

User Birth Details:
{context_block}
""".strip()


def is_astrology_question(user_question: str) -> bool:
    try:
        result = llm_chat(
            messages=[
                {"role": "system", "content": ASTRO_CLASSIFIER_PROMPT},
                {"role": "user", "content": user_question},
            ],
            temperature=0,
            max_tokens=50,
        )

        result = result.lower()
        return '"is_astrology": true' in result

    except Exception:
        return False

# ==========================================================
# MAIN ASTRO RESPONSE
# ==========================================================

def get_astro_response(user_question: str, user_id: int) -> str:
    if not is_astrology_question(user_question):
        return "🙏 I can answer only astrology-related questions."

    profile = get_user_profile_smart(user_id)
    final_prompt = build_astro_prompt(user_question, profile)

    return llm_chat(
        messages=[
            {"role": "system", "content": ASTRO_EXPERT_PROMPT},
            {"role": "user", "content": final_prompt},
        ],
        temperature=0.7,
        max_tokens=500,
    )
# ==========================================================
# PROMPT IMPROVER (NO ASTRO CHECK)
# ==========================================================

def improve_prompt(user_prompt: str) -> str:
    """
    Improves the prompt ONLY.
    No astrology validation.
    No extra text.
    """
    return llm_chat(
        messages=[
            {"role": "system", "content": PROMPT_IMPROVER_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,  # lower temp = less fluff
        max_tokens=120,
    )
