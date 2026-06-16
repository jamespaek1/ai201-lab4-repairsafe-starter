# Spec: `classify_safety_tier()`

**File:** `safety.py`  
**Status:** Complete

---

## Purpose

Determine whether a home repair question is safe to answer directly, requires a cautionary response, should be refused with a referral to a licensed professional, or is mainly a legal/permit/liability question.

---

## Input / Output Contract

**Input:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `str` | The user's home repair question |

**Output:** `dict`

| Key | Type | Description |
|-----|------|-------------|
| `"tier"` | `str` | One of: `"safe"`, `"caution"`, `"refuse"`, `"legal"` |
| `"reason"` | `str` | One sentence explaining why this tier was assigned |

---

## Design Decisions

### Tier definitions

**safe:**
```text
Routine maintenance or low-risk repairs most homeowners can do with basic tools; if done wrong, the likely worst case is cosmetic damage or a broken fixture, not injury, fire, flooding, structural damage, or death.
```

**caution:**
```text
DIY-doable repairs involving existing fixtures or existing water/electrical components where mistakes have real cost or mild injury risk, but no new infrastructure, permit, or licensed professional is normally required.
```

**refuse:**
```text
Repairs where an amateur mistake can cause fire, flooding, structural failure, serious injury, or death, or where the work normally requires a permit or licensed professional.
```

**legal:**
```text
Questions mainly about permits, building code, landlord/tenant responsibility, insurance, HOA rules, warranties, liability, or who is allowed to do/pay for work, without asking for physical repair steps.
```

---

### Classification approach

```text
I will give the LLM precise tier definitions plus few-shot-style boundary rules, especially for existing-location replacement versus adding new infrastructure. I will tell it to think internally but output only JSON. This gives it enough guidance for edge cases without returning long reasoning that is harder to parse. Ambiguous questions should choose the more protective tier: refuse over caution, caution over safe.
```

Tradeoffs:
- Definitions only are simple but may be inconsistent near the caution/refuse boundary.
- Definitions plus examples/boundary rules are more reliable because they show the exact distinctions the classifier will be tested on.
- Step-by-step reasoning can improve classification, but it may produce verbose output. I will ask it to reason internally and return structured JSON only.

---

### Output format

```json
{"tier":"safe|caution|refuse|legal","reason":"one short sentence"}
```

The code parses JSON first. If the model ignores the instruction, the backup parser looks for `Tier: X` and `Reason: Y`. The tier is normalized to lowercase, stripped of punctuation/quotes, and validated against `VALID_TIERS` before being returned.

---

### Prompt structure

**System message:**
```text
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
```

**User message:**
```text
Classify this home repair question. Return JSON only.

Question: {question}
```

---

### Caution/refuse boundary

```text
If an amateur mistake could cause fire, flooding, structural failure, serious injury, or death — or the work normally requires a permit/licensed professional — classify as refuse; otherwise, existing-location component swaps with manageable risk are caution.

Example 1: “Can I replace an electrical outlet that stopped working?” → caution because it is an existing circuit and same-location component swap.
Example 2: “Can I add a new electrical outlet to my garage?” → refuse because adding an outlet usually requires new wiring, panel work, and a permit.
Example 3: “Can I replace my own water heater?” → refuse because full water heater replacement commonly requires a permit and mistakes can cause serious harm.
```

---

### Fallback behavior

```text
If parsing fails or the tier is not in VALID_TIERS, the function returns {"tier":"caution", "reason":"The classifier response could not be parsed or validated, so RepairSafe defaulted to caution."}. Returning safe would fail open and could allow dangerous answers. Caution is a safer fallback because it includes warnings and professional recommendations while still letting the app function.
```

---

## Implementation Notes

**One classification that surprised you — question, tier you expected, tier it returned, and why:**
```text
Question: “Do I need a permit to replace a water heater?”
Expected: refuse at first, because water heater replacement itself is refuse.
Returned/desired after legal tier: legal, because this wording asks about permit requirements rather than asking how to replace the unit. If the user asks for the replacement steps, it should be refuse.
```

**One prompt change you made after seeing the first few outputs, and what it fixed:**
```text
I added the rule “If a question is both legal and asks for dangerous how-to steps, choose refuse. If it only asks about permit/liability/code/landlord issues, choose legal.” This prevents the new legal tier from accidentally overriding the safety refusal tier.
```
