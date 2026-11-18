"""Tijorat banklari dollar kurslari jadvali (kanal uslubidagi rasm).

Ishlatish: python rates_image.py rates.json out.png
rates.json: {"updated": "18.11.2026 12:29", "banks": [{"name": "...", "buy": 11965, "sell": 12055}, ...]}
"""
import json
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf"
NAVY = (12, 38, 74)
GREEN = (34, 150, 60)
GRID = (205, 220, 240)
BADGE_COLORS = [(0, 150, 80), (190, 40, 70), (200, 30, 40), (20, 90, 200), (0, 140, 110),
                (40, 60, 160), (0, 130, 60), (150, 110, 40), (180, 120, 60), (20, 60, 130),
                (0, 110, 110), (220, 50, 40), (90, 60, 160), (60, 120, 180)]


def font(size, bold=True):
    return ImageFont.truetype(FONT % ("-Bold" if bold else ""), size)


def fmt(n):
    if not n:
        return "—"
    return f"{n:,}".replace(",", " ")


SHORT = {"agrobank": "AGRO", "anorbank": "ANOR", "asakabank": "ASAKA", "asia alliance bank": "AAB",
         "hamkorbank": "HAMKOR", "infinbank": "INFIN", "ipoteka-bank": "IPOTEKA",
         "orient finans bank": "OFB", "o‘zmilliybank": "NBU", "turonbank": "TURON",
         "xalq bank": "XALQ", "“brb” atb": "BRB",
         "ipak yo‘li bank": "IPAK", "poytaxt bank": "POYTAXT",
         "kapitalbank": "KAPITAL", "aloqabank": "ALOQA"}


def initials(name):
    if name.lower() in SHORT:
        return SHORT[name.lower()]
    words = [w for w in name.replace('"', "").replace("-", " ").split() if w[0].isalpha()]
    return (words[0][0] + (words[1][0] if len(words) > 1 else words[0][1])).upper()


def _background(W, H, HEAD):
    """Jadval ortidagi bezak: gradient, globus, $ belgilari, kurs grafigi."""
    import math
    bg = Image.new("RGBA", (W, H))
    g = ImageDraw.Draw(bg)
    for y in range(HEAD, H):
        t = (y - HEAD) / max(1, H - HEAD)
        g.line([(0, y), (W, y)], fill=(int(228 - 40 * t), int(238 - 28 * t), int(252 - 10 * t), 255))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    o = ImageDraw.Draw(lay)
    # Globus
    cx, cy, R = W * 0.5, HEAD + (H - HEAD) * 0.5, min(W, H - HEAD) * 0.46
    col = (60, 110, 190, 85)
    o.ellipse([cx - R, cy - R, cx + R, cy + R], outline=col, width=4)
    for k in range(1, 6):
        h = R * math.sin(math.pi * k / 6)
        o.ellipse([cx - R, cy - h * 0.18, cx + R, cy + h * 0.18], outline=col, width=2) if k == 3 else None
        yk = cy - R * math.cos(math.pi * k / 6)
        wk = R * math.sin(math.pi * k / 6)
        o.line([(cx - wk, yk), (cx + wk, yk)], fill=col, width=2)
    for k in range(1, 6):
        wk = R * abs(math.cos(math.pi * k / 6))
        o.ellipse([cx - wk, cy - R, cx + wk, cy + R], outline=col, width=2)
    # Kurs grafigi (pastda o'sib boruvchi chiziq va ostidagi soya)
    pts, base = [], H - 40
    for i in range(0, 13):
        x = i * W / 12
        y = base - 60 - i * 14 - 38 * math.sin(i * 1.3) - 20 * math.cos(i * 2.1)
        pts.append((x, y))
    o.polygon(pts + [(W, H), (0, H)], fill=(40, 150, 110, 45))
    o.line(pts, fill=(30, 140, 100, 130), width=5, joint="curve")
    for x, y in pts[1:-1]:
        o.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(30, 140, 100, 110))
    # Shamlar (candlestick) — o'ng yuqori burchakda
    for i in range(9):
        x = W - 300 + i * 30
        mid = HEAD + 230 - i * 12 + (25 if i % 3 == 1 else 0)
        up = i % 3 != 1
        c = (34, 150, 60, 75) if up else (200, 60, 60, 75)
        o.line([(x + 7, mid - 45), (x + 7, mid + 45)], fill=c, width=2)
        o.rectangle([x, mid - 25, x + 14, mid + 25], fill=c)
    # Sochilgan $ belgilari
    spots = [(70, .12, 70), (880, .18, 90), (150, .55, 60), (820, .62, 80), (470, .9, 70),
             (60, .85, 90), (900, .9, 60), (330, .3, 50), (640, .4, 55), (600, .75, 65)]
    for x, fy, sz in spots:
        o.text((x, HEAD + (H - HEAD) * fy), "$", font=font(sz), fill=(60, 110, 180, 55), anchor="mm")
    bg = Image.alpha_composite(bg, lay)
    return bg


def _shade(c, k):
    """Rangni yorqinlashtirish (k>0) yoki to'qlashtirish (k<0)."""
    return tuple(max(0, min(255, int(v + (255 - v) * k if k > 0 else v * (1 + k)))) for v in c[:3])


def _shadow(size, boxes, radius, offset=(0, 8), blur=10, alpha=90):
    """Berilgan to'rtburchaklar uchun xiralashtirilgan soya qatlami."""
    sh = Image.new("RGBA", size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for x0, y0, x1, y1 in boxes:
        sd.rounded_rectangle([x0 + offset[0], y0 + offset[1], x1 + offset[0], y1 + offset[1]],
                             radius, fill=(10, 30, 70, alpha))
    return sh.filter(ImageFilter.GaussianBlur(blur))


def _text3d(d, xy, text, f, color, depth=3, anchor="mm"):
    """Hajmli matn: pastga-o'ngga qatlamli soya + asosiy rang."""
    dark = _shade(color, -0.55) if color != (20, 20, 20) else (150, 165, 190)
    for k in range(depth, 0, -1):
        d.text((xy[0] + k, xy[1] + k), text, font=f, fill=dark, anchor=anchor)
    d.text(xy, text, font=f, fill=color, anchor=anchor)


def _chart(img, series, x0, y0, x1, y1):
    """Kun davomidagi eng yaxshi sotib olish / sotish kurslari grafigi (3D kartochkada)."""
    W, H = img.size
    img = Image.alpha_composite(img, _shadow((W, H), [(x0, y0, x1, y1)], 16, (0, 8), 8, 95))
    face = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(face)
    fd.rounded_rectangle([x0, y0, x1, y1], 16, fill=(246, 249, 255, 245), outline=(255, 255, 255, 255), width=2)
    img = Image.alpha_composite(img, face)
    d = ImageDraw.Draw(img)
    d.text((x0 + 24, y0 + 26), "KUN DAVOMIDA O‘ZGARISH", font=font(20), fill=(25, 45, 90), anchor="lm")
    BUY_C, SELL_C = (22, 140, 60), (30, 90, 200)
    lx = x1 - 24
    for label, c in (("Eng yuqori sotib olish", BUY_C), ("Eng arzon sotish", SELL_C)):
        tw = d.textlength(label, font=font(15, False))
        d.text((lx, y0 + 26), label, font=font(15, False), fill=(40, 50, 70), anchor="rm")
        d.rounded_rectangle([lx - tw - 34, y0 + 20, lx - tw - 10, y0 + 32], 5, fill=c)
        lx -= tw + 54
    px0, px1, py0, py1 = x0 + 90, x1 - 40, y0 + 62, y1 - 46
    vals = [p["best_buy"] for p in series] + [p["best_sell"] for p in series]
    lo, hi = min(vals), max(vals)
    pad = max(10, (hi - lo) * 0.25)
    lo, hi = lo - pad, hi + pad
    Y = lambda v: py1 - (v - lo) / (hi - lo) * (py1 - py0)
    n = len(series)
    X = lambda i: px0 + (px1 - px0) * (i / (n - 1))
    for k in range(5):
        v = lo + (hi - lo) * k / 4
        y = Y(v)
        d.line([(px0, y), (px1, y)], fill=(215, 225, 240), width=1)
        d.text((px0 - 12, y), fmt(int(round(v / 5) * 5)), font=font(14, False), fill=(90, 100, 120), anchor="rm")
    for i, p in enumerate(series):
        d.text((X(i), py1 + 22), p["time"], font=font(15), fill=(60, 70, 95), anchor="mm")
    for key, c in (("best_buy", BUY_C), ("best_sell", SELL_C)):
        pts = [(X(i), Y(p[key])) for i, p in enumerate(series)]
        sh = [(x + 2, y + 4) for x, y in pts]
        d.line(sh, fill=(180, 190, 210), width=6, joint="curve")
        d.line(pts, fill=c, width=5, joint="curve")
        for (x, y), p in zip(pts, series):
            d.ellipse([x - 8, y - 8, x + 8, y + 8], fill="white", outline=c, width=4)
        lx, ly = pts[-1]
        d.text((lx, ly - 22 if key == "best_sell" else ly + 24), fmt(series[-1][key]),
               font=font(17), fill=c, anchor="mm")
    return img


def render(data, out, signature="@bankkursi"):
    banks = data["banks"]
    W, HEAD, TH, ROW, GAP = 950, 140, 54, 96, 12
    prev = {b["name"]: b for b in data.get("prev", [])}
    series = [p for p in data.get("series", []) if p.get("best_buy") and p.get("best_sell")]
    CH = 330 if len(series) >= 2 else 0
    H = HEAD + TH + GAP + ROW * len(banks) + GAP + CH
    img = _background(W, H, HEAD)
    d = ImageDraw.Draw(img)

    # --- Sarlavha: yaltiroq 3D panel ---
    for y in range(HEAD):
        t = y / HEAD
        d.line([(0, y), (W, y)], fill=(int(10 + 25 * t), int(30 + 45 * t), int(70 + 60 * t)))
    gloss = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gloss)
    for y in range(HEAD // 2):
        gd.line([(0, y), (W, y)], fill=(255, 255, 255, int(38 * (1 - y / (HEAD / 2)))))
    for i in range(0, W, 38):
        gd.line([(i, HEAD - 22 - (i * 7 % 60)), (i + 38, HEAD - 22 - ((i + 38) * 7 % 60))],
                fill=(90, 150, 220, 140), width=2)
    img = Image.alpha_composite(img, gloss)
    # sarlavha ostidagi soya chizig'i
    img = Image.alpha_composite(img, _shadow((W, H), [(0, HEAD - 6, W, HEAD)], 0, (0, 6), 6, 120))
    d = ImageDraw.Draw(img)
    for y in range(HEAD - 4, HEAD):
        d.line([(0, y), (W, y)], fill=(212, 175, 55))  # oltin chiziq

    # 3D tanga
    img = Image.alpha_composite(img, _shadow((W, H), [(26, 24, 120, 118)], 47, (4, 6), 6, 140))
    d = ImageDraw.Draw(img)
    for r in range(47, 0, -1):
        t = r / 47
        d.ellipse([73 - r, 70 - r, 73 + r, 70 + r], fill=(int(240 - 70 * t), int(205 - 70 * t), int(90 - 40 * t)))
    d.ellipse([33, 30, 113, 110], outline=(150, 110, 30), width=3)
    _text3d(d, (73, 70), "$", font(56), (255, 248, 220), depth=3)

    lines = ["BANKLARNING VALYUTA AYIRBOSHLASH SHOXOBCHALARIDA",
             "SO‘MGA NISBATAN DOLLAR KURSI",
             "US DOLLAR TO SUM EXCHANGE RATES IN BANK EXCHANGE OFFICES"]
    for i, ln in enumerate(lines):
        size = 17
        while d.textlength(ln, font=font(size)) > 600 and size > 10:
            size -= 1
        d.text((447, 38 + i * 26) , ln, font=font(size), fill=(5, 15, 40), anchor="mm")
        d.text((445, 36 + i * 26), ln, font=font(size), fill="white", anchor="mm")

    # 3D sana qutisi
    img = Image.alpha_composite(img, _shadow((W, H), [(768, 16, 930, 112)], 12, (5, 7), 6, 150))
    d = ImageDraw.Draw(img)
    for y in range(16, 112):
        t = (y - 16) / 96
        d.line([(768, y), (930, y)], fill=(int(255 - 30 * t), int(255 - 25 * t), int(255 - 15 * t)))
    d.rounded_rectangle([768, 16, 930, 112], 12, outline=(160, 170, 190), width=2)
    date, _, time = data["updated"].partition(" ")
    d.text((849, 46), date, font=font(22), fill=(20, 30, 60), anchor="mm")
    _text3d(d, (849, 80), time, font(28), (12, 38, 74), depth=2)

    # --- Ustun sarlavhalari: bo'rtma panel ---
    cols = [0, 236, 546, 750, W]
    y0 = HEAD + 10
    M = 12
    img = Image.alpha_composite(img, _shadow((W, H), [(M, y0, W - M, y0 + TH - 10)], 12, (0, 5), 6, 90))
    d = ImageDraw.Draw(img)
    for y in range(y0, y0 + TH - 10):
        t = (y - y0) / (TH - 10)
        d.line([(M, y), (W - M, y)], fill=(int(250 - 25 * t), int(252 - 20 * t), int(255 - 10 * t)))
    d.rounded_rectangle([M, y0, W - M, y0 + TH - 10], 12, outline=(190, 205, 230), width=1)
    for i, title in enumerate(["BELGI", "BANK NOMI", "SOTIB OLISH", "SOTISH"]):
        d.text(((cols[i] + cols[i + 1]) / 2, y0 + (TH - 10) / 2), title, font=font(16), fill=(25, 45, 90), anchor="mm")

    # --- Qatorlar: suzib turgan kartochkalar ---
    top0 = HEAD + TH + GAP
    cards = [(M, top0 + r * ROW + 6, W - M, top0 + (r + 1) * ROW - 6) for r in range(len(banks))]
    img = Image.alpha_composite(img, _shadow((W, H), cards, 14, (0, 7), 7, 85))
    face = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(face)
    for (x0, y1, x1, y2) in cards:
        fd.rounded_rectangle([x0, y1, x1, y2], 14, fill=(238, 244, 252, 240))
        fd.rounded_rectangle([x0 + 2, y1 + 2, x1 - 2, y1 + (y2 - y1) * 0.48], 12, fill=(255, 255, 255, 250))
        fd.rounded_rectangle([x0, y1, x1, y2], 14, outline=(255, 255, 255, 255), width=2)
        fd.line([(x0 + 14, y2), (x1 - 14, y2)], fill=(150, 170, 205, 200), width=2)
        for x in cols[1:-1]:
            fd.line([(x, y1 + 14), (x, y2 - 14)], fill=(190, 205, 230, 220), width=2)
    img = Image.alpha_composite(img, face)

    # Bo'rtma bank belgilari (soyasi bilan)
    badges = [(cols[0] + 28, (c[1] + c[3]) / 2 - 27, cols[1] - 22, (c[1] + c[3]) / 2 + 27) for c in cards]
    img = Image.alpha_composite(img, _shadow((W, H), badges, 14, (3, 5), 4, 120))
    d = ImageDraw.Draw(img)

    best_buy = max(b["buy"] for b in banks if b.get("buy"))
    best_sell = min(b["sell"] for b in banks if b.get("sell"))
    for r, (b, bx) in enumerate(zip(banks, badges)):
        cy = (cards[r][1] + cards[r][3]) / 2
        c = BADGE_COLORS[r % len(BADGE_COLORS)]
        x0, y1, x1, y2 = bx
        for y in range(int(y1), int(y2)):
            t = (y - y1) / (y2 - y1)
            col = _shade(c, 0.28 * (1 - 2 * t)) if t < 0.5 else _shade(c, -0.25 * (2 * t - 1))
            d.line([(x0 + 1, y), (x1 - 1, y)], fill=col)
        d.rounded_rectangle([x0, y1, x1, y2], 14, outline=_shade(c, -0.35), width=2)
        d.line([(x0 + 14, y1 + 3), (x1 - 14, y1 + 3)], fill=_shade(c, 0.5), width=2)
        label = initials(b["name"])
        size = 30
        while d.textlength(label, font=font(size)) > cols[1] - 76 and size > 14:
            size -= 1
        _text3d(d, ((x0 + x1) / 2, cy), label, font(size), (255, 255, 255), depth=2)
        d.text((cols[1] + 12, cy), b["name"], font=font(25), fill=(15, 25, 50), anchor="lm")
        pb = prev.get(b["name"], {})
        for key, xc, best in (("buy", (cols[2] + cols[3]) / 2, best_buy),
                              ("sell", (cols[3] + cols[4]) / 2, best_sell)):
            v = b.get(key)
            color = GREEN if v == best else (20, 20, 20)
            old = pb.get(key)
            delta = (v - old) if (v and old) else 0
            if delta:
                _text3d(d, (xc, cy - 10), fmt(v), font(30), color, depth=2)
                up = delta > 0
                dc = (22, 140, 60) if up else (205, 45, 45)
                tag = ("▲ +" if up else "▼ −") + fmt(abs(delta))
                tw = d.textlength(tag, font=font(17))
                d.rounded_rectangle([xc - tw / 2 - 8, cy + 13, xc + tw / 2 + 8, cy + 35], 10,
                                    fill=_shade(dc, 0.82), outline=_shade(dc, 0.4))
                d.text((xc, cy + 24), tag, font=font(17), fill=dc, anchor="mm")
            else:
                _text3d(d, (xc, cy), fmt(v), font(32), color, depth=2)

    if CH:
        img = _chart(img, series, M, H - CH + 4, W - M, H - 14)

    # Suv belgisi
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(wm).text((W / 2, top0 + ROW * len(banks) * 0.42), signature,
                             font=font(110), fill=(150, 175, 205, 50), anchor="mm")
    img = Image.alpha_composite(img, wm).convert("RGB")
    img.save(out)
    return out


if __name__ == "__main__":
    render(json.load(open(sys.argv[1], encoding="utf-8")), sys.argv[2])
