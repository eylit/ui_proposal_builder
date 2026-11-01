# Web UI and Report Layout Proposal Builder (demo)

Upload a lab test report (PDF) and/or type draft points. The AI proposes a **Website UI** (an editable form for
nurses) and a **Report Layout** (what the patient sees), then writes a **proposal** with pictures and a BioHealthy
logo that you can edit and download as a Word file.

> **Demo uses invented data only. Please don't enter real or confidential information.**

## Run it on your computer
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
echo 'ANTHROPIC_API_KEY=paste-your-key-here' > .env          # git ignores this file
cp .streamlit/secrets.toml.example .streamlit/secrets.toml    # then set APP_PASSWORD in it (also ignored)
streamlit run app.py
```
Sign in with your `APP_PASSWORD`. On Streamlit Cloud, put `APP_PASSWORD` and `ANTHROPIC_API_KEY` in the app's Secrets.

## Try the samples
Three buttons fill in an invented client and brief (samples 1 and 3 also attach an invented vendor report PDF). Clicking
one never calls the AI. Then either:
- **Generate** (live AI), or
- **Load saved result** (ready-made, no AI, free). Run `python make_saved.py` once to replace the
  hand-written placeholders in `saved_results.json` with real AI output (about 6 API calls).

If an AI call fails you get a friendly message and can load the saved result instead.

## Known limits
- Invented data only. Not for real patients or clients.
- 10 AI generations per session (Generate, Apply change, Generate Proposal each count once). Refreshing the page
  starts a new session, so also set a spend limit on your API key.
- One panel per layout; normally 1 to 2 tests (more only if the draft points name them).
- Proposal pictures are simplified drawings, not screenshots. The AI can be wrong: check every number.
- The model name is set at the top of `core.py`. Confirm it is current.

## Stack
Python, Streamlit, Anthropic API (JSON layout from the model), Pillow (pictures), python-docx (Word export).

## Files
`app.py` page · `core.py` prompts and AI calls · `pictures.py` / `proposal_doc.py` pictures and Word file ·
`samples.py`, `saved.py`, `saved_results.json`, `make_saved.py` samples and saved results ·
`make_sample_report*.py` draw the invented sample PDFs.
