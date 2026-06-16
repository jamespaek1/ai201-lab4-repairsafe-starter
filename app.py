import gradio as gr

from auditor import log_interaction
from responder import generate_safe_response
from safety import classify_safety_tier

# ---------------------------------------------------------------------------
# Example questions — includes safe, caution, refuse, boundary, and legal tiers
# ---------------------------------------------------------------------------
EXAMPLES = [
    "How do I patch a small hole in drywall?",
    "How do I unclog a slow bathroom drain?",
    "How do I replace a bathroom faucet?",
    "How do I reset a GFCI outlet that won't reset?",
    "Can I replace an electrical outlet that stopped working?",
    "Can I add a new electrical outlet to my garage?",
    "Can I upgrade my electrical panel to 200 amps myself?",
    "How do I fix a gas line that smells like it's leaking?",
    "Do I need a permit to build a deck?",
]

# ---------------------------------------------------------------------------
# Tier display config
# ---------------------------------------------------------------------------
TIER_CONFIG = {
    "safe": {
        "color": "#16a34a",
        "icon": "✅",
        "label": "SAFE TO DIY",
        "note": "This is a routine repair most homeowners can handle.",
    },
    "caution": {
        "color": "#d97706",
        "icon": "⚠️",
        "label": "PROCEED WITH CAUTION",
        "note": "This repair is doable, but mistakes have real cost. Read carefully.",
    },
    "refuse": {
        "color": "#dc2626",
        "icon": "🚫",
        "label": "PROFESSIONAL REQUIRED",
        "note": "This repair requires a licensed professional. Do not attempt DIY.",
    },
    "legal": {
        "color": "#2563eb",
        "icon": "📋",
        "label": "LEGAL / PERMIT QUESTION",
        "note": "This is mainly about permits, code, liability, or responsibility. Verify locally.",
    },
    "unknown": {
        "color": "#64748b",
        "icon": "⚙️",
        "label": "NOT YET CLASSIFIED",
        "note": "Complete Milestone 1 to enable safety classification.",
    },
}


def _tier_html(tier: str, reason: str) -> str:
    cfg = TIER_CONFIG.get(tier, TIER_CONFIG["unknown"])
    color = cfg["color"]
    icon = cfg["icon"]
    label = cfg["label"]
    note = cfg["note"]

    reason_block = (
        f'<div style="margin-top: 8px; font-size: 0.9rem; color: #475569;">'
        f'<strong>Why:</strong> {reason}'
        f'</div>'
        if reason and tier in ("safe", "caution", "refuse", "legal")
        else ""
    )

    return (
        f'<div style="border-left: 6px solid {color}; padding: 14px 16px; '
        f'background: #f8fafc; border-radius: 8px;">'
        f'<div style="font-weight: 800; color: {color}; font-size: 1.05rem;">'
        f'{icon} {label}'
        f'</div>'
        f'<div style="margin-top: 6px; color: #334155;">{note}</div>'
        f'{reason_block}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Core pipeline
# ---------------------------------------------------------------------------
def handle_question(question: str):
    if not question.strip():
        return "<p>Ask a repair question to see the safety tier.</p>", ""

    tier_result = classify_safety_tier(question)
    tier = tier_result.get("tier", "unknown")
    reason = tier_result.get("reason", "")

    response = generate_safe_response(question, tier)

    log_interaction(question, tier, response)

    return _tier_html(tier, reason), response


# ---------------------------------------------------------------------------
# Tier guide content (loaded once at startup)
# ---------------------------------------------------------------------------
def _load_tier_guide() -> str:
    try:
        with open("data/repair_tiers.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "_Tier guide not found. Make sure `data/repair_tiers.md` exists._"


TIER_GUIDE_CONTENT = _load_tier_guide()

# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------
THEME = gr.themes.Soft(
    primary_hue="orange",
    secondary_hue="red",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "sans-serif"],
)

CSS = """
#ask-btn {
    background: #ea580c;
    color: white;
    font-weight: 600;
}
#ask-btn:hover {
    background: #c2410c;
}
"""

with gr.Blocks(title="RepairSafe") as demo:
    gr.Markdown(
        """
        # RepairSafe

        **AI201 Lab 4 — Home Repair Safety Assistant**

        Ask any home repair question. RepairSafe classifies the risk before answering — not every repair should come with a confident "here's how."
        """
    )

    with gr.Tabs():
        with gr.Tab("Ask a Question"):
            with gr.Row():
                with gr.Column(scale=2):
                    question_box = gr.Textbox(
                        label="Your repair question",
                        placeholder="e.g. How do I replace a bathroom faucet?",
                        lines=3,
                    )
                    ask_btn = gr.Button("Ask RepairSafe →", elem_id="ask-btn")

                    gr.Markdown("---")
                    gr.Markdown("#### Try an example")
                    with gr.Row():
                        for ex in EXAMPLES:
                            short = ex[:40] + "…" if len(ex) > 40 else ex
                            btn = gr.Button(short, size="sm")
                            btn.click(fn=lambda e=ex: e, outputs=question_box)

                with gr.Column(scale=2):
                    gr.Markdown("#### Safety Classification")
                    tier_display = gr.HTML(value="<p>Result will appear here.</p>")

                    gr.Markdown("#### Response")
                    response_box = gr.Textbox(
                        label="",
                        lines=10,
                        interactive=False,
                        show_label=False,
                        placeholder="Response will appear here.",
                    )

            ask_btn.click(
                fn=handle_question,
                inputs=question_box,
                outputs=[tier_display, response_box],
            )
            question_box.submit(
                fn=handle_question,
                inputs=question_box,
                outputs=[tier_display, response_box],
            )

        with gr.Tab("Tier Guide"):
            gr.Markdown(
                """
                Use this reference while building your classifier. The taxonomy defines each tier and the edge cases where the caution/refuse boundary is easy to confuse.
                """
            )
            gr.Markdown(TIER_GUIDE_CONTENT)


if __name__ == "__main__":
    demo.launch(theme=THEME, css=CSS)
