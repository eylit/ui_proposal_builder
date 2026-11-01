"""Draw the invented vendor lab report PDF used by sample button 1.

Run once:  python make_sample_reports.py
It copies only the STRUCTURE of a typical vendor report (cover, summary, key test pages, biomarker cards).
The vendor, patient, test names and numbers are all invented. Image-style PDF made with Pillow.
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PAGE_W, PAGE_H, M = 1240, 1754, 90  # A4 at 150 dpi, margin
INK, MUTED, LINE, SOFT = "#222222", "#6B6B6B", "#D9D9D9", "#F3F5F7"
GOOD, WARN = "#3E9B6B", "#C8553D"
ACCENT = "#1B5E7A"
VENDOR = "Meridian Biosciences"

REPORT = {
    "file": "samples/meridian_bioage_report.pdf",
    "title": "Advanced BioAge Report",
    "patient": "Sample Patient A", "age": 38, "sex": "Male", "id": "MB-20931", "chrono": 38.2,
    "collected": "08 Sep 2025", "reported": "12 Sep 2025",
    # Three headline tests (invented names and numbers)
    "clocks": [
        {"name": "Cellular Age Index", "value": "33.6", "unit": "years", "status": "Younger", "good": True,
         "history": [("Dec 2024", 41.0), ("Jun 2025", 35.2), ("Sep 2025", 33.6)]},
        {"name": "Organ Systems Age", "value": "36.9", "unit": "years", "status": "Younger", "good": True,
         "history": [("Dec 2024", 40.1), ("Jun 2025", 38.0), ("Sep 2025", 36.9)]},
        {"name": "Aging Tempo", "value": "0.8", "unit": "years per year", "status": "Slower", "good": True,
         "history": [("Dec 2024", 1.0), ("Jun 2025", 0.9), ("Sep 2025", 0.8)]},
    ],
    "actionable": [
        {"name": "Marker Alpha-7", "status": "High", "value": "84.2%", "pos": 84.2, "scale": (0, 100), "normal": (0, 80),
         "function": "Alpha-7 is a protein linked to cell stress and protein turnover.",
         "recs": ["Stay well hydrated.", "Eat more leafy greens and berries.", "Make time for regular rest."]},
        {"name": "Protein Q12", "status": "High", "value": "81.5%", "pos": 81.5, "scale": (0, 100), "normal": (0, 80),
         "function": "Q12 is a structural protein involved in tissue repair and blood vessel health.",
         "recs": ["Consider an anti-inflammatory diet.", "Stay physically active.", "Keep an eye on your blood pressure."]},
        {"name": "Lipid L-18:2", "status": "Low", "value": "12.7%", "pos": 12.7, "scale": (0, 100), "normal": (20, 100),
         "function": "L-18:2 is a fat molecule that supports cell membranes and brain health.",
         "recs": ["Eat more oily fish, flaxseeds and walnuts.", "Limit alcohol."]},
    ],
    "additional": [
        {"name": "Marker Beta-3", "status": "Normal", "value": "52.0%", "pos": 52.0, "scale": (0, 100), "normal": (0, 80),
         "function": "Beta-3 is a protein that helps carry substances around the body.",
         "recs": ["Keep a balanced diet."]},
        {"name": "Protein R5", "status": "Normal", "value": "34.6%", "pos": 34.6, "scale": (0, 100), "normal": (0, 80),
         "function": "R5 is an enzyme involved in digestion and cell processes.",
         "recs": ["Maintain an active lifestyle."]},
        {"name": "Enzyme S9", "status": "Normal", "value": "71.3%", "pos": 71.3, "scale": (0, 100), "normal": (0, 80),
         "function": "S9 is an enzyme that helps the body clear waste products.",
         "recs": ["Stay hydrated.", "Eat a balanced diet."]},
        {"name": "Marker T2", "status": "Normal", "value": "45.8%", "pos": 45.8, "scale": (0, 100), "normal": (0, 80),
         "function": "T2 is a small molecule linked to energy metabolism.",
         "recs": ["Exercise regularly."]},
    ],
}


def font(size, bold=False):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default(size)


def text(d, x, y, s, size, fill=INK, bold=False, anchor="la"):
    d.text((x, y), str(s), font=font(size, bold), fill=fill, anchor=anchor)


def wrap(s, size, max_w):
    f, lines, line = font(size), [], ""
    for word in str(s).split():
        trial = f"{line} {word}".strip()
        if line and f.getlength(trial) > max_w:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + ([line] if line else [])


def colour(status):
    return GOOD if status in ("Normal", "Younger", "Slower", "Your score < 1") else WARN


def chip(d, x, y, status, size=26):
    w = font(size, True).getlength(status) + 40
    d.rounded_rectangle([x, y, x + w, y + size + 20], radius=(size + 20) // 2, fill=colour(status))
    text(d, x + w / 2, y + (size + 20) / 2, status, size, "white", True, "mm")
    return w


def page(no, heading):
    img = Image.new("RGB", (PAGE_W, PAGE_H), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, PAGE_W, 110], fill=ACCENT)
    text(d, M, 55, VENDOR, 34, "white", True, "lm")
    text(d, PAGE_W - M, 55, heading, 26, "white", False, "rm")
    d.line([M, PAGE_H - 90, PAGE_W - M, PAGE_H - 90], fill=LINE, width=2)
    text(d, M, PAGE_H - 60, f"{REPORT['patient']}   |   Invented sample report for demonstration only", 20, MUTED, False, "lm")
    text(d, PAGE_W - M, PAGE_H - 60, f"Page {no}", 20, MUTED, False, "rm")
    return img, d


def trend(d, history, x, y, w, h, line_colour):
    vals = [v for _, v in history]
    vmin, vmax = min(vals), max(vals)
    pad = (vmax - vmin) * 0.15 or 1
    vmin, vmax = vmin - pad, vmax + pad
    xs = [x + 70 + (w - 140) * i / (len(vals) - 1) for i in range(len(vals))]
    ys = [y + 45 + (h - 115) * (1 - (v - vmin) / (vmax - vmin)) for v in vals]
    for gy in (y + 45, y + 45 + (h - 115) / 2, y + h - 70):
        d.line([x, gy, x + w, gy], fill="#EEEEEE", width=2)
    d.line(list(zip(xs, ys)), fill=line_colour, width=5)
    for i, (label, v) in enumerate(history):
        last = i == len(history) - 1
        d.ellipse([xs[i] - 11, ys[i] - 11, xs[i] + 11, ys[i] + 11], fill=INK if last else "white", outline=INK, width=4)
        text(d, xs[i], ys[i] - 24, f"{v:.1f}", 24, INK, True, "ms")
        text(d, xs[i], y + h - 30, label, 22, MUTED, False, "mm")


def bar(d, lo, hi, n_lo, n_hi, pos, x, y, w, labels=True):
    px = lambda v: x + w * max(0, min(1, (v - lo) / (hi - lo)))
    d.rounded_rectangle([x, y, x + w, y + 22], radius=11, fill="#E4E4E4")
    d.rounded_rectangle([px(n_lo), y, px(n_hi), y + 22], radius=11, fill="#7CC4A0")
    d.polygon([(px(pos) - 12, y - 24), (px(pos) + 12, y - 24), (px(pos), y - 4)], fill=INK)
    if labels:
        text(d, px(n_lo), y + 34, f"{n_lo:g}", 20, MUTED, False, "ma")
        text(d, px(n_hi), y + 34, f"{n_hi:g}", 20, MUTED, False, "ma")


def cover():
    img = Image.new("RGB", (PAGE_W, PAGE_H), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, PAGE_W, 640], fill=ACCENT)
    text(d, M, 130, VENDOR, 64, "white", True)
    text(d, M, 220, "Biological age testing (invented company)", 28, "#DCE9EF")
    d.ellipse([PAGE_W - 520, 250, PAGE_W - 160, 610], outline="white", width=6)
    d.ellipse([PAGE_W - 430, 340, PAGE_W - 250, 520], outline="white", width=6)
    text(d, M, 800, REPORT["title"], 64, INK, True)
    y = 980
    for label, value in [("Patient", REPORT["patient"]), ("Age / Sex", f"{REPORT['age']} / {REPORT['sex']}"),
                         ("Patient ID", REPORT["id"]), ("Collected", REPORT["collected"]), ("Reported", REPORT["reported"])]:
        text(d, M, y, label, 28, MUTED)
        text(d, M + 260, y, value, 28, INK, True)
        y += 56
    text(d, M, PAGE_H - 100, "Invented sample report for demonstration only. Not a real laboratory or patient.", 22, MUTED)
    return img


def summary():
    img, d = page(2, "Aging summary")
    text(d, M, 190, "Aging Summary", 46, INK, True)
    text(d, PAGE_W - M, 205, f"Chronological age: {REPORT['chrono']}", 26, INK, False, "ra")
    y = 290
    for c in REPORT["clocks"]:
        d.rounded_rectangle([M, y, PAGE_W - M, y + 400], radius=24, outline=LINE, width=3)
        text(d, M + 40, y + 36, c["name"], 32, INK, True)
        text(d, M + 40, y + 120, c["value"], 100, INK)
        text(d, M + 40, y + 250, c["unit"], 24, MUTED)
        chip(d, M + 40, y + 300, c["status"], 26)
        trend(d, c["history"], M + 440, y + 30, PAGE_W - 2 * M - 480, 340, ACCENT)
        y += 440
    return img


def detail_cellular():
    c = REPORT["clocks"][0]
    img, d = page(3, "Cellular Age Index")
    text(d, M, 190, c["name"], 46, INK, True)
    text(d, PAGE_W - M, 205, f"Chronological age: {REPORT['chrono']}", 26, INK, False, "ra")
    d.rounded_rectangle([M, 290, 560, 490], radius=24, fill="#25465A")
    text(d, M + 36, 320, c["name"], 26, "white")
    text(d, M + 36, 370, c["value"], 80, "white")
    chip(d, 360, 390, c["status"], 24)
    text(d, M, 560, "17.6%", 76, INK)
    d.rectangle([M - 24, 550, M - 14, 700], fill="#B0489A")
    for i, line in enumerate(wrap("Your Cellular Age Index is lower than 82.4% of people of the same age and sex.", 26, 440)):
        text(d, M, 660 + i * 38, line, 26, INK)
    # simple scatter of invented population points with a marker for "You"
    ox, oy, ow, oh = 680, 300, 470, 420
    d.line([ox, oy + oh, ox + ow, oy + oh], fill=MUTED, width=2)
    d.line([ox, oy, ox, oy + oh], fill=MUTED, width=2)
    rnd = random.Random(7)
    for _ in range(420):
        a = rnd.uniform(20, 90)
        v = a + rnd.gauss(0, 7)
        px, py = ox + (a - 15) / 90 * ow, oy + oh - max(0, min(1, v / 110)) * oh
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill="#9BCBE0")
    yx, yy = ox + (REPORT["chrono"] - 15) / 90 * ow, oy + oh - 33.6 / 110 * oh
    d.ellipse([yx - 12, yy - 12, yx + 12, yy + 12], fill=INK)
    text(d, ox + ow / 2, oy + oh + 40, "Chronological age", 22, MUTED, False, "ma")
    text(d, M, 900, "Results Over Time", 36, INK, True)
    trend(d, c["history"], M, 940, PAGE_W - 2 * M, 420, ACCENT)
    for i, line in enumerate(wrap("The population graph and percentile are based on invented data patterns and are shown "
                                  "for demonstration only.", 20, PAGE_W - 2 * M)):
        text(d, M, PAGE_H - 170 + i * 28, line, 20, MUTED)
    return img


def detail_tempo():
    c = REPORT["clocks"][2]
    img, d = page(4, "Aging Tempo")
    text(d, M, 190, c["name"], 46, INK, True)
    for i, line in enumerate(wrap("Your rate of aging will change based on your lifestyle. "
                                  "Be sure to retest every 3 months to track your progress.", 32, PAGE_W - 2 * M)):
        text(d, M, 290 + i * 46, line, 32, INK)
    d.rounded_rectangle([M, 430, 620, 900], radius=28, fill=SOFT)
    text(d, 355, 560, c["value"], 110, INK, False, "mm")
    bar(d, 0.45, 1.6, 0.45, 1.0, 0.8, M + 50, 650, 480, labels=False)
    text(d, M + 50, 686, "0.45", 20, MUTED)
    text(d, M + 530, 686, "1.6", 20, MUTED, False, "ra")
    chip(d, 200, 740, "Your score < 1", 24)
    for i, line in enumerate(wrap("Each year that passes, your body will biologically age 0.8 years.", 26, 480)):
        text(d, 355, 830 + i * 36, line, 26, INK, False, "ma")
    text(d, 680, 450, "Reference range: < 1", 30, INK, True)
    for i, line in enumerate(wrap("A score below 1 means your body is aging more slowly than one year for each calendar year.",
                                  26, 470)):
        text(d, 680, 510 + i * 38, line, 26, INK)
    text(d, M, 980, "Results Over Time", 36, INK, True)
    trend(d, c["history"], M, 1020, PAGE_W - 2 * M, 420, ACCENT)
    return img


def card(d, b, y, h):
    d.rounded_rectangle([M, y, PAGE_W - M, y + h], radius=22, outline=LINE, width=3)
    text(d, M + 34, y + 30, b["name"], 30, INK, True)
    chip(d, M + 34 + font(30, True).getlength(b["name"]) + 24, y + 22, b["status"], 22)
    d.rounded_rectangle([PAGE_W - M - 170, y + 22, PAGE_W - M - 34, y + 74], radius=26, fill=INK)
    text(d, PAGE_W - M - 102, y + 48, b["value"], 26, "white", True, "mm")
    lo, hi = b["scale"]
    bar(d, lo, hi, b["normal"][0], b["normal"][1], b["pos"], 600, y + 50, 300)
    d.line([M, y + 118, PAGE_W - M, y + 118], fill=LINE, width=2)
    text(d, M + 34, y + 140, "Function", 22, INK, True)
    yy = y + 176
    for line in wrap(b["function"], 22, 420):
        text(d, M + 34, yy, line, 22, MUTED)
        yy += 32
    text(d, 560, y + 140, "Recommendations", 22, INK, True)
    yy = y + 176
    for rec in b["recs"]:
        d.ellipse([560, yy + 10, 570, yy + 20], fill=MUTED)
        for line in wrap(rec, 22, PAGE_W - M - 600):
            text(d, 584, yy, line, 22, INK)
            yy += 32


def biomarker_page(no, heading, items, h, intro=None):
    img, d = page(no, heading)
    text(d, M, 190, heading, 44, INK, True)
    y = 270
    if intro:
        for line in wrap(intro, 22, PAGE_W - 2 * M):
            text(d, M, y, line, 22, MUTED)
            y += 32
        y += 20
    for b in items:
        card(d, b, y, h)
        y += h + 30
    return img


def build():
    return [
        cover(), summary(), detail_cellular(), detail_tempo(),
        biomarker_page(5, "Most Actionable Biomarkers", REPORT["actionable"], 340,
                       "Biomarkers are compared with a reference group of people of the same sex and a similar age. "
                       "They are listed in order of impact on your Cellular Age Index."),
        biomarker_page(6, "Additional Biomarkers", REPORT["additional"], 270),
    ]


if __name__ == "__main__":
    pages = build()
    out = Path(__file__).parent / REPORT["file"]
    out.parent.mkdir(exist_ok=True)
    pages[0].save(out, "PDF", save_all=True, append_images=pages[1:], resolution=150)
    print(f"wrote {out} ({len(pages)} pages, {out.stat().st_size // 1024} KB)")
