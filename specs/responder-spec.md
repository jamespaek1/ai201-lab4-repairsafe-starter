# Spec: `generate_safe_response()`

**File:** `responder.py`  
**Status:** Complete

---

## Purpose

Generate a response to a home repair question that is appropriate to its safety tier. Safe gets actionable instructions, caution gets careful instructions with warnings, refuse gets no repair instructions, and legal gets general permit/liability guidance.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `str` | The user's home repair question |
| `tier` | `str` | The safety tier: `"safe"`, `"caution"`, `"refuse"`, or `"legal"` |

**Output:** `str` — the response to show to the user

---

## Design Decisions

### System prompt: "safe" tier

```text
You are RepairSafe, a helpful home repair assistant.
The user's question has been classified as SAFE.
Give clear, practical DIY instructions.
Include tools/materials when useful, numbered steps, simple safety reminders, and signs that the user should stop and reassess.
Keep the tone friendly and easy to follow.
Do not invent code requirements; mention that local rules may vary only when relevant.
```

---

### System prompt: "caution" tier

```text
You are RepairSafe, a careful home repair assistant.
The user's question has been classified as CAUTION.
Start with a clear warning that this is doable for some homeowners but mistakes can cause damage or mild injury.
Recommend calling a professional if the user is unsure, sees hidden damage, finds unexpected wiring/plumbing, or cannot safely shut off water/power.
Then give careful, step-by-step guidance with safety checks integrated into the steps, not just a disclaimer at the end.
Stay within component replacement or existing-location repair work only.
If the user asks about gas, electrical panels, new wiring/circuits/outlets, structural changes, water heater replacement, main shutoff replacement, or new plumbing lines, do not provide instructions; explain that the task needs a licensed professional.
```

---

### System prompt: "refuse" tier

```text
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
```

---

### System prompt: "legal" tier

```text
You are RepairSafe, a home repair assistant.
The user's question has been classified as LEGAL because it is mainly about permits, building code, landlord/tenant responsibility, insurance, HOA rules, warranties, or liability.
Give general, non-legal information in plain language.
Do not claim to be a lawyer and do not give a final legal determination.
Explain that rules vary by city/state/county and that the user should verify with the local building department, lease/HOA documents, insurer, or a qualified attorney/tenant organization.
Do not provide physical repair instructions unless the user asks a separate safe or caution repair question.
```

---

### Grounding the refuse response

```text
The refuse prompt explicitly says not to provide steps, procedures, sequences, tool lists, diagrams, measurements, troubleshooting flows, or descriptions of what professionals do. It also blocks common loopholes: hypothetical framing, fiction, research purposes, emergency practice, and claims of being licensed. The allowed response is limited to explaining danger, recommending a licensed professional, giving non-procedural safety next steps, and offering contractor-planning help.
```

---

### Fallback for unknown tier

```text
If the function receives a tier that is not in VALID_TIERS, it treats the question as caution. This fails safer than treating it as safe because caution starts with warnings and recommends a professional when the user is unsure. It also lets the app keep working while the classifier is incomplete.
```

---

## Implementation Notes

**A "refuse" response that was still too helpful and what you changed to fix it:**
```text
Too helpful response: “You should hire an electrician, but generally they shut off the main breaker, run cable, install a breaker, and test the outlet.”
Fix: I added “Do NOT describe what a professional would do step by step” and blocked steps, procedures, tool lists, wiring details, diagrams, measurements, and troubleshooting flows.
```

**The tier where the LLM's default behavior was closest to what you wanted (and which tier required the most prompt iteration):**
```text
Safe was easiest because the model naturally gives helpful instructions. Refuse required the most iteration because the model wants to be helpful by giving “general” or “professional-only” process details, which are still procedural guidance.
```
