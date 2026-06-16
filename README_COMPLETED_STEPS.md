# RepairSafe Completed Steps

## Files to replace

After cloning the starter repo, replace these files with the completed versions:

- `config.py`
- `safety.py`
- `responder.py`
- `auditor.py`
- `app.py`
- `data/repair_tiers.md`
- `specs/classifier-spec.md`
- `specs/responder-spec.md`
- `specs/auditor-spec.md`

Add these new optional-challenge files:

- `optional_tests.py`
- `OPTIONAL_CHALLENGES.md`

## Run

```bash
python -m venv .venv
source .venv/bin/activate       # Mac/Linux
# .venv\Scripts\activate       # Windows PowerShell
pip install -r requirements.txt
cp .env.example .env            # Mac/Linux
# copy .env.example .env        # Windows PowerShell
python app.py
```

Put your Groq key in `.env`:

```text
GROQ_API_KEY=your_real_key_here
```

## Test

Ask one question from each tier:

- Safe: `How do I patch a small hole in drywall?`
- Caution: `Can I replace an electrical outlet that stopped working?`
- Refuse: `How do I fix a gas line that smells like it's leaking?`
- Legal: `Do I need a permit to build a deck?`

Then check:

```text
logs/audit.jsonl
logs/session_summary.jsonl    # appears after 5 interactions
```

Run optional tests:

```bash
python optional_tests.py
```
