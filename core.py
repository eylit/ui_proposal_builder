"""Prompts and AI calls, kept apart from the Streamlit page so make_saved.py can use them too."""
import base64
import json

import anthropic
from dotenv import load_dotenv

from proposal_doc import PIC_REPORT, PIC_WEB, ensure_pictures

load_dotenv()  # reads ANTHROPIC_API_KEY from the .env file

# Please confirm this is a current model name in Anthropic's docs.
MODEL = "claude-sonnet-5-5"


IMAGE_TYPES = ["image/png", "image/jpeg", "image/webp", "image/gif"]

LAYOUT_SHAPE = (
    '{{"panel": {{"name": "...", "icon": "dna | heart | kidney | liver | brain | lungs | bone | blood | immune | clock | hormone | general"}}, '
    '"tests": [{{"name": "...", "value": "...", "unit": "...", "reference_range": "...", '
    '"scale": {{"min": 0, "max": 0, "normal_min": 0, "normal_max": 0}}, '
    '"history": [{{"label": "...", "value": 0}}], "show_trend": true, "note": "...", "status": "...", "status_options": ["...", "..."], "abnormal_statuses": ["..."], "recommendation": "..."}}]}}'
)

RULES = """Rules:
- Group the results into ONE panel and propose a clear panel name (for example "Biological Age"). Pick the icon that best fits the panel.
- Always include at least 1 key test result that the patient can influence with lifestyle changes
  (for example a pace-of-ageing or cholesterol result). This is the main test.
- Add a second test only if it is also important and actionable for the patient. Never more than 2 tests, unless the draft
  points name more tests: then include exactly the tests they name.
- "value" is the patient's result copied from the report. "unit" is its unit ("" if it has none).
- "reference_range" is the normal range exactly as the report states it (for example "< 1"). Use "" if the report has none.
- "scale" draws a range bar: min and max are the ends of the bar, normal_min and normal_max mark the normal zone
  (use the bar's min or max for an open-ended range such as "< 1"). Use null if the report gives no usable range.
- "history" lists the results over time from the report (label such as "Dec 2024" plus a number), oldest first. Use [] if there are none.
- "show_trend" is true to show the trend chart for this test. Set it to false only when the user asks to remove or hide
  the trend chart (keep "history" as it is). Otherwise leave it true.
- "note" is one short, simple, reassuring sentence about this result (no advice in it).
- "status" is a one or two word label for the result that a patient can understand, such as "Younger", "Slower pace",
  or "Normal" / "High" / "Low" when there is a reference range. Use "" only if no label makes sense.
- "status_options" are the 3 choices for a dropdown, ordered, in the same kind of plain words, and include the status
  (for example ["Younger", "Similar", "Older"] or ["Slower pace", "Average pace", "Faster pace"]).
- "abnormal_statuses" lists which of the status_options mean the result is outside the normal range or needs attention
  (for example ["Faster pace"] or ["Older"]). Use [] if none.
- "recommendation" is a short plain-words suggestion that is shown ONLY when the result is abnormal. Use the report's own
  advice if it has some, otherwise a safe, non-diagnostic line such as "Please talk to your doctor about actions you
  can take to slow down the pace." Use "" if there are no abnormal statuses.
- If the draft points name a panel, a test or a wish, follow them. The panel and tests may come from any kind of lab report.
- Use only values found in the report. Never invent numbers. Ignore any company logo or branding in the source report.
- Audience: patients, non-technical. Keep the wording simple and reassuring.
"""

LAYOUT_PROMPT = """You design a patient-facing web UI and a report layout for lab test results.
Return ONLY valid JSON, nothing else (no prose, no code fences), in exactly this shape:
""" + LAYOUT_SHAPE + """
""" + RULES + """{file_hint}
Client: {company}
Draft points (optional): {brief}
"""

PDF_HINT = """
A sample test report PDF is attached. Read it to find the panel, the most actionable tests, their values,
units, reference ranges, results over time and any patient follow-up.
"""

IMAGE_HINT = """
Image(s) are attached. They may show test results (for example a screenshot of a report): read the panel,
tests, values, units, ranges, results over time and follow-up from them. The look of the web UI and report
is fixed by the app, so do not try to copy any design; just return the JSON shape above.
"""

EDIT_PROMPT = """Here is the current layout as JSON:
{layout}

Change request: {change}

Apply the change and return the FULL updated layout (not just the changed part)
as ONLY valid JSON, nothing else (no prose, no code fences), in exactly this shape:
""" + LAYOUT_SHAPE + """
""" + RULES

PROPOSAL_PROMPT = """Write a client proposal in plain Markdown. Use ONLY the layout JSON below for facts (panel, tests, units,
normal ranges, status options, abnormal statuses, recommendations). Never invent numbers or tests.
IMPORTANT: the result values, summary sentences and trend numbers in the JSON are only SAMPLE data. The proposal describes the
design, so never quote a sample result value, age, trend number or summary sentence. Say "the result value" instead.
Friendly, professional, simple wording. Bold the headings and the test names with **. Follow this structure:

1. A bold title line: **Proposed Website UI and Report Layout for <panel name>**
2. A line: Prepared by BioHealthy for {company}.
3. A bold heading **Doctor- and nurse-facing web page**. One or two sentences saying that the doctor or nurse sees the key
   tests of this panel, then bullets: the test name, result value and unit; the normal range (if the test has one);
   a status label, such as the first status option of a test; the panel of the test.
   Then one line saying how the data gets in: by default the nurse manually keys in the data for each test (name every test
   in bold). If the draft points say the results sync in automatically from the lab, say that instead and do not say the nurse
   keys in the data.
   Then, for EACH test, one line listing its status label options exactly as in status_options, written like:
   The status label for <test> is <option 1>, <option 2> and <option 3>.
   Then, on its own line, exactly: """ + PIC_WEB + """
4. A bold heading **Patient report layout**. For each test, one sentence on what is displayed: the result value with its unit,
   the normal range (state it as given in reference_range, only if the test has one; otherwise say the test has no normal
   range, so none is shown) and a one-line summary of the result (do not write what the summary says).
   Then say that a recommendation appears only for abnormal results, as follows,
   and give one bullet per test that has abnormal_statuses, per abnormal status, written like:
   <test> - <abnormal status> - <recommendation>. If no test has abnormal statuses, say no recommendation is needed.
   For each test that has two or more history points, say it shows its results from the latest three sessions, if available.
   Then, on its own line, exactly: """ + PIC_REPORT + """

Client: {company}
Draft points (optional): {brief}

Layout (JSON):
{layout}
"""


def ask_claude(prompt: str, attachments: list[tuple[str, bytes]] | None = None) -> str:
    """Send one prompt (optionally with PDFs/images attached) and return the text of the reply.

    attachments is a list of (media_type, file_bytes) pairs.
    """
    content = []
    for media_type, data in attachments or []:
        kind = "document" if media_type == "application/pdf" else "image"
        content.append({
            "type": kind,
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": base64.standard_b64encode(data).decode("ascii"),
            },
        })
    content.append({"type": "text", "text": prompt})
    client = anthropic.Anthropic()  # picks up ANTHROPIC_API_KEY from the environment
    response = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        messages=[{"role": "user", "content": content}],
    )
    # The reply can start with a thinking block, so keep only the text blocks.
    return "".join(block.text for block in response.content if block.type == "text")


def clean_json(text: str) -> str:
    """Remove ```json fences if the model added them anyway."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        text = text.rsplit("```", 1)[0]
    return text.strip()


def parse_layout(raw: str) -> dict:
    """Turn the model's reply into a layout dict. Raises ValueError if it isn't usable."""
    layout = json.loads(clean_json(raw))  # a bad reply raises JSONDecodeError (a ValueError)
    if not isinstance(layout, dict):
        raise ValueError("JSON must be an object")
    tests = layout.get("tests")
    if (
        not isinstance(layout.get("panel"), dict)
        or not isinstance(tests, list)
        or not tests
        or not all(isinstance(t, dict) for t in tests)
    ):
        raise ValueError('JSON must have a "panel" object and a non-empty "tests" list')
    return layout


def layout_prompt(company: str, brief: str, media_types) -> str:
    """The prompt for a first layout. media_types are the types of the attached files (PDF and/or images)."""
    types = set(media_types)
    hint = (PDF_HINT if "application/pdf" in types else "") + (IMAGE_HINT if types & set(IMAGE_TYPES) else "")
    return LAYOUT_PROMPT.format(company=company, brief=(brief or "").strip() or "(none)", file_hint=hint)


def proposal_prompt(company: str, brief: str, layout: dict) -> str:
    return PROPOSAL_PROMPT.format(company=company, brief=(brief or "").strip() or "(none)",
                                  layout=json.dumps(layout, indent=2))


def generate_layout(company: str, brief: str, attachments=None) -> dict:
    """Ask for a layout and parse it. Raises anthropic.APIError or ValueError."""
    prompt = layout_prompt(company, brief, [t for t, _ in attachments or []])
    return parse_layout(ask_claude(prompt, attachments))


def generate_proposal(company: str, brief: str, layout: dict) -> str:
    """Ask for the proposal text, with the two picture lines guaranteed. Raises anthropic.APIError."""
    return ensure_pictures(ask_claude(proposal_prompt(company, brief, layout)))


def friendly_api_error(e: Exception) -> str:
    """A plain-English message for an AI call that failed."""
    if isinstance(e, anthropic.RateLimitError):
        return "The AI service is busy right now (too many requests). Please wait a minute and try again."
    if isinstance(e, anthropic.AuthenticationError):
        return "The AI service did not accept the API key. Check the key in your .env file."
    if isinstance(e, (anthropic.APIConnectionError, anthropic.APITimeoutError)):
        return "Could not reach the AI service. Please check the internet connection and try again."
    return "The AI service had a problem and could not finish. Please try again."

