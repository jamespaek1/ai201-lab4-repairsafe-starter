import json
import os
from collections import Counter
from datetime import datetime, timezone
from typing import Any

from config import LOG_FILE, SUMMARY_LOG_FILE, VALID_TIERS

SCHEMA_VERSION = 1
SUMMARY_EVERY_N_INTERACTIONS = 5


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _truncate(text: str, limit: int) -> str:
    text = str(text)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _ensure_log_directory(path: str) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def _read_jsonl(path: str) -> list[dict[str, Any]]:
    if not os.path.exists(path):
        return []

    records: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                records.append(record)
    return records


def _write_session_summary_if_needed() -> None:
    records = _read_jsonl(LOG_FILE)
    total = len(records)

    if total == 0 or total % SUMMARY_EVERY_N_INTERACTIONS != 0:
        return

    tier_counts = Counter(str(record.get("tier", "unknown")) for record in records)
    distribution = {tier: tier_counts.get(tier, 0) for tier in sorted(VALID_TIERS)}
    extra_tiers = sorted(set(tier_counts) - VALID_TIERS)
    for tier in extra_tiers:
        distribution[tier] = tier_counts[tier]

    summary = {
        "timestamp": _utc_timestamp(),
        "schema_version": SCHEMA_VERSION,
        "total_interactions": total,
        "tier_distribution": distribution,
        "recent_questions": [record.get("question", "") for record in records[-3:]],
    }

    _ensure_log_directory(SUMMARY_LOG_FILE)
    with open(SUMMARY_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(summary, ensure_ascii=False) + "\n")

    print(f"[SUMMARY] total={total} | distribution={distribution}")


def log_interaction(question: str, tier: str, response: str) -> None:
    """Append one interaction to logs/audit.jsonl as one JSON object per line."""
    question_text = str(question)
    response_text = str(response)
    normalized_tier = str(tier).strip().lower()

    record = {
        "timestamp": _utc_timestamp(),
        "schema_version": SCHEMA_VERSION,
        "tier": normalized_tier,
        "tier_valid": normalized_tier in VALID_TIERS,
        "question": _truncate(question_text, 300),
        "response_preview": _truncate(response_text, 200),
        "question_length": len(question_text),
        "response_length": len(response_text),
    }

    _ensure_log_directory(LOG_FILE)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    terminal_question = _truncate(" ".join(question_text.split()), 70)
    print(f'[LOGGED] tier={normalized_tier} | "{terminal_question}" → {len(response_text)} chars')

    _write_session_summary_if_needed()
