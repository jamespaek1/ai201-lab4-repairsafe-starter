import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = "llama-3.3-70b-versatile"

LOG_FILE = "logs/audit.jsonl"
SUMMARY_LOG_FILE = "logs/session_summary.jsonl"

# Optional challenge: added a fourth tier for legal / permit / liability questions.
VALID_TIERS = {"safe", "caution", "refuse", "legal"}
