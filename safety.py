import json
import re
from typing import Any

from groq import Groq

from config import GROQ_API_KEY, LLM_MODEL, VALID_TIERS

_client = Groq(api_key=GROQ_API_KEY)

FALLBACK_TIER = "caution"

CLASSIFIER_SYSTEM_PROMPT = """
You are RepairSafe's safety classifier. Your job is to classify a home repair question before any answer is written.

Return ONLY one valid JSON object in this exact shape:
{"tier":"safe|caution|refuse|legal","reason":"one short sentence"}

Do not answer the repair question. Do not give instructions. Classify the request only.

Tier definitions:
- safe: Routine maintenance or low-risk repairs most homeowners can do with basic tools; if done wrong, the likely worst case is cosmetic damage or a broken fixture, not injury, fire, flooding, structural damage, or death.
- caution: DIY-doable repairs involving existing fixtures or existing water/electrical components where mistakes have real cost or mild injury risk, but no new infrastructure, permit, or licensed professional is normally required.
- refuse: Repairs where an amateur mistake can cause fire, flooding, structural failure, serious injury, or death, or where the work normally requires a permit or licensed professional. This includes gas work, electrical panel/service work, adding new outlets/circuits/wiring, moving switches that require new wire, structural/load-bearing wall work, main water shutoff replacement, water heater replacement, new plumbing lines, foundation repair, and structural roof repair.
- legal: Questions mainly about permits, building code, landlord/tenant responsibility, insurance, HOA rules, warranties, liability, or who is allowed to do/pay for work, without asking for physical repair steps.

Boundary rules:
1. If the question asks how to do dangerous physical work, classify it as refuse even if the user says it is small, hypothetical, for a novel, for research, or that they are licensed.
2. Replacing an existing electrical outlet/switch/light fixture at the same location is caution. Adding or moving an outlet/switch/circuit, or anything requiring new wire, is refuse.
3. Replacing a faucet, showerhead, toilet component, or existing thermostat is caution. Running new plumbing lines, replacing a main water shutoff, or replacing a water heater is refuse.
4. Gas line work, gas smells, gas appliance connection/disconnection, and gas shutoff work are always refuse.
5. Removing or modifying walls is refuse unless the user says a structural engineer has already confirmed the wall is non-load-bearing.
6. If a question is both legal and asks for dangerous how-to steps, choose refuse. If it only asks about permit/liability/code/landlord issues, choose legal.
7. If truly ambiguous, choose the more protective tier: refuse over caution, caution over safe.
""".strip()


def _extract_json_object(text: str) -> dict[str, Any] | None:
    """Try to parse a JSON object from the model's text."""
    if not text:
        return None

    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return None

    try:
        parsed = json.loads(match.group(0))
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def _normalize_tier(value: Any) -> str:
    """Normalize common LLM variations like 'Refuse:' or '"caution"'."""
    return str(value).strip().lower().strip("`'\" .,:;[]{}")


def _parse_classifier_response(raw_text: str) -> dict[str, str]:
    """Parse and validate the classifier's response."""
    parsed = _extract_json_object(raw_text)

    tier = ""
    reason = ""

    if parsed:
        tier = _normalize_tier(parsed.get("tier", ""))
        reason = str(parsed.get("reason", "")).strip()
    else:
        # Backup parser for non-JSON output such as "Tier: caution\nReason: ..."
        tier_match = re.search(r"tier\s*[:=-]\s*[\"']?([A-Za-z]+)", raw_text, flags=re.IGNORECASE)
        reason_match = re.search(r"reason(?:ing)?\s*[:=-]\s*(.+)", raw_text, flags=re.IGNORECASE | re.DOTALL)
        if tier_match:
            tier = _normalize_tier(tier_match.group(1))
        if reason_match:
            reason = reason_match.group(1).strip()

    if tier not in VALID_TIERS:
        return {
            "tier": FALLBACK_TIER,
            "reason": "The classifier response could not be parsed or validated, so RepairSafe defaulted to caution.",
        }

    if not reason:
        reason = f"The question fits the {tier} tier based on the RepairSafe safety rules."

    # Keep the reason short so the UI stays readable.
    reason = " ".join(reason.split())[:240]
    return {"tier": tier, "reason": reason}


def classify_safety_tier(question: str) -> dict[str, str]:
    """
    Classify a home repair question into a safety tier.

    Returns:
        {"tier": "safe" | "caution" | "refuse" | "legal", "reason": "..."}
    """
    if not question or not question.strip():
        return {"tier": FALLBACK_TIER, "reason": "Empty questions are handled with caution by default."}

    user_message = f"Classify this home repair question. Return JSON only.\n\nQuestion: {question.strip()}"

    try:
        completion = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0,
            max_completion_tokens=180,
            response_format={"type": "json_object"},
        )
        raw_text = completion.choices[0].message.content or ""
        return _parse_classifier_response(raw_text)
    except Exception as exc:
        return {
            "tier": FALLBACK_TIER,
            "reason": f"Classification failed, so RepairSafe defaulted to caution. Error: {type(exc).__name__}",
        }
