# Genera favicon + apple-touch-icon: el "15" del lettering (quince.png)
# centrado sobre el degradé rosa perlado de la tarjeta.
from PIL import Image
import math, os

BASE = os.path.join(os.path.dirname(__file__), "..", "assets")

def pearl_bg(size):
    """Degradé radial rosa perlado (mismo espíritu que el body de la tarjeta)."""
    img = Image.new("RGB", (size, size))
    cx, cy = size * 0.5, size * 0.32          # luz arriba-centro, como el body
    maxd = math.hypot(size, size) * 0.62
    c0 = (255, 225, 236)                       # #ffe1ec centro
    c1 = (238, 199, 213)                       # #eec7d5 borde
    px = img.load()
    for y in range(size):
        for x in range(size):
            t = min(1.0, math.hypot(x - cx, y - cy) / maxd)
            px[x, y] = tuple(round(a + (b - a) * t) for a, b in zip(c0, c1))
    return img

quince = Image.open(os.path.join(BASE, "quince.png")).convert("RGBA")
qb = quince.getbbox()
quince = quince.crop(qb)                       # recortar transparencia sobrante

for size, name in [(64, "favicon.png"), (180, "apple-touch-icon.png")]:
    bg = pearl_bg(size)
    # el "15" ocupa ~78% del lado mayor, centrado
    scale = (size * 0.78) / max(quince.size)
    w, h = (max(1, round(d * scale)) for d in quince.size)
    q = quince.resize((w, h), Image.LANCZOS)
    bg.paste(q, ((size - w) // 2, (size - h) // 2), q)
    out = os.path.join(BASE, name)
    bg.save(out)
    print("OK", name, bg.size)
