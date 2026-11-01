"""Pictures for the proposal, drawn with Pillow from the current layout.

Three PNGs: the BioHealthy logo, a picture of the Website UI form and a picture of the Report Layout.
They are simplified drawings of the live preview, in the same palette.
"""
import io
import math

from PIL import Image, ImageDraw, ImageFont

from helpers import is_abnormal, num, recommendation_text
from theme import BLUSH, DARK, GOLD, GREEN, ORANGE, SAND

K = 2  # everything is drawn at 2x so the pictures stay sharp in the Word file
W = 700  # logical width of the two layout pictures


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = ["Carlito-Bold.ttf", "calibrib.ttf", "DejaVuSans-Bold.ttf"] if bold else [
        "Carlito-Regular.ttf", "calibri.ttf", "DejaVuSans.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size * K)
        except OSError:
            continue
    return ImageFont.load_default(size * K)


def _mix(colour: str, amount: float, base: str = "#FFFFFF") -> str:
    """Blend colour toward base (amount 1 = colour only), to fake opacity."""
    c = [int(colour[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(base[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x * amount + y * (1 - amount)):02X}" for x, y in zip(c, b))


def _text(d, x, y, s, size, fill=DARK, bold=False, anchor="la"):
    d.text((x * K, y * K), str(s), font=_font(size, bold), fill=fill, anchor=anchor)


def _width(s, size, bold=False) -> float:
    return _font(size, bold).getlength(str(s)) / K


def _wrap(s, size, max_w, bold=False) -> list[str]:
    lines, line = [], ""
    for word in str(s).split():
        trial = f"{line} {word}".strip()
        if line and _width(trial, size, bold) > max_w:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + ([line] if line else [])


def _rect(d, box, fill=None, outline=None, r=0, width=1):
    # Pillow wants a whole-number width and radius; icon sizes can make them fractional.
    d.rounded_rectangle([v * K for v in box], radius=int(r * K), fill=fill, outline=outline, width=max(1, round(width * K)))


def _line(d, pts, fill, width=2):
    d.line([(x * K, y * K) for x, y in pts], fill=fill, width=int(width * K), joint="curve")


def _dot(d, x, y, r, fill, outline=None, width=2):
    d.ellipse([(x - r) * K, (y - r) * K, (x + r) * K, (y + r) * K], fill=fill, outline=outline, width=int(width * K))


def _png(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _icon(d, name, cx, cy, size, colour):
    """Simple line icon centred on (cx, cy). Names without a drawing fall back to the general icon."""
    s, w = size, max(1.5, size / 14)
    x0, y0 = cx - s / 2, cy - s / 2

    def p(u, v):
        return (x0 + u * s, y0 + v * s)

    if name == "clock":
        _dot(d, cx, cy, s * 0.45, None, colour, w)
        _line(d, [p(.5, .5), p(.5, .25)], colour, w)
        _line(d, [p(.5, .5), p(.68, .6)], colour, w)
    elif name == "heart":
        pts = [(16 * math.sin(t) ** 3, -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)))
               for t in [i * math.pi / 30 for i in range(61)]]
        _line(d, [p(.5 + x / 38, .48 + y / 38) for x, y in pts], colour, w)
    elif name == "blood":
        arc = [p(.5 + .3 * math.cos(math.radians(a)), .64 + .3 * math.sin(math.radians(a))) for a in range(160, 19, -10)]
        _line(d, [p(.5, .06)] + arc + [p(.5, .06)], colour, w)
    elif name == "immune":
        _line(d, [p(.5, .08), p(.88, .22), p(.88, .5), p(.5, .94), p(.12, .5), p(.12, .22), p(.5, .08)], colour, w)
        _line(d, [p(.32, .5), p(.46, .64), p(.68, .38)], colour, w)
    elif name == "dna":
        left = [p(.5 - .28 * math.sin(i / 12 * 2 * math.pi), .05 + .9 * i / 24) for i in range(25)]
        right = [p(.5 + .28 * math.sin(i / 12 * 2 * math.pi), .05 + .9 * i / 24) for i in range(25)]
        _line(d, left, colour, w)
        _line(d, right, colour, w)
        for i in (3, 9, 15, 21):
            _line(d, [left[i], right[i]], colour, w * 0.7)
    else:  # general: a clipboard with a cross
        _rect(d, (x0 + s * .15, y0 + s * .08, x0 + s * .85, y0 + s * .94), outline=colour, r=s * .1, width=w)
        _line(d, [p(.5, .35), p(.5, .75)], colour, w)
        _line(d, [p(.3, .55), p(.7, .55)], colour, w)


def logo_png() -> bytes:
    """Simple invented logo for BioHealthy: a green circle with a white leaf, then the name."""
    w, h = 300, 80
    img = Image.new("RGBA", (w * K, h * K), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    cx, cy, r = 40, 40, 32
    _dot(d, cx, cy, r, GREEN)
    us = [-1 + i / 20 for i in range(41)]  # pointed leaf: y = +-8 * (1 - u^2), tilted up to the right
    pts = [(u * 17, 8 * (1 - u * u)) for u in us] + [(u * 17, -8 * (1 - u * u)) for u in reversed(us)]
    ang = math.radians(-40)
    pts = [(cx + x * math.cos(ang) - y * math.sin(ang), cy + x * math.sin(ang) + y * math.cos(ang)) for x, y in pts]
    d.polygon([(x * K, y * K) for x, y in pts], fill="#FFFFFF")
    a = (cx - 12 * math.cos(ang), cy - 12 * math.sin(ang))
    b = (cx + 12 * math.cos(ang), cy + 12 * math.sin(ang))
    _line(d, [a, b], GREEN, 1.6)
    _text(d, 86, 40, "Bio", 34, GREEN, True, "lm")
    _text(d, 86 + _width("Bio", 34, True), 40, "Healthy", 34, DARK, True, "lm")
    return _png(img)


def web_ui_png(layout: dict) -> bytes:
    """Picture of the Website UI: panel header and an editable form per test."""
    panel = layout.get("panel", {})
    img = Image.new("RGB", (W * K, (120 + 330 * len(layout.get("tests", []))) * K), "#FFFFFF")
    d = ImageDraw.Draw(img)
    _rect(d, (0, 0, W, 46), fill=DARK, r=8)
    _text(d, W / 2, 23, panel.get("name", "Panel"), 20, "#FFFFFF", False, "mm")
    y = 60
    for test in layout.get("tests", []):
        top = y
        y += 16
        _text(d, 20, y, test.get("name", "Test"), 17, DARK, True)
        y += 34
        unit = str(test.get("unit") or "").strip()
        fields = [(f"Result ({unit})" if unit else "Result", str(test.get("value") or ""), False)]
        if test.get("reference_range"):
            fields.append(("Reference range", str(test["reference_range"]), False))
        if test.get("status") or test.get("status_options"):
            fields.append(("Status", str(test.get("status") or ""), True))
        for label, value, dropdown in fields:
            _text(d, 20, y, label, 12, _mix(DARK, .7))
            _rect(d, (20, y + 20, W - 20, y + 54), fill="#FFFFFF", outline="#C9C4BE", r=6)
            _text(d, 32, y + 37, value, 15, DARK, False, "lm")
            if dropdown:
                ax, ay = W - 38, y + 37
                d.polygon([((ax - 6) * K, (ay - 3) * K), ((ax + 6) * K, (ay - 3) * K), (ax * K, (ay + 4) * K)], fill=DARK)
            y += 70
        _rect(d, (0, top, W, y + 6), outline=SAND, r=6)
        y += 20
    return _png(img.crop((0, 0, W * K, (y + 10) * K)))


def _range_bar(d, test, x, y, w):
    """Green normal zone on an orange track with a marker for the result. Returns the height used (0 = no bar)."""
    scale = test.get("scale")
    if not isinstance(scale, dict):
        return 0
    lo, hi, value = num(scale.get("min")), num(scale.get("max")), num(test.get("value"))
    if lo is None or hi is None or hi <= lo or value is None:
        return 0

    def pos(v):
        return x + w * max(0.0, min(1.0, (v - lo) / (hi - lo)))

    n_lo, n_hi = num(scale.get("normal_min")), num(scale.get("normal_max"))
    has_zone = n_lo is not None or n_hi is not None
    _rect(d, (x, y + 14, x + w, y + 28), fill=ORANGE if has_zone else BLUSH, r=7)
    if has_zone:
        a, b = pos(lo if n_lo is None else n_lo), pos(hi if n_hi is None else n_hi)
        if b > a:
            _rect(d, (a, y + 14, b, y + 28), fill=GREEN, r=7)
    mx = pos(value)
    d.polygon([((mx - 6) * K, (y + 2) * K), ((mx + 6) * K, (y + 2) * K), (mx * K, (y + 11) * K)], fill=DARK)
    _text(d, x, y + 32, f"{lo:g}", 11, _mix(DARK, .65))
    _text(d, x + w, y + 32, f"{hi:g}", 11, _mix(DARK, .65), False, "ra")
    return 50


def _trend(d, test, x, y, w, h):
    """Trend chart from history, or a faded example (no numbers) when there is none. Nothing if the user removed it."""
    if test.get("show_trend") is False:
        return
    points = [(str(i.get("label", "")), num(i.get("value"))) for i in test.get("history") or [] if isinstance(i, dict)]
    points = [(label, v) for label, v in points if v is not None]
    sample = not points
    fade = .55 if sample else 1.0
    gold, dark, grid, fill = _mix(GOLD, fade), _mix(DARK, fade), _mix(SAND, fade), "#FFFFFF"
    left, right, top, bottom = 26, 26, 22, 30
    cx0, cx1, cy0, cy1 = x + left, x + w - right, y + top, y + h - bottom
    for gy in (cy0, (cy0 + cy1) / 2, cy1):
        _line(d, [(cx0, gy), (cx1, gy)], grid, 1)
    if sample:
        vals = [1.0, 0.2, 0.7]
        labels = ["Test 1", "Test 2", "Test 3"]
    else:
        vals = [v for _, v in points]
        labels = [label for label, _ in points]
        vmin, vmax = min(vals), max(vals)
        if vmax == vmin:
            vmin, vmax = vmin - 1, vmax + 1
        vals = [(v - vmin) / (vmax - vmin) for v in vals]
    n = len(vals)
    xs = [cx0 + (cx1 - cx0) * (i / (n - 1) if n > 1 else .5) for i in range(n)]
    ys = [cy1 - (cy1 - cy0) * v for v in vals]
    if sample:  # dashed line
        for i in range(n - 1):
            steps = 14
            for s in range(0, steps, 2):
                t0, t1 = s / steps, (s + 1) / steps
                _line(d, [(xs[i] + (xs[i + 1] - xs[i]) * t0, ys[i] + (ys[i + 1] - ys[i]) * t0),
                          (xs[i] + (xs[i + 1] - xs[i]) * t1, ys[i] + (ys[i + 1] - ys[i]) * t1)], gold, 2)
    else:
        _line(d, list(zip(xs, ys)), gold, 2)
    for i in range(n):
        _dot(d, xs[i], ys[i], 5, dark if (i == n - 1 and not sample) else fill, gold, 2)
        if not sample:
            _text(d, xs[i], ys[i] - 8, f"{vals_raw(points, i):g}", 11, dark, True, "ms")
        _text(d, xs[i], y + h - 14, labels[i], 10, _mix(DARK, .65 * fade), False, "mm")
    if sample:
        _text(d, x + w / 2, y + h + 4, "Example trend - your results over time will appear here", 10, _mix(DARK, .55), False, "ma")


def vals_raw(points, i):
    return points[i][1]


def report_png(layout: dict) -> bytes:
    """Picture of the Report Layout: header with icon, then a card per test."""
    panel = layout.get("panel", {})
    tests = layout.get("tests", [])
    img = Image.new("RGB", (W * K, (120 + 380 * len(tests)) * K), "#FFFFFF")
    d = ImageDraw.Draw(img)
    _rect(d, (0, 0, W, 54), fill=DARK, r=8)
    _icon(d, panel.get("icon"), 34, 27, 28, "#FFFFFF")
    _text(d, 58, 27, panel.get("name", "Panel"), 20, "#FFFFFF", True, "lm")
    y = 54
    for test in tests:
        top = y
        lx, lw = 20, 320
        yy = y + 18
        _text(d, lx, yy, test.get("name", "Test"), 16, DARK, True)
        yy += 30
        value = str(test.get("value") or "")
        _text(d, lx, yy, value, 36, DARK)
        unit = str(test.get("unit") or "").strip()
        if unit:
            _text(d, lx + _width(value, 36) + 8, yy + 24, unit, 13, _mix(DARK, .65))
        yy += 54
        for line in _wrap(test.get("note", ""), 13, lw):
            _text(d, lx, yy, line, 13, _mix(DARK, .8))
            yy += 19
        rec = recommendation_text(test) if is_abnormal(test) else ""
        if rec:
            yy += 6
            lines = _wrap(rec, 13, lw - 14)
            d.rectangle([lx * K, yy * K, (lx + 2) * K, (yy + 19 * len(lines)) * K], fill=GOLD)
            for line in lines:
                _text(d, lx + 12, yy, line, 13, DARK)
                yy += 19
        if test.get("reference_range"):
            yy += 12
            _text(d, lx, yy, "Normal range: ", 13, DARK)
            _text(d, lx + _width("Normal range: ", 13), yy, test["reference_range"], 13, DARK, True)
            yy += 20
        yy += _range_bar(d, test, lx + 4, yy + 8, lw - 8)
        _trend(d, test, 360, y + 18, 320, 160)
        y = max(yy + 24, y + 230)
        _rect(d, (0, top, W, y), outline=SAND, r=0)
    return _png(img.crop((0, 0, W * K, (y + 6) * K)))
