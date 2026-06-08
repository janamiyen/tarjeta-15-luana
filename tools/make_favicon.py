# Genera favicon + apple-touch-icon: un MOÑO glossy candy pink
# sobre el degrade rosa perlado de la tarjeta. Se dibuja en alta
# resolucion (supersampling) y se baja con LANCZOS para bordes suaves.
from PIL import Image, ImageDraw
import math, os

BASE = os.path.join(os.path.dirname(__file__), "..", "assets")
S = 1024  # canvas de trabajo (luego se baja a 64 y 180)

# --- paleta (misma que los botones/body de la tarjeta) ---
PEARL_C0 = (255, 225, 236)   # #ffe1ec centro
PEARL_C1 = (238, 199, 213)   # #eec7d5 borde
LOOP_TOP = (255, 156, 198)   # #ff9cc6
LOOP_BOT = (232, 93, 152)    # #e85d98
KNOT_TOP = (240, 107, 162)   # #f06ba2
KNOT_BOT = (208, 74, 130)    # mas oscuro para el nudo
EDGE     = (198, 70, 116, 255)


def pearl_bg(size):
    """Degrade radial rosa perlado (mismo espiritu que el body)."""
    img = Image.new("RGB", (size, size))
    cx, cy = size * 0.5, size * 0.32
    maxd = math.hypot(size, size) * 0.62
    px = img.load()
    for y in range(size):
        for x in range(size):
            t = min(1.0, math.hypot(x - cx, y - cy) / maxd)
            px[x, y] = tuple(round(a + (b - a) * t) for a, b in zip(PEARL_C0, PEARL_C1))
    return img


def vgrad(w, h, top, bot):
    """Gradiente vertical RGBA (top -> bot)."""
    g = Image.new("RGBA", (w, h))
    px = g.load()
    for y in range(h):
        t = y / max(1, h - 1)
        c = tuple(round(a + (b - a) * t) for a, b in zip(top, bot)) + (255,)
        for x in range(w):
            px[x, y] = c
    return g


def loop(diam_w, diam_h, angle, top, bot):
    """Una oreja del mono: elipse con gradiente + borde, rotada."""
    pad = int(max(diam_w, diam_h) * 0.9)
    W = H = pad * 2
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    box = [pad - diam_w // 2, pad - diam_h // 2, pad + diam_w // 2, pad + diam_h // 2]
    md.ellipse(box, fill=255)
    grad = vgrad(W, H, top, bot)
    layer.paste(grad, (0, 0), mask)
    # borde
    d = ImageDraw.Draw(layer)
    d.ellipse(box, outline=EDGE, width=int(S * 0.012))
    # brillo glossy arriba
    hl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hl)
    hb = [box[0] + diam_w * 0.16, box[1] + diam_h * 0.12,
          box[2] - diam_w * 0.16, box[1] + diam_h * 0.5]
    hd.ellipse(hb, fill=(255, 255, 255, 90))
    layer = Image.alpha_composite(layer, hl)
    return layer.rotate(angle, resample=Image.BICUBIC, expand=False)


def draw_bow(size):
    bg = pearl_bg(size).convert("RGBA")
    cx, cy = size // 2, int(size * 0.46)

    lw, lh = int(size * 0.42), int(size * 0.34)

    left = loop(lw, lh, -26, LOOP_TOP, LOOP_BOT)
    right = loop(lw, lh, 26, LOOP_TOP, LOOP_BOT)
    # las orejas salen hacia los costados desde el centro
    off = int(size * 0.19)
    bg.alpha_composite(left, (cx - off - left.width // 2, cy - left.height // 2))
    bg.alpha_composite(right, (cx + off - right.width // 2, cy - right.height // 2))

    # --- colas (cintas que cuelgan con muesca en V) ---
    tails = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    td = ImageDraw.Draw(tails)
    ty = int(cy + size * 0.02)
    Lt = [(cx - size * 0.03, ty), (cx - size * 0.04, ty),
          (cx - size * 0.20, size * 0.84),   # esquina inferior izq
          (cx - size * 0.135, size * 0.78),  # vertice de la muesca (sube)
          (cx - size * 0.075, size * 0.86)]  # esquina inferior der
    Rt = [(p[0] + (cx - p[0]) * 2, p[1]) for p in Lt]  # espejo en x=cx
    for poly in (Lt, Rt):
        td.polygon(poly, fill=KNOT_TOP)
        td.line(poly + [poly[0]], fill=EDGE, width=int(S * 0.01))
    bg.alpha_composite(tails)

    # --- nudo central ---
    knot = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    kd = ImageDraw.Draw(knot)
    kw, kh = int(size * 0.135), int(size * 0.20)
    kbox = [cx - kw // 2, cy - kh // 2, cx + kw // 2, cy + kh // 2]
    r = int(kw * 0.45)
    grad = vgrad(size, size, KNOT_TOP, KNOT_BOT)
    kmask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(kmask).rounded_rectangle(kbox, radius=r, fill=255)
    knot.paste(grad, (0, 0), kmask)
    kd.rounded_rectangle(kbox, radius=r, outline=EDGE, width=int(S * 0.012))
    bg.alpha_composite(knot)

    # destello/sparkle arriba a la derecha del mono
    sd = ImageDraw.Draw(bg)
    spx, spy, sr = int(size * 0.74), int(size * 0.30), int(size * 0.02)
    sd.ellipse([spx - sr, spy - sr, spx + sr, spy + sr], fill=(255, 255, 255, 230))
    return bg


big = draw_bow(S)
for size, name in [(64, "favicon.png"), (180, "apple-touch-icon.png")]:
    out = os.path.join(BASE, name)
    big.resize((size, size), Image.LANCZOS).convert("RGB").save(out)
    print("OK", name)

# preview grande para revisar a ojo
big.resize((320, 320), Image.LANCZOS).convert("RGB").save(os.path.join(BASE, "_preview_favicon.png"))
print("OK preview")
