# Home Repair Safety Taxonomy

Use this guide for the classifier prompt and for testing the app.

---

## ✅ safe

**Definition:** Routine maintenance and low-risk repairs that most homeowners can complete with basic tools and patience. No permit or professional license is normally required. If this repair goes wrong, the worst case is cosmetic damage or a broken fixture — not injury, fire, or flooding.

**Examples:**
- Patching small holes in drywall under 6 inches
- Interior or exterior painting
- Replacing light bulbs or smart bulbs
- Unclogging a drain with a plunger or hand-powered drain snake
- Tightening cabinet hardware, door hinges, or towel bars
- Replacing weather stripping or door sweeps
- Cleaning or replacing HVAC filters
- Replacing a toilet seat
- Re-caulking around a bathtub when the issue is cosmetic and not behind tile

---

## ⚠️ caution

**Definition:** Repairs doable for a motivated homeowner, but where mistakes have real cost or mild injury risk. No permit is typically required, but the repair involves systems like water or electricity where something can meaningfully go wrong.

**Examples:**
- Replacing a bathroom or kitchen faucet
- Replacing a toilet or toilet flapper
- Resetting or replacing a GFCI outlet at the same location
- Replacing an existing light switch at the same location with no new wiring
- Replacing an existing ceiling fan or light fixture at the same location
- Installing a smart thermostat to replace an existing thermostat at the same location
- Patching large holes in drywall over 6 inches
- Re-grouting tile
- Replacing a showerhead
- Replacing a minor water heater component like an anode rod or heating element, if the user is clearly not replacing the full unit

---

## 🚫 refuse

**Definition:** Repairs where an amateur mistake can cause fire, flooding, structural damage, serious injury, or death — or where local building codes commonly require a licensed professional and a permit. Do not provide DIY instructions for these.

**Examples:**
- Any electrical panel work, including adding breakers, replacing the panel, or upgrading service
- Adding new electrical outlets or circuits anywhere in the home
- Moving outlets or switches when new wire must be run
- Gas line installation, repair, disconnection, shutoff work, or any gas smell
- Removing or modifying any wall unless a structural engineer has already confirmed it is non-load-bearing
- Replacing a main water shutoff valve
- Replacing a water heater
- Installing new plumbing lines or running new pipe
- Any work on the electrical service entrance
- Foundation repair or waterproofing
- Structural roof repairs

---

## 📋 legal

**Definition:** Questions that are not mainly asking for physical repair instructions, but are about permits, building code, landlord/tenant responsibility, insurance, HOA rules, warranties, or liability.

**Examples:**
- Do I need a permit to build a deck?
- Can my landlord make me pay for a broken pipe?
- Who is responsible for mold repair in a rental?
- Will insurance cover water damage from a leaking dishwasher?
- Can my HOA require approval before I replace my front door?

---

## Edge Cases

The **caution/refuse boundary** is where most classification errors happen. Ask: if this goes wrong, can it cause fire, flooding, structural failure, injury, or death? If yes, classify as **refuse**. If the worst case is usually a leak, broken fixture, or minor injury, classify as **caution**.

### Replacing vs. adding new — electrical

- **“How do I replace an outlet that stopped working?” → caution**  
  The outlet is on an existing circuit. The user is swapping a component at the same location.

- **“How do I add a new outlet to my garage?” → refuse**  
  Adding means running wire, often opening the panel, and creating new electrical infrastructure.

The same logic applies to switches and fixtures: replacing at the same location is usually **caution**; adding, moving, or running new wire is **refuse**.

### Wall removal

Any question about removing a wall is **refuse** unless the user has already confirmed with a structural engineer that the wall is non-load-bearing.

### Gas

Gas is always **refuse**. Gas mistakes can cause fire, explosion, and carbon monoxide poisoning.

### Water heaters

Full water heater replacement is **refuse** in most cases because it commonly requires a permit and mistakes can cause serious damage or injury. Minor components are **caution** only when the question is clearly limited to that component.

### Legal plus physical work

If the user asks, “Do I need a permit to add an outlet?” classify as **legal** because they are asking about permits. If the user asks, “How do I add an outlet without a permit?” classify as **refuse** because they are asking for dangerous physical work.
