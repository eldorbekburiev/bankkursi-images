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
         "xalq bank": "XALQ", "“brb” atb": "BRB"}


def initials(name):
    if name.lower() in SHORT:
        return SHORT[name.lower()]
    words = [w for w in name.replace('"', "").replace("-", " ").split() if w[0].isalpha()]
    return (words[0][0] + (words[1][0] if len(words) > 1 else words[0][1])).upper()


def render(data, out, signature="@bankkursi"):
    banks = data["banks"]
    W, HEAD, TH, ROW = 950, 130, 46, 94
    H = HEAD + TH + ROW * len(banks)
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)

    # Sarlavha foni
    for y in range(HEAD):
        t = y / HEAD
        d.line([(0, y), (W, y)], fill=(int(10 + 25 * t), int(30 + 45 * t), int(70 + 60 * t)))
    for i in range(0, W, 38):  # yengil grafik chiziqlari
        d.line([(i, HEAD - 20 - (i * 7 % 60)), (i + 38, HEAD - 20 - ((i + 38) * 7 % 60))],
               fill=(60, 120, 190), width=2)
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

    # Jadval
    cols = [0, 236, 546, 750, W]
    y0 = HEAD
    d.rectangle([0, y0, W, y0 + TH], fill=(242, 245, 250))
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
    img = Image.alpha_composite(img.convert("RGBA"), wm).convert("RGB")
    img.save(out)
    return out


if __name__ == "__main__":
    render(json.load(open(sys.argv[1], encoding="utf-8")), sys.argv[2])
