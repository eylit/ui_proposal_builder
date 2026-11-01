import copy
import html
import json
import math
import os
from pathlib import Path

import anthropic
import streamlit as st

from core import (
    EDIT_PROMPT,
    IMAGE_TYPES,
    ask_claude,
    friendly_api_error,
    generate_proposal,
    layout_prompt,
    parse_layout,
)
from helpers import is_abnormal, num, recommendation_text
from pictures import logo_png, report_png, web_ui_png
from saved import get_saved
from samples import SAMPLES
from proposal_doc import build_docx, split_proposal
from theme import BLUSH, BRAND_FONT, DARK, GOLD, GREEN, ORANGE, SAND

MAX_PDF_MB = 10
MAX_IMAGE_MB = 5  # the API limit for one image
MAX_FILES = 5

def load_saved_result(i: int) -> None:
    """Button callback: show the saved layout and proposal for sample i. Makes no AI call."""
    entry = get_saved(i)
    if not entry:
        st.session_state["saved_notice"] = "There is no saved result for this sample yet. Run make_saved.py once to create them."
        return
    st.session_state.pop("saved_notice", None)
    st.session_state["layout"] = copy.deepcopy(entry["layout"])
    st.session_state["layout_version"] = st.session_state.get("layout_version", 0) + 1
    if entry.get("proposal"):
        st.session_state["proposal"] = entry["proposal"]
    else:
        st.session_state.pop("proposal", None)
    st.session_state["company"] = SAMPLES[i]["company"]
    st.session_state["draft_points"] = SAMPLES[i]["brief"]
    st.session_state["sample_idx"] = i
    st.session_state["sample_report"] = None
    st.session_state["request"] = ""
    st.session_state["loaded_saved"] = entry.get("source", "model")


def show_failure(message: str, offer_saved: bool = False, raw: str | None = None) -> None:
    """A friendly message when an AI call fails, plus a way forward with a saved result when there is one."""
    st.warning(message)
    if raw:
        with st.expander("What the AI replied"):
            st.code(raw)
    if offer_saved:
        idx = st.session_state.get("sample_idx")
        if idx is not None and get_saved(idx):
            st.button("Load saved result", key="fallback_load", on_click=load_saved_result, args=(idx,))
        else:
            st.caption("Tip: the sample buttons come with saved results you can load without the AI.")


def request_layout(prompt: str, attachments: list[tuple[str, bytes]] | None = None, offer_saved: bool = False):
    """Ask the model for a layout. On any failure show a friendly message and return None."""
    try:
        raw = ask_claude(prompt, attachments)
    except anthropic.APIError as e:
        show_failure(friendly_api_error(e) + (" Your current layout is unchanged." if not offer_saved else ""), offer_saved)
        return None
    try:
        return parse_layout(raw)
    except ValueError:
        show_failure(
            "The AI replied, but not in a form this page could read. Please try again."
            + (" Your current layout is unchanged." if not offer_saved else ""),
            offer_saved,
            raw,
        )
        return None


# Built-in icon set: 24x24 line icons. The AI only picks a name from this list.
ICONS = {
    "dna": '<path d="M7 3c0 5 10 5 10 9s-10 4-10 9"/><path d="M17 3c0 5-10 5-10 9s10 4 10 9"/><path d="M8.5 6.5h7M8.5 17.5h7"/>',
    "heart": '<path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.5-7 10-7 10z"/>',
    "kidney": '<path d="M14 4C9 4 6 8 6 12s3 8 8 8c2.5 0 3-2 1.5-3.5-2-2-2-7 0-9C17 6 16.5 4 14 4z"/>',
    "liver": '<path d="M3 10c0-3 3-5 8-5 6 0 10 3 10 7 0 4-4 7-9 7-3 0-4-2-6-3-2-1-3-3-3-6z"/>',
    "brain": '<path d="M12 5a3.5 3.5 0 0 0-6.5 1.5A3.5 3.5 0 0 0 4 12a3.5 3.5 0 0 0 2 3.2A3.5 3.5 0 0 0 12 18z"/><path d="M12 5a3.5 3.5 0 0 1 6.5 1.5A3.5 3.5 0 0 1 20 12a3.5 3.5 0 0 1-2 3.2A3.5 3.5 0 0 1 12 18z"/>',
    "lungs": '<path d="M12 4v8"/><path d="M12 8C8 8 5 13 5 17a2 2 0 0 0 3 1.5l4-2.5z"/><path d="M12 8c4 0 7 5 7 9a2 2 0 0 1-3 1.5l-4-2.5z"/>',
    "bone": '<path d="M7 6a2 2 0 1 1 3 2l6 6a2 2 0 1 1 2 3 2 2 0 1 1-3-2L9 9a2 2 0 0 1-2-3z"/>',
    "blood": '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
    "immune": '<path d="M12 3l7 3v5c0 5-3 8-7 10-4-2-7-5-7-10V6z"/><path d="M9 12l2 2 4-4"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "hormone": '<path d="M12 3l7 4v8l-7 4-7-4V7z"/><circle cx="12" cy="11" r="2"/>',
    "general": '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M12 9v7M8.5 12.5h7"/>',
}


def icon_svg(name: str, colour: str, size: int = 28) -> str:
    """Inline SVG for a named icon; unknown names fall back to the general icon."""
    shapes = ICONS.get(name if isinstance(name, str) else "", ICONS["general"])
    return (
        f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{colour}" '
        f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{shapes}</svg>'
    )


def esc(value) -> str:
    """Escape text for HTML. $ is escaped too so Streamlit does not treat it as maths."""
    return html.escape(str(value)).replace("$", "&#36;")


def range_bar_html(test: dict) -> str:
    """Horizontal bar with a normal zone and a marker for the result. Empty if there is no usable scale."""
    scale = test.get("scale")
    if not isinstance(scale, dict):
        return ""
    lo, hi, value = num(scale.get("min")), num(scale.get("max")), num(test.get("value"))
    if lo is None or hi is None or hi <= lo or value is None:
        return ""

    def pos(x: float) -> float:
        return max(0.0, min(100.0, (x - lo) / (hi - lo) * 100))

    n_lo, n_hi = num(scale.get("normal_min")), num(scale.get("normal_max"))
    zone = ""
    if n_lo is not None or n_hi is not None:
        start = pos(lo if n_lo is None else n_lo)
        end = pos(hi if n_hi is None else n_hi)
        if end > start:
            zone = (
                f'<div style="position:absolute;left:{start:.1f}%;width:{end - start:.1f}%;height:100%;'
                f'background:{GREEN};border-radius:7px"></div>'
            )
    return (
        '<div style="position:relative;margin:24px 4px 4px 4px">'
        f'<div style="position:absolute;left:{pos(value):.1f}%;top:-18px;transform:translateX(-50%);'
        f'color:{DARK};font-size:13px">&#9660;</div>'
        f'<div style="position:relative;height:14px;background:{ORANGE if zone else BLUSH};border-radius:7px">{zone}</div>'
        f'<div style="display:flex;justify-content:space-between;font-size:11px;color:{DARK};opacity:0.65">'
        f'<span>{lo:g}</span><span>{hi:g}</span></div></div>'
    )


def trend_svg(history) -> str:
    """Small line chart of results over time, with a labelled dot per point. Empty if no numeric points."""
    points = []
    for item in history if isinstance(history, list) else []:
        if isinstance(item, dict) and num(item.get("value")) is not None:
            points.append((str(item.get("label", "")), num(item["value"])))
    if not points:
        return ""
    w, h, left, right, top, bottom = 300, 130, 26, 26, 28, 28
    values = [v for _, v in points]
    vmin, vmax = min(values), max(values)
    if vmax == vmin:  # flat history: centre the line
        vmin, vmax = vmin - 1, vmax + 1

    def px(i: int) -> float:
        return left + (w - left - right) * (i / (len(points) - 1) if len(points) > 1 else 0.5)

    def py(v: float) -> float:
        return top + (h - top - bottom) * (1 - (v - vmin) / (vmax - vmin))

    grid = "".join(
        f'<line x1="{left}" x2="{w - right}" y1="{y:.1f}" y2="{y:.1f}" stroke="{SAND}" stroke-width="1"/>'
        for y in (top, (top + h - bottom) / 2, h - bottom)
    )
    line = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, (_, v) in enumerate(points))
    marks = ""
    for i, (label, v) in enumerate(points):
        fill = DARK if i == len(points) - 1 else "#fff"
        marks += (
            f'<circle cx="{px(i):.1f}" cy="{py(v):.1f}" r="5" fill="{fill}" stroke="{GOLD}" stroke-width="2"/>'
            f'<text x="{px(i):.1f}" y="{py(v) - 10:.1f}" text-anchor="middle" font-size="11" '
            f'font-weight="bold" fill="{DARK}">{v:g}</text>'
            f'<text x="{px(i):.1f}" y="{h - 8}" text-anchor="middle" font-size="10" '
            f'fill="{DARK}" opacity="0.65">{esc(label)}</text>'
        )
    return (
        f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:auto;display:block">{grid}'
        f'<polyline fill="none" stroke="{GOLD}" stroke-width="2" points="{line}"/>{marks}</svg>'
    )


def sample_trend_svg() -> str:
    """Faded example chart (no numbers) so the reader can picture a trend when the report has no history."""
    w, h, left, right, top, bottom = 300, 130, 26, 26, 28, 28
    xs = [left, (left + w - right) / 2, w - right]
    ys = [top + 10, h - bottom - 14, top + 38]
    grid = "".join(
        f'<line x1="{left}" x2="{w - right}" y1="{y:.1f}" y2="{y:.1f}" stroke="{SAND}" stroke-width="1"/>'
        for y in (top, (top + h - bottom) / 2, h - bottom)
    )
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    marks = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#fff" stroke="{GOLD}" stroke-width="2"/>'
        f'<text x="{x:.1f}" y="{h - 8}" text-anchor="middle" font-size="10" fill="{DARK}" opacity="0.65">Test {i}</text>'
        for i, (x, y) in enumerate(zip(xs, ys), 1)
    )
    return (
        f'<div style="opacity:0.55"><svg viewBox="0 0 {w} {h}" style="width:100%;height:auto;display:block">{grid}'
        f'<polyline fill="none" stroke="{GOLD}" stroke-width="2" stroke-dasharray="5 4" points="{line}"/>{marks}</svg>'
        f'<div style="text-align:center;font-size:12px;font-style:italic">'
        f'Example trend - your results over time will appear here</div></div>'
    )


def render_web_ui(layout: dict, version: int) -> None:
    """Website UI as a form: panel header bar, then editable fields for each test.

    Result and reference range are text boxes, status is a dropdown. Edits are written back into
    the layout so the report view, the raw JSON and later AI calls all see them. `version` goes into
    the widget keys so a freshly generated layout starts with fresh fields.
    """
    panel = layout.get("panel", {})
    st.markdown(
        f'<div style="font-family:{BRAND_FONT};background:{DARK};color:#fff;text-align:center;'
        f'padding:10px;font-size:18px">{esc(panel.get("name", "Panel"))}</div>',
        unsafe_allow_html=True,
    )
    for i, test in enumerate(layout.get("tests", [])):
        key = f"v{version}_t{i}"
        with st.container(border=True):
            st.markdown(
                f'<div style="font-family:{BRAND_FONT};font-weight:bold;font-size:17px;color:{DARK}">'
                f'{esc(test.get("name", "Test"))}</div>',
                unsafe_allow_html=True,
            )
            unit = str(test.get("unit") or "").strip()
            test["value"] = st.text_input(
                f"Result ({unit})" if unit else "Result", value=str(test.get("value") or ""), key=f"{key}_value"
            )
            # Show the reference range if there is one (or if it was just cleared, so the box stays put).
            if test.get("reference_range") or f"{key}_ref" in st.session_state:
                test["reference_range"] = st.text_input(
                    "Reference range", value=str(test.get("reference_range") or ""), key=f"{key}_ref"
                )
            status = str(test.get("status") or "").strip()
            options = [str(o) for o in test.get("status_options") or [] if str(o).strip()]
            if status and status not in options:
                options.append(status)
            if options:
                choice = st.selectbox(
                    "Status", options, index=options.index(status) if status else None, key=f"{key}_status"
                )
                test["status"] = choice or ""


def render_report(layout: dict) -> None:
    """Designed report view: panel header with icon, then one card per test with value, note,
    patient follow-up, range bar and trend chart."""
    panel = layout.get("panel", {})
    out = (
        f'<div style="font-family:{BRAND_FONT};color:{DARK}">'
        f'<div style="display:flex;align-items:center;gap:10px;background:{DARK};color:#fff;'
        f'padding:12px 16px;border-radius:8px 8px 0 0;font-size:20px;font-weight:bold">'
        f'{icon_svg(panel.get("icon"), "#fff", 26)}{esc(panel.get("name", "Panel"))}</div>'
    )
    for test in layout.get("tests", []):
        unit = f' <span style="font-size:14px;opacity:0.65">{esc(test["unit"])}</span>' if test.get("unit") else ""
        note = f'<div style="margin-top:6px;font-size:13px;opacity:0.8">{esc(test["note"])}</div>' if test.get("note") else ""
        # The recommendation shows only while the chosen status is abnormal (the nurse can change the status).
        recommendation = (
            f'<div style="margin-top:8px;padding-left:8px;border-left:3px solid {GOLD};font-size:13px">'
            f'{esc(recommendation_text(test))}</div>'
            if is_abnormal(test)
            else ""
        )
        reference = (
            f'<div style="margin-top:8px;font-size:13px">Normal range: <b>{esc(test["reference_range"])}</b></div>'
            if test.get("reference_range")
            else ""
        )
        # The faded example chart fills in when there is no history, unless the user asked to remove the chart.
        trend = "" if test.get("show_trend") is False else (trend_svg(test.get("history")) or sample_trend_svg())
        chart = f'<div style="flex:1.2 1 260px">{trend}</div>' if trend else ""
        out += (
            f'<div style="display:flex;flex-wrap:wrap;gap:16px;border:1px solid {SAND};border-top:none;'
            f'padding:16px;background:#fff">'
            f'<div style="flex:1 1 220px"><div style="font-size:16px;font-weight:bold">{esc(test.get("name", "Test"))}</div>'
            f'<div style="margin-top:4px"><span style="font-size:36px;font-weight:300">{esc(test.get("value", ""))}</span>{unit}</div>'
            f'{note}{recommendation}{reference}{range_bar_html(test)}</div>'
            f'{chart}</div>'
        )
    st.markdown(out + "</div>", unsafe_allow_html=True)


st.title("Web UI and Report Layout Proposal Builder (Demo)")

if not os.getenv("ANTHROPIC_API_KEY"):
    st.error("No API key found. Paste your key into the .env file (ANTHROPIC_API_KEY=...) and restart.")
    st.stop()

def pick_sample(i: int) -> None:
    """Button callback: fill Client Name and the draft points, and attach the sample's report. No API call."""
    sample = SAMPLES[i]
    st.session_state["company"] = sample["company"]
    st.session_state["request"] = sample["brief"]
    st.session_state["sample_report"] = sample["report"]
    st.session_state["sample_idx"] = i


def remove_sample_report() -> None:
    st.session_state["sample_report"] = None


st.session_state.setdefault("company", "Longevity Analytics")
if "layout" not in st.session_state:  # samples fill the form, so they only make sense before a layout exists
    st.caption("Try a sample (invented data). It fills the client name and draft points; nothing is sent until you generate.")
    for col, (i, sample) in zip(st.columns(len(SAMPLES)), enumerate(SAMPLES)):
        col.button(sample["name"], key=f"sample_{i}", on_click=pick_sample, args=(i,), use_container_width=True)
    if st.session_state.get("sample_idx") is not None:
        st.button(
            "Load saved result",
            key="load_saved",
            on_click=load_saved_result,
            args=(st.session_state["sample_idx"],),
            help="Shows a ready-made layout and proposal for this sample. No AI call is made.",
        )
    if st.session_state.get("saved_notice"):
        st.info(st.session_state["saved_notice"])
company = st.text_input("Client Name", key="company")
files = st.file_uploader(
    "Upload files",
    type=["pdf", "png", "jpg", "jpeg", "webp", "gif"],
    accept_multiple_files=True,
    help="The test report (PDF, or a screenshot of it). No reference design is needed: the web UI and report layout are built in.",
)
if st.session_state.get("sample_report") and "layout" not in st.session_state:
    note_col, remove_col = st.columns([12, 1], vertical_alignment="center")
    note_col.info(f"Sample report attached: {Path(st.session_state['sample_report']).name}")
    remove_col.button(
        ":material/close:", key="remove_sample_report", on_click=remove_sample_report, help="Remove the sample report"
    )


def check_files(files) -> tuple[list[tuple[str, bytes]], str | None]:
    """Return (attachments, error). error is a message to show if a file is not usable."""
    if len(files) > MAX_FILES:
        return [], f"Please upload at most {MAX_FILES} files."
    attachments = []
    for f in files:
        is_pdf = f.type == "application/pdf"
        if not is_pdf and f.type not in IMAGE_TYPES:
            return [], f"{f.name}: unsupported file type."
        limit = MAX_PDF_MB if is_pdf else MAX_IMAGE_MB
        if f.size > limit * 1024 * 1024:
            return [], f"{f.name} is over {limit} MB. Please upload a smaller file."
        attachments.append((f.type, f.getvalue()))
    return attachments, None


def save_layout(layout: dict, draft_points: str | None = None) -> None:
    """Store a new layout, reset the dependent state, clear the request box and redraw the page."""
    st.session_state["layout"] = layout
    st.session_state["layout_version"] = st.session_state.get("layout_version", 0) + 1
    st.session_state.pop("loaded_saved", None)
    if draft_points is not None:  # a brand new layout: the old proposal no longer matches
        st.session_state.pop("proposal", None)
        st.session_state["draft_points"] = draft_points  # kept for the proposal
    st.session_state["clear_request"] = True
    st.rerun()


# One request box: draft points before a layout exists, a change request after.
if st.session_state.pop("clear_request", False):
    st.session_state["request"] = ""  # must be set before the box is drawn
has_layout = "layout" in st.session_state
request = st.text_area(
    "Describe a change" if has_layout else "Draft points on test",
    key="request",
    height=100 if has_layout else 320,  # tall while drafting (the sample briefs are long), short for a quick change
    placeholder=(
        "e.g. remove the trend chart, or retest in 6 months instead of 3"
        if has_layout
        else "Share your expectation on how the test should appear in the website & report"
    ),
)

if not has_layout:
    if st.button("Generate web UI and report layout"):
        attachments, file_error = check_files(files or [])
        sample_path = st.session_state.get("sample_report")
        if sample_path and not file_error:
            try:
                attachments = [("application/pdf", (Path(__file__).parent / sample_path).read_bytes())] + attachments
            except OSError:
                file_error = "The sample report file is missing. Run make_sample_reports.py (or remove the sample report)."
        if file_error:
            st.error(file_error)
        else:
            prompt = layout_prompt(company, request, [t for t, _ in attachments])
            with st.spinner("Asking the model for a layout..."):
                layout = request_layout(prompt, attachments, offer_saved=True)
            if layout is not None:
                save_layout(layout, request.strip())
else:
    apply_col, start_col, _ = st.columns([1, 1, 4])
    if apply_col.button("Apply change"):
        if not request.strip():
            st.warning("Type a change first.")
        else:
            with st.spinner("Updating the layout..."):
                updated = request_layout(
                    EDIT_PROMPT.format(layout=json.dumps(st.session_state["layout"], indent=2), change=request)
                )
            if updated is not None:  # on failure the old layout stays as it was
                save_layout(updated)
    if start_col.button("Start over"):
        for k in ("layout", "proposal", "draft_points", "sample_report", "sample_idx", "loaded_saved", "saved_notice"):
            st.session_state.pop(k, None)
        st.session_state["clear_request"] = True
        st.rerun()

if "layout" in st.session_state:
    if st.session_state.get("loaded_saved"):
        st.caption(
            "Showing a saved result made earlier with the AI. No AI call was made."
            if st.session_state["loaded_saved"] == "model"
            else "Showing a saved example written by hand. No AI call was made. Run make_saved.py to replace it with real AI output."
        )
    try:
        st.subheader("Website UI")
        render_web_ui(st.session_state["layout"], st.session_state.get("layout_version", 0))
        st.subheader("Report Layout")
        render_report(st.session_state["layout"])
    except Exception as e:  # a strange reply should not break the page
        st.error(f"Could not draw the preview ({e}). Try Apply change or Start over.")

st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)  # space above the button
if st.button(
    "Generate a new proposal" if "proposal" in st.session_state else "Generate Proposal",
    help="Writes a new draft. This replaces the text below, including any edits you made. "
    "You do not need to click it after editing: your edits are saved as you type."
    if "proposal" in st.session_state
    else None,
):
    if "layout" not in st.session_state:
        st.warning("Please click Generate web UI and report layout first - there is no saved layout yet.")
    else:
        with st.spinner("Writing the proposal..."):
            try:
                st.session_state["proposal"] = generate_proposal(
                    company, st.session_state.get("draft_points") or "", st.session_state["layout"]
                )
            except anthropic.APIError as e:
                st.warning(friendly_api_error(e) + " Please try again.")

if "proposal" in st.session_state:
    st.subheader("Proposal")
    # The text box is tied to st.session_state["proposal"], so whatever you type is kept.
    st.text_area(
        "Proposal text",
        key="proposal",
        height=400,
        label_visibility="collapsed",
        help="You can edit this text. Clicking Generate Proposal again replaces it with a new draft. "
        "Keep the [Picture: ...] lines where you want the pictures to appear.",
    )
    st.caption("After editing, press **Ctrl + Enter** (or click outside the box) to update the preview and the Word file below.")

    @st.cache_data(show_spinner=False)
    def proposal_pictures(layout_json: str) -> dict[str, bytes]:
        layout = json.loads(layout_json)
        return {"web": web_ui_png(layout), "report": report_png(layout)}

    pictures = proposal_pictures(json.dumps(st.session_state["layout"], sort_keys=True))
    st.subheader("Proposal preview")
    st.caption("This is how the proposal looks, with the BioHealthy logo and pictures drawn from the current layout.")
    with st.container(border=True):
        st.image(logo_png(), width=220)
        for kind, chunk in split_proposal(st.session_state["proposal"]):
            if kind == "text":
                # keep line breaks, and stop "____" and "$" from being read as Markdown / maths
                st.markdown(chunk.replace("_", "\\_").replace("$", "\\$").replace("\n", "  \n"))
            else:
                st.image(pictures[kind])
    st.download_button(
        "Download Word (.docx)",
        data=build_docx(st.session_state["proposal"], pictures, logo_png()),
        file_name="proposal.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
