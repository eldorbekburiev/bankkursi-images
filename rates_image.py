"""Tijorat banklari dollar kurslari jadvali (kanal uslubidagi rasm).

Ishlatish: python rates_image.py rates.json out.png
rates.json: {"updated": "18.11.2026 12:29", "banks": [{"name": "...", "buy": 11965, "sell": 12055}, ...]}
"""
import json
import sys

from PIL import Image, ImageDraw, ImageFont

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


def render(data, out, signature="@bankkursi"):
    banks = data["banks"]
    W, HEAD, TH, ROW = 950, 130, 46, 94
    H = HEAD + TH + ROW * len(banks)
    img = _background(W, H, HEAD)
    d = ImageDraw.Draw(img)

    # Sarlavha foni
    for y in range(HEAD):
        t = y / HEAD
        d.line([(0, y), (W, y)], fill=(int(10 + 25 * t), int(30 + 45 * t), int(70 + 60 * t)))
    for i in range(0, W, 38):  # yengil grafik chiziqlari
        d.line([(i, HEAD - 20 - (i * 7 % 60)), (i + 38, HEAD - 20 - ((i + 38) * 7 % 60))],
               fill=(60, 120, 190), width=2)
    for i in range(14):  # sarlavhadagi xira shamlar
        x = 130 + i * 45
        h = 8 + (i * 7) % 14
        d.rectangle([x, HEAD - 12 - h, x + 10, HEAD - 12], fill=(40, 85, 150))
    # Dollar belgisi
    d.ellipse([22, 18, 116, 112], fill=(225, 230, 238), outline=(150, 160, 175), width=4)
    d.ellipse([32, 28, 106, 102], fill=(25, 55, 120))
    d.text((69, 65), "$", font=font(52), fill="white", anchor="mm")
    # Matn
    lines = ["BANKLARNING VALYUTA AYIRBOSHLASH SHOXOBCHALARIDA",
             "SO‘MGA NISBATAN DOLLAR KURSI",
             "US DOLLAR TO SUM EXCHANGE RATES IN BANK EXCHANGE OFFICES"]
    for i, ln in enumerate(lines):
        size = 17
        while d.textlength(ln, font=font(size)) > 620 and size > 10:
            size -= 1
        d.text((442, 34 + i * 26), ln, font=font(size), fill="white", anchor="mm")
    # Sana qutisi
    d.rectangle([768, 14, 930, 104], fill="white", outline=(40, 40, 40), width=3)
    date, _, time = data["updated"].partition(" ")
    d.text((849, 44), date, font=font(22), fill=(20, 20, 20), anchor="mm")
    d.text((849, 74), time, font=font(26), fill=(20, 20, 20), anchor="mm")

    # Jadval: yarim shaffof qatorlar (fon ko'rinib turadi)
    cols = [0, 236, 546, 750, W]
    y0 = HEAD
    rows = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rows)
    rd.rectangle([0, y0, W, y0 + TH], fill=(255, 255, 255, 215))
    for r in range(len(banks)):
        top = y0 + TH + r * ROW
        rd.rectangle([0, top, W, top + ROW], fill=(255, 255, 255, 120 if r % 2 == 0 else 70))
    img = Image.alpha_composite(img, rows)
    d = ImageDraw.Draw(img)
    for i, title in enumerate(["BELGI", "BANK NOMI", "SOTIB OLISH", "SOTISH"]):
        d.text(((cols[i] + cols[i + 1]) / 2, y0 + TH / 2), title, font=font(16), fill=(30, 30, 30), anchor="mm")

    best_buy = max(b["buy"] for b in banks if b.get("buy"))
    best_sell = min(b["sell"] for b in banks if b.get("sell"))
    for r, b in enumerate(banks):
        top = y0 + TH + r * ROW
        cy = top + ROW / 2
        c = BADGE_COLORS[r % len(BADGE_COLORS)]
        d.rounded_rectangle([cols[0] + 22, cy - 30, cols[1] - 22, cy + 30], 16, fill=c)
        label = initials(b["name"])
        size = 30
        while d.textlength(label, font=font(size)) > cols[1] - 70 and size > 14:
            size -= 1
        d.text(((cols[0] + cols[1]) / 2, cy), label, font=font(size), fill="white", anchor="mm")
        d.text((cols[1] + 8, cy), b["name"], font=font(25), fill=(15, 15, 15), anchor="lm")
        d.text(((cols[2] + cols[3]) / 2, cy), fmt(b.get("buy")), font=font(32),
               fill=GREEN if b.get("buy") == best_buy else (20, 20, 20), anchor="mm")
        d.text(((cols[3] + cols[4]) / 2, cy), fmt(b.get("sell")), font=font(32),
               fill=GREEN if b.get("sell") == best_sell else (20, 20, 20), anchor="mm")

    # Panjara
    for x in cols[1:-1]:
        d.line([(x, y0), (x, H)], fill=GRID, width=2)
    for r in range(len(banks) + 1):
        y = y0 + TH + r * ROW
        d.line([(0, y), (W, y)], fill=GRID, width=2)

    # Suv belgisi
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(wm).text((W / 2, y0 + TH + ROW * len(banks) * 0.42), signature,
                             font=font(110), fill=(150, 175, 205, 55), anchor="mm")
    img = Image.alpha_composite(img, wm).convert("RGB")
    img.save(out)
    return out


if __name__ == "__main__":
    render(json.load(open(sys.argv[1], encoding="utf-8")), sys.argv[2])
