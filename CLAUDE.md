# Project: Proposal Builder (demo)

## What this app does
A tool that turns a client brief into (1) a proposed UI layout and
(2) a branded proposal document. Flow: enter brand + draft points ->
Generate UI -> review and edit the layout -> Generate Proposal -> export
a branded Word (.docx) file. A person approves the layout before the
proposal is generated.

## Stack
- Streamlit (frontend)
- Python (logic)
- AI model via API (generation), structured JSON output for the layout
- python-docx for the Word export
- Session state to hold the brand kit and the approved layout

## How to work with me
- Build ONE small step at a time; after each step tell me how to run it.
- After each step, explain in plain English what the code does.
- Keep the AI's layout output as a small, fixed JSON shape.
- Read the API key from a .env file; never hardcode it; keep .env gitignored.

## Data rule
INVENTED DATA ONLY. No real clients, patients, logos or company files

## Hour 1 thin slice ("UI Proposal Builder" demo)
Brand inputs + draft points -> Generate UI (AI returns a JSON layout spec:
sections with title + display_type) -> Generate Proposal (AI writes a short
proposal from that saved spec). Streamlit, Python, Anthropic API.
Rules: invented data only, one step at a time, explain each step.

## Approved layout design (keep for any new test or draft points)
One panel per Generate; at least 1 key test the patient can change with lifestyle (e.g. DunedinPACE),
plus a 2nd only if it is also important (max 2, unless the draft points name more tests); shared JSON shape
(panel{name,icon}, tests[{name,value,unit,reference_range,scale,history,note,status,status_options,abnormal_statuses,recommendation,show_trend}]).
- Website UI: panel header bar + editable form per test (Result text box, Reference range text box if any,
  Status dropdown). Edits write back into st.session_state["layout"].
- Report Layout: header bar with panel icon, per-test card: name, big value + unit, note, recommendation (only if the status
  is abnormal; placeholder "Doctor's recommended follow-up to appear here" if abnormal but none given), normal range, range bar
  with marker (green = normal range, orange = out of range), trend chart. Missing pieces: no history -> faded example trend
  chart (no numbers) unless show_trend=false (user removed it); no range -> no range bar.
- Palette: charcoal #2E2A2B, sand #E9DCC9, blush #F2D6CF, gold #B8915A; font Calibri.
- Never invent numbers: values, ranges and history come from the uploaded report only.

## Proposal (BioHealthy proposes to the client)
- Recommendations show only while a test's status is in abnormal_statuses (Report Layout, drawn pictures and proposal);
  nurses change the status in the Website UI dropdown, so the report follows live.
- Proposal text follows the approved structure: title, "Prepared by BioHealthy for <client>", Doctor- and nurse-facing web page
  (incl. the status label options per test and that nurses key in the data), Patient report layout (incl. abnormal-only
  recommendations). No client sign-off section by default (the user can type one in). The proposal never quotes sample
  result values or summary sentences, only describes the design. Two lines [Picture: Website UI] and [Picture: Report Layout]
  mark where the pictures go.
- Pictures and the invented BioHealthy logo are drawn with Pillow (pictures.py) from the current layout; the proposal preview
  shows them and "Download Word (.docx)" (proposal_doc.py, python-docx) puts the logo in the page header.
- Files: app.py (page + prompts), theme.py (colours), helpers.py, pictures.py, proposal_doc.py.

## Hour 4: safe to share (done)
- Sample buttons (samples.py) fill Client Name + draft points (no API call); samples 1 and 3 also attach an invented vendor
  report PDF from samples/ (made by make_sample_reports.py / make_sample_report_gut.py).
- saved_results.json holds a layout + proposal per sample (key sample_1..3). make_saved.py (run by the user, costs API money)
  overwrites hand-written placeholders with real model output. "Load saved result" loads them with no API call.
- AI failures show a friendly message; after a sample is chosen, a "Load saved result" fallback is offered.
- core.py holds prompts + AI calls (shared with make_saved.py); saved.py reads/writes saved_results.json.
- Password gate (st.secrets["APP_PASSWORD"], never hardcoded), 10 AI calls per session (app.py MAX_GENERATIONS), and a
  visible "invented data only" note. Secrets live in .env and .streamlit/secrets.toml, both git ignored.
- README.md has the run instructions. Do not touch other features when working on hygiene.
