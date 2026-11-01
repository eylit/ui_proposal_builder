"""Make the saved results used by the "Load saved result" button. Run this once, on your own computer:

    python make_saved.py          # all three samples
    python make_saved.py 2        # just sample 2

It calls the real AI API (needs ANTHROPIC_API_KEY in .env) twice per sample: one layout and one proposal.
That costs a little money. The results go into saved_results.json, replacing any hand-written placeholders.
"""
import datetime
import os
import sys
from pathlib import Path

import anthropic

import core
from saved import SAVED_PATH, save_entry
from samples import SAMPLES

ROOT = Path(__file__).parent


def make_entry(sample: dict) -> dict:
    """Run the same AI steps as the app for one sample and return the saved entry."""
    attachments = []
    if sample["report"]:
        attachments.append(("application/pdf", (ROOT / sample["report"]).read_bytes()))
    layout = core.generate_layout(sample["company"], sample["brief"], attachments)
    proposal = core.generate_proposal(sample["company"], sample["brief"], layout)
    return {"source": "model", "model": core.MODEL, "made": datetime.date.today().isoformat(),
            "layout": layout, "proposal": proposal}


def main(argv: list[str]) -> int:
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("No ANTHROPIC_API_KEY found. Put your key in the .env file first.")
        return 1
    try:
        wanted = [int(a) - 1 for a in argv] or list(range(len(SAMPLES)))
        samples = [(i, SAMPLES[i]) for i in wanted if 0 <= i < len(SAMPLES)]
    except ValueError:
        print("Usage: python make_saved.py [sample numbers, e.g. 1 3]")
        return 1
    failed = 0
    for i, sample in samples:
        print(f"{sample['name']} ...", end=" ", flush=True)
        try:
            save_entry(i, make_entry(sample))
            print("saved")
        except (anthropic.APIError, ValueError, OSError) as e:  # keep any older entry for this sample
            failed += 1
            print(f"FAILED ({type(e).__name__}: {e})")
    print(f"Done. Results are in {SAVED_PATH.name}." + (f" {failed} failed; run again for those." if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
