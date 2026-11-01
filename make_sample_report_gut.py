"""Draw the invented gut-health vendor report PDF used by sample button 3.

Run once:  python make_sample_report_gut.py
Only the STRUCTURE of a typical gut microbiome report is copied (cover, scores overview with goals, indicator pages,
dietary recommendations, a detailed pathway page, lifestyle page). The vendor, patient, test names, groups and numbers
are all invented. Image-style PDF made with Pillow.
"""
from pathlib import Path

from PIL import Image, ImageDraw

from make_sample_reports import PAGE_H, PAGE_W, M, font, text, wrap

VENDOR = "Fernhill Microbiome Labs"
ACCENT, TINT = "#2F7D6B", "#E6F1EE"
INK, MUTED, LINE = "#222222", "#6B6B6B", "#D9D9D9"
RED, ORANGE, GREEN = "#D9534F", "#F0A04B", "#7FB069"
OUT = "samples/fernhill_gut_report.pdf"

P = {"name": "Sample Patient C", "age": 44, "sex": "Female", "no": "FM-7720-Q1", "received": "14 Oct 2025"}
GUT_AGE, CHRONO = 41, 44
PATHWAYS = [("Mind-Gut Link", 2), ("Defence Balance", 4), ("Energy Balance", 5), ("Nutrient Processing", 10)]
GOALS = [
    ("Support Variety", "Builds overall resilience, digestion and immune balance.", ["Poor Variety Index"],
     ["Eat about 30 different plant foods a week.", "Add fermented foods and prebiotic fibre every day."]),
    ("Support Defence Balance", "Helps the body manage stress on cells and keep inflammation in check.",
     ["Poor Antioxidant Pathway score"],
     ["Eat colourful, antioxidant-rich whole foods.", "Cut back on processed foods and alcohol."]),
    ("Support Mind-Gut Link", "Helps stress response, mood, sleep quality and mental clarity.",
     ["Poor Calm Signal score", "Poor Mood Signal score"],
     ["Eat more fibre and nutrient-dense foods.", "Sleep 7 to 8 hours in a dark, cool room."]),
]
COMPOSITION = [("Group Alpha", "#E07A9B", 0.01, 0.04), ("Group Beta", "#4F5BA6", 0.02, 0.10),
               ("Group Gamma", "#F2E27A", 0.63, 0.26), ("Group Delta", "#8CD3DD", 0.33, 0.60), ("Others", "#F2994A", 0.01, 0.00)]
FOODS = {"Mind-Gut Link": ["Red capsicum", "Flaxseed", "Apple"], "Defence Balance": ["Blueberries", "Spinach", "Pumpkin seeds"],
         "Energy Balance": ["Rolled oats", "Lentils", "Cinnamon"], "Nutrient Processing": ["Kefir", "Wheat bran", "Garlic"]}


def level(score):
    return "POOR" if score <= 4 else "GOOD" if score <= 7 else "GREAT"


def level_colour(label):
    return {"POOR": RED, "LOW": RED, "GOOD": ORANGE, "GREAT": GREEN, "OPTIMUM": GREEN}.get(label, MUTED)


def tri_bar(d, x, y, w, pos_frac, active, labels=("POOR", "GOOD", "GREAT"), colours=(RED, ORANGE, GREEN)):
    seg = (w - 12) / 3
    for i, c in enumerate(colours):
        d.rounded_rectangle([x + i * (seg + 6), y, x + i * (seg + 6) + seg, y + 14], radius=7, fill=c)
        text(d, x + i * (seg + 6) + seg / 2, y + 44, labels[i], 22, c if labels[i] == active else MUTED, labels[i] == active, "mm")
    mx = x + w * pos_frac
    d.polygon([(mx - 16, y - 40), (mx + 16, y - 40), (mx, y - 6)], fill=level_colour(active))


def score_pos(score):
    return (score - 0.5) / 10


def page(no, heading):
    img = Image.new("RGB", (PAGE_W, PAGE_H), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, PAGE_W, 100], fill=ACCENT)
    text(d, M, 50, VENDOR, 32, "white", True, "lm")
    text(d, PAGE_W - M, 50, heading, 24, "white", False, "rm")
    d.line([M, PAGE_H - 90, PAGE_W - M, PAGE_H - 90], fill=LINE, width=2)
    text(d, M, PAGE_H - 60, f"{P['no']}   |   Invented sample report for demonstration only", 20, MUTED, False, "lm")
    text(d, PAGE_W - M, PAGE_H - 60, f"Page {no}", 20, MUTED, False, "rm")
    return img, d


def para(d, x, y, s, size, w, fill=INK, gap=None):
    for line in wrap(s, size, w):
        text(d, x, y, line, size, fill)
        y += gap or int(size * 1.5)
    return y


def cover():
    img = Image.new("RGB", (PAGE_W, PAGE_H), ACCENT)
    d = ImageDraw.Draw(img)
    text(d, M, 120, VENDOR, 52, "white", True)
    text(d, M, 200, "Gut health testing (invented company)", 26, "#D5E9E3")
    for i, r in enumerate((300, 220, 140)):
        d.ellipse([PAGE_W - 330 - r, 560 - r, PAGE_W - 330 + r, 560 + r], outline="#FFFFFF", width=5 if i < 2 else 8)
    text(d, M, 1200, "Gut Wellness Profile", 78, "white", True)
    text(d, M, 1320, "A snapshot of your gut health and what to do next.", 30, "#D5E9E3")
    text(d, M, PAGE_H - 140, f"Prepared for {P['name']}  |  Report {P['no']}  |  Sample received {P['received']}", 24, "#D5E9E3")
    text(d, M, PAGE_H - 100, "Invented sample report for demonstration only. Not a real laboratory or patient.", 22, "#D5E9E3")
    return img


def glance():
    img, d = page(2, "Your gut at a glance")
    text(d, M, 170, "Your Gut at a Glance", 46, ACCENT, True)
    d.rounded_rectangle([M, 260, PAGE_W - M, 450], radius=24, fill="#F3F3F3")
    para(d, M + 40, 290, "Your gut bacteria are shaped by what you eat and how you live. This report shows your unique gut "
         "landscape and gives personal tips to support your mood, defences, energy and digestion.", 28, PAGE_W - 2 * M - 80)
    text(d, M, 520, "A healthy gut supports", 38, ACCENT, True)
    chips = ["Mood and calm", "Strong defences", "Steady energy", "Easy digestion", "Restful sleep", "Regular bowels"]
    for i, c in enumerate(chips):
        x = M + (i % 3) * 360
        y = 590 + (i // 3) * 150
        d.rounded_rectangle([x, y, x + 330, y + 120], radius=20, fill=TINT)
        text(d, x + 165, y + 60, c, 26, INK, False, "mm")
    d.rounded_rectangle([M, 930, PAGE_W - M, 1380], radius=28, fill="#E7E4F2")
    text(d, M + 40, 970, "A note from our CEO", 32, ACCENT, True)
    para(d, M + 40, 1040, "Welcome to Fernhill! We are committed to turning gut science into clear, useful insights. "
         "Retest every 3 to 6 months to see how your gut changes over time. Thank you for trusting us with your health.",
         27, PAGE_W - 2 * M - 80)
    text(d, M + 40, 1290, "Dr Alex Moreno, Chief Executive (invented)", 26, MUTED)
    return img


def overview():
    img, d = page(3, "Scores overview")
    text(d, M, 160, "Your Scores Overview", 46, INK, True)
    # gut age tile
    d.rounded_rectangle([M, 250, 600, 420], radius=22, outline=LINE, width=3)
    text(d, M + 30, 285, "Gut Age Estimate", 28, ACCENT, True)
    d.ellipse([480, 290, 570, 380], fill=TINT)
    text(d, 525, 335, str(GUT_AGE), 44, INK, True, "mm")
    # indicators
    tiles = [("Your Variety Index", "POOR", 0.12, "2/10"), ("Your Group Ratio", "LOW", 0.12, ""), ("Your Harmony Indicator", "GREAT", 0.88, "9/10")]
    for i, (name, lab, pos, shown) in enumerate(tiles):
        x = 640 if i == 0 else M + (i - 1) * 520
        y = 250 if i == 0 else 460
        w = PAGE_W - M - 640 if i == 0 else 500
        h = 170 if i == 0 else 190
        d.rounded_rectangle([x, y, x + w, y + h], radius=22, outline=LINE, width=3)
        text(d, x + 24, y + 24, name, 26, ACCENT, True)
        text(d, x + w - 24, y + 24, shown, 26, level_colour(lab), True, "ra")
        labels = ("LOW", "OPTIMUM", "HIGH") if lab == "LOW" else ("POOR", "GOOD", "GREAT")
        colours = (RED, GREEN, RED) if lab == "LOW" else (RED, ORANGE, GREEN)
        tri_bar(d, x + 24, y + 100, w - 48, pos, lab, labels, colours)
    # pathway tiles
    for i, (name, score) in enumerate(PATHWAYS):
        x = M + i * 262
        lab = level(score)
        d.rounded_rectangle([x, 700, x + 245, 920], radius=18, outline=LINE, width=3)
        d.rounded_rectangle([x, 700, x + 245, 760], radius=18, fill=TINT)
        text(d, x + 122, 730, name, 20, ACCENT, True, "mm")
        text(d, x + 122, 810, str(score), 52, level_colour(lab), True, "mm")
        text(d, x + 122, 880, lab, 24, level_colour(lab), True, "mm")
    text(d, PAGE_W / 2, 1010, "Your Top Gut Goals", 40, INK, True, "mm")
    for i, (title, intro, based, todo) in enumerate(GOALS):
        x = M + i * 354
        d.rounded_rectangle([x, 1060, x + 330, 1630], radius=20, outline=LINE, width=3)
        text(d, x + 165, 1100, title, 24, ACCENT, True, "mm")
        yy = para(d, x + 20, 1140, intro, 20, 290, MUTED, 28)
        d.rounded_rectangle([x + 16, 1280, x + 314, 1370], radius=12, fill="#F3F3F3")
        text(d, x + 28, 1292, "Based on your result", 19, INK, True)
        for j, b in enumerate(based):
            text(d, x + 28, 1324 + j * 26, b, 18, RED)
        d.rounded_rectangle([x + 16, 1385, x + 314, 1615], radius=12, fill="#E7E4F2")
        text(d, x + 28, 1397, "What to do", 19, INK, True)
        yy = 1430
        for item in todo:
            for line in wrap(item, 19, 270):
                text(d, x + 28, yy, "- " + line if line == wrap(item, 19, 270)[0] else "  " + line, 19, INK)
                yy += 26
            yy += 6
    return img


def age_and_scores():
    img, d = page(4, "Gut age and functional scores")
    text(d, M, 170, "Your Gut Age Estimate", 44, ACCENT, True)
    para(d, M, 250, "Your gut age is estimated from the types of bacteria in your gut, which naturally shift as we age. "
         "It can change with recent diet, lifestyle or supplements.", 26, PAGE_W - 2 * M)
    d.rounded_rectangle([M + 60, 440, PAGE_W - M - 60, 470], radius=15, fill="#CFE4DD")
    px = lambda v: M + 60 + (PAGE_W - 2 * M - 120) * (v - 30) / 25
    for v, lab, y in ((GUT_AGE, "Gut age", 380), (CHRONO, "Your age", 500)):
        d.ellipse([px(v) - 40, y - 10, px(v) + 40, y + 70], fill=TINT, outline=ACCENT, width=3)
        text(d, px(v), y + 30, str(v), 36, INK, True, "mm")
        text(d, px(v) - 70, y + 30, lab, 20, MUTED, False, "rm")
    d.rounded_rectangle([M + 150, 620, PAGE_W - M - 150, 690], radius=35, outline=INK, width=2)
    text(d, PAGE_W / 2, 655, f"Your gut is {CHRONO - GUT_AGE} years younger than your actual age.", 28, INK, False, "mm")
    text(d, M, 770, "Your Functional Scores", 44, ACCENT, True)
    text(d, M, 840, "Scores run from 1 to 10 and come from bacteria levels and key functions.", 24, MUTED)
    for i, (name, score) in enumerate(PATHWAYS):
        x = M + (i % 2) * 540
        y = 920 + (i // 2) * 330
        lab = level(score)
        d.rounded_rectangle([x, y, x + 520, y + 300], radius=20, outline=LINE, width=3)
        d.rounded_rectangle([x, y, x + 520, y + 60], radius=20, fill=TINT)
        text(d, x + 260, y + 30, name, 26, ACCENT, True, "mm")
        text(d, x + 40, y + 150, str(score), 72, level_colour(lab), True, "lm")
        tri_bar(d, x + 160, y + 140, 330, score_pos(score), lab)
    return img


def variety_and_composition():
    img, d = page(5, "Variety and composition")
    text(d, M, 170, "Your Variety Index", 44, ACCENT, True)
    para(d, M, 250, "Shows how many different kinds of bacteria live in your gut. A more varied gut is usually more "
         "resilient and better at supporting digestion and defences.", 26, PAGE_W - 2 * M)
    text(d, M, 395, "2", 90, RED, True, "lm")
    text(d, M + 62, 410, "/10", 32, MUTED, False, "lm")
    tri_bar(d, 300, 440, 640, 0.13, "POOR")
    d.rounded_rectangle([M, 560, 590, 770], radius=16, fill="#F3F3F3")
    text(d, M + 24, 580, "POOR", 24, RED, True)
    para(d, M + 24, 620, "Fewer kinds of bacteria are present. The gut may find it harder to recover from stress or diet changes.", 21, 440, INK, 30)
    text(d, 640, 580, "GOOD / GREAT", 24, GREEN, True)
    para(d, 640, 620, "A varied, resilient gut gives a strong base for overall gut health.", 21, 460, INK, 30)
    text(d, M, 880, "Your Gut Composition", 44, ACCENT, True)
    para(d, M, 960, "The main bacteria groups in your gut compared with an average healthy gut.", 24, 560, MUTED, 34)
    for i, (name, col, _, _) in enumerate(COMPOSITION):
        d.rounded_rectangle([M, 1080 + i * 70, M + 34, 1114 + i * 70], radius=6, fill=col)
        text(d, M + 56, 1097 + i * 70, name, 24, INK, True, "lm")
    for k, (label, idx) in enumerate((("Your gut", 2), ("Average gut", 3))):
        x0, top, h = 760 + k * 220, 980, 520
        y = top + h
        for name, col, mine, avg in COMPOSITION:
            frac = (mine, avg)[k]
            if frac <= 0:
                continue
            d.rectangle([x0, y - frac * h, x0 + 150, y], fill=col)
            y -= frac * h
        text(d, x0 + 75, top + h + 36, label, 22, MUTED, False, "mm")
    return img


def ratio_and_harmony():
    img, d = page(6, "Ratio and harmony")
    text(d, M, 170, "Your Group Ratio", 44, ACCENT, True)
    para(d, M, 250, "Compares two major groups of gut bacteria (Group Gamma and Group Delta) that influence how your body "
         "uses energy and handles inflammation.", 26, PAGE_W - 2 * M)
    tri_bar(d, 300, 440, 640, 0.13, "LOW", ("LOW", "OPTIMUM", "HIGH"), (RED, GREEN, RED))
    for i, (head, body) in enumerate((("LOW RATIO", "More Group Delta and less Group Gamma. May mean less energy is taken from food."),
                                       ("OPTIMUM RATIO", "A balanced gut that supports healthy energy use and calm inflammation."),
                                       ("HIGH RATIO", "More Group Gamma and less Group Delta. Linked to changes in fat storage."))):
        x = M + i * 354
        d.rounded_rectangle([x, 560, x + 330, 820], radius=16, fill="#F3F3F3")
        text(d, x + 20, 580, head, 22, ACCENT, True)
        para(d, x + 20, 620, body, 20, 290, INK, 28)
    text(d, M, 940, "Your Harmony Indicator", 44, ACCENT, True)
    para(d, M, 1020, "Compares helpful bacteria with less helpful ones. A harmonious gut supports steady gut function.",
         26, PAGE_W - 2 * M)
    text(d, M, 1135, "9", 90, GREEN, True, "lm")
    text(d, M + 62, 1150, "/10", 32, MUTED, False, "lm")
    tri_bar(d, 300, 1180, 640, 0.88, "GREAT")
    d.rounded_rectangle([700, 1300, PAGE_W - M, 1520], radius=16, fill="#F3F3F3")
    text(d, 724, 1320, "GREAT", 24, GREEN, True)
    para(d, 724, 1360, "Your gut is well balanced, with plenty of helpful bacteria and controlled less helpful ones.", 21, 390, INK, 30)
    return img


def diet():
    img, d = page(7, "Dietary recommendations")
    text(d, M, 170, "Your Dietary Recommendations", 44, ACCENT, True)
    para(d, M, 250, "Foods chosen for your lower-scoring pathways, plus ones that keep strong pathways in good shape.",
         26, PAGE_W - 2 * M)
    for i, (name, score) in enumerate(PATHWAYS):
        y = 370 + i * 300
        lab = level(score)
        d.rounded_rectangle([M, y, PAGE_W - M, y + 270], radius=20, outline=LINE, width=3)
        d.rounded_rectangle([M, y, PAGE_W - M, y + 56], radius=20, fill=TINT)
        text(d, PAGE_W / 2, y + 28, name, 26, ACCENT, True, "mm")
        text(d, M + 60, y + 150, str(score), 64, level_colour(lab), True, "lm")
        text(d, M + 60, y + 220, lab, 22, level_colour(lab), True, "lm")
        for j, food in enumerate(FOODS[name]):
            fx = 400 + j * 260
            d.ellipse([fx, y + 90, fx + 130, y + 220], fill=TINT, outline=ACCENT, width=3)
            text(d, fx + 65, y + 155, food.split()[0][:1], 48, ACCENT, True, "mm")
            text(d, fx + 65, y + 240, food, 21, INK, False, "mm")
    return img


def pathway_detail():
    img, d = page(8, "Mind-Gut Link")
    text(d, M, 170, "Mind-Gut Link: Overview", 44, ACCENT, True)
    para(d, M, 250, "This pathway looks at how your gut talks to your brain, which influences mood, stress response, focus "
         "and thinking.", 26, PAGE_W - 2 * M)
    d.rounded_rectangle([M, 370, PAGE_W - M, 640], radius=24, fill="#F6F6F6")
    text(d, PAGE_W / 2, 410, "Mind-Gut Link - Overall Score", 30, INK, True, "mm")
    text(d, 340, 520, "2", 80, RED, True, "mm")
    text(d, 395, 535, "/10", 34, MUTED, False, "lm")
    tri_bar(d, 480, 500, 560, score_pos(2), "POOR")
    text(d, M, 720, "What is influencing this score", 36, ACCENT, True)
    for i, (name, score, hint) in enumerate((("Calm Signal", 3, "Stress management"), ("Mood Signal", 3, "Mood regulation"))):
        y = 800 + i * 380
        lab = level(score)
        d.line([M, y - 20, PAGE_W - M, y - 20], fill=LINE, width=2)
        text(d, M, y, name, 34, ACCENT, True)
        text(d, M, y + 52, hint, 24, MUTED)
        tri_bar(d, M, y + 170, 400, score_pos(score), lab)
        text(d, 560, y + 4, f"Your {name} score is {lab.lower()}!", 28, INK, True)
        yy = para(d, 580, y + 60, "The bacteria linked to this signal are present in low amounts, which gives a poor score.", 24, 570, INK, 34)
        para(d, 580, yy + 10, "Low levels can make it harder to stay calm, sleep well and manage stress.", 24, 570, INK, 34)
    return img


def lifestyle():
    img, d = page(9, "Lifestyle")
    text(d, M, 170, "Lifestyle Factors That Help Your Gut", 44, ACCENT, True)
    para(d, M, 250, "Your gut responds to how you live as well as what you eat.", 26, PAGE_W - 2 * M)
    boxes = [("Diet", "Aim for about 30 different plant foods a week. Choose whole foods, use less oil and sugar, and limit processed foods."),
             ("Exercise", "About 30 minutes of movement a day, such as walking or cycling, supports helpful bacteria and digestion."),
             ("Stress", "Even 10 minutes of breathing exercises or quiet time can ease stress and support your gut-brain link."),
             ("Sleep", "Aim for 7 to 9 hours of quality sleep so your gut can recover and your defences stay strong.")]
    for i, (head, body) in enumerate(boxes):
        y = 360 + i * 310
        d.rounded_rectangle([M, y, PAGE_W - M, y + 280], radius=22, outline=LINE, width=3)
        text(d, M + 40, y + 36, head, 34, ACCENT, True)
        para(d, M + 40, y + 100, body, 26, PAGE_W - 2 * M - 80, INK, 38)
    return img


def notes():
    img, d = page(10, "Notes")
    text(d, M, 170, "Important Notes", 44, ACCENT, True)
    para(d, M, 260, "This gut test is a non-diagnostic wellness and lifestyle assessment. It does not diagnose, treat or "
         "prevent any condition. Please talk to your doctor before making big changes to your diet or health routine.",
         28, PAGE_W - 2 * M)
    para(d, M, 520, "All names, scores and people in this report are invented for a software demonstration.", 26, PAGE_W - 2 * M, MUTED)
    return img


def build():
    return [cover(), glance(), overview(), age_and_scores(), variety_and_composition(), ratio_and_harmony(),
            diet(), pathway_detail(), lifestyle(), notes()]


if __name__ == "__main__":
    pages = build()
    out = Path(__file__).parent / OUT
    out.parent.mkdir(exist_ok=True)
    pages[0].save(out, "PDF", save_all=True, append_images=pages[1:], resolution=150)
    print(f"wrote {out} ({len(pages)} pages, {out.stat().st_size // 1024} KB)")
