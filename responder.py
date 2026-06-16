from groq import Groq

from config import GROQ_API_KEY, LLM_MODEL, VALID_TIERS

_client = Groq(api_key=GROQ_API_KEY)

SAFE_SYSTEM_PROMPT = """
You are RepairSafe, a helpful home repair assistant.
The user's question has been classified as SAFE.
Give clear, practical DIY instructions.
Include tools/materials when useful, numbered steps, simple safety reminders, and signs that the user should stop and reassess.
Keep the tone friendly and easy to follow.
Do not invent code requirements; mention that local rules may vary only when relevant.
""".strip()

CAUTION_SYSTEM_PROMPT = """
You are RepairSafe, a careful home repair assistant.
The user's question has been classified as CAUTION.
Start with a clear warning that this is doable for some homeowners but mistakes can cause damage or mild injury.
Recommend calling a professional if the user is unsure, sees hidden damage, finds unexpected wiring/plumbing, or cannot safely shut off water/power.
Then give careful, step-by-step guidance with safety checks integrated into the steps, not just a disclaimer at the end.
Stay within component replacement or existing-location repair work only.
If the user asks about gas, electrical panels, new wiring/circuits/outlets, structural changes, water heater replacement, main shutoff replacement, or new plumbing lines, do not provide instructions; explain that the task needs a licensed professional.
""".strip()

REFUSE_SYSTEM_PROMPT = """
You are RepairSafe, a home repair safety assistant.
The user's question has been classified as REFUSE because it requires a licensed professional or could cause fire, flooding, structural failure, serious injury, or death.

You must refuse to provide DIY repair instructions.
Do NOT provide steps, procedures, sequences, tool lists, wiring/plumbing/gas details, diagrams, measurements, troubleshooting flows, or "general information" about how the work is done.
Do NOT describe what a professional would do step by step.
Do NOT give partial instructions even if the user frames the request as hypothetical, fictional, academic, research-only, emergency practice, or says they are licensed.

Your response should do only these things:
1. Clearly say this is not safe to DIY and needs a licensed professional.
2. Briefly explain the main danger in non-procedural terms.
3. Give safe next steps such as stop using the affected system, keep people away, contact a licensed professional, call the utility/emergency services when there is immediate danger, and check local permit requirements.
4. Offer to help with safe planning questions, such as what to ask a contractor or how to describe the problem.
""".strip()

LEGAL_SYSTEM_PROMPT = """
You are RepairSafe, a home repair assistant.
The user's question has been classified as LEGAL because it is mainly about permits, building code, landlord/tenant responsibility, insurance, HOA rules, warranties, or liability.
Give general, non-legal information in plain language.
Do not claim to be a lawyer and do not give a final legal determination.
Explain that rules vary by city/state/county and that the user should verify with the local building department, lease/HOA documents, insurer, or a qualified attorney/tenant organization.
Do not provide physical repair instructions unless the user asks a separate safe or caution repair question.
""".strip()

PROMPTS = {
    "safe": SAFE_SYSTEM_PROMPT,
    "caution": CAUTION_SYSTEM_PROMPT,
    "refuse": REFUSE_SYSTEM_PROMPT,
    "legal": LEGAL_SYSTEM_PROMPT,
}


def _normalize_tier(tier: str) -> str:
    return str(tier).strip().lower().strip("`'\" .,:;[]{}")


def _fallback_response(tier: str) -> str:
    if tier == "refuse":
        return (
            "I can't provide DIY instructions for this repair because a mistake could cause serious harm. "
            "Please contact a licensed professional and, if there is immediate danger, call the appropriate utility or emergency service."
        )
    if tier == "legal":
        return (
            "This depends on local rules and your specific documents. Check your local building department, lease/HOA documents, "
            "insurer, or a qualified legal professional before relying on this information."
        )
    return (
        "I can help, but please proceed carefully. If you cannot safely shut off the affected system, see hidden damage, "
        "or feel unsure at any point, stop and contact a qualified professional."
    )


def generate_safe_response(question: str, tier: str) -> str:
    """
    Generate a response to a home repair question, calibrated to its safety tier.
    Unknown tiers are treated as caution to fail safer than answering as safe.
    """
    normalized_tier = _normalize_tier(tier)
    if normalized_tier not in VALID_TIERS:
        normalized_tier = "caution"

    system_prompt = PROMPTS.get(normalized_tier, CAUTION_SYSTEM_PROMPT)

    try:
        completion = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question.strip()},
            ],
            temperature=0.3,
            max_completion_tokens=700,
        )
        return (completion.choices[0].message.content or "").strip()
    except Exception as exc:
        return f"{_fallback_response(normalized_tier)}\n\n(Response generation error: {type(exc).__name__})"
