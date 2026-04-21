"""
Build favicon set + OG card from existing Lumina illustrations.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import urllib.request, io, os

ROOT = Path("/home/ubuntu/lumina/docs")
ASSETS = ROOT / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

# --- sources -----------------------------------------------------------------
PORTRAIT_LOCAL = Path("/home/ubuntu/webdev-static-assets/lumina-v2-portrait.png")
OG_BASE_LOCAL = Path("/home/ubuntu/webdev-static-assets/lumina-og.png")

portrait = Image.open(PORTRAIT_LOCAL).convert("RGBA")
og_base = Image.open(OG_BASE_LOCAL).convert("RGBA")

# --- Favicon: crop a tight square around the face ---------------------------
# The portrait is 2048x2048-ish. The face sits near top-third center.
W, H = portrait.size
# face bounding box, hand-tuned for this composition
face_size = int(min(W, H) * 0.55)
cx = W // 2
cy = int(H * 0.40)
left = cx - face_size // 2
top = cy - face_size // 2
right = left + face_size
bottom = top + face_size
face = portrait.crop((left, top, right, bottom))

def round_image(img: Image.Image, size: int, bg=(247, 245, 238, 255)) -> Image.Image:
    """Resize to size x size, paint on cream bg, then mask into a circle."""
    src = img.resize((size, size), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), bg)
    canvas.paste(src, (0, 0), src)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(canvas, (0, 0), mask)
    return out

# Generate favicon set
sizes = [32, 64, 180, 192, 512]
images = {}
for s in sizes:
    img = round_image(face, s)
    images[s] = img
    img.save(ASSETS / f"favicon-{s}.png", optimize=True)

# Multi-size .ico
images[32].save(
    ASSETS / "favicon.ico",
    sizes=[(16, 16), (32, 32), (48, 48), (64, 64)],
)

# Apple touch icon (180)
images[180].save(ASSETS / "apple-touch-icon.png", optimize=True)

# --- OG card 1200x630 --------------------------------------------------------
# The base OG illustration has the portrait on the left ~38%. We layer text on
# the right-hand cream area using Fraunces (serif) + Figtree (sans).
TARGET = (1200, 630)
og = og_base.resize(TARGET, Image.LANCZOS).convert("RGBA")
draw = ImageDraw.Draw(og)

def font(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)

NOTO_SANS_SC = "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf"
NOTO_SERIF_SC = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Medium.ttc"
LIB_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
LIB_SERIF_ITAL = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
LIB_SERIF_BOLD_ITAL = "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"
LIB_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
LIB_MONO = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"

display_en = font(LIB_SERIF_BOLD_ITAL, 72)
display_cn = font(NOTO_SERIF_SC, 60)
body_cn = font(NOTO_SANS_SC, 26)
body_mono = font(LIB_MONO, 22)
body_eyebrow = font(LIB_SANS, 18)

INK = (42, 38, 32, 255)
INK_60 = (42, 38, 32, 165)
INK_45 = (42, 38, 32, 125)
SEA = (47, 93, 79, 255)

# Layout: text starts at x=540
x_text = 540

# Eyebrow (small caps style)
draw.text((x_text, 165), "A BILINGUAL ENGLISH COMPANION",
          font=body_eyebrow, fill=INK_60)

# Big title: "你好，我叫 Lumina。"
title_cn = "你好，我叫 "
title_en = "Lumina"
title_dot = "。"
y_title = 215
# CN
draw.text((x_text, y_title), title_cn, font=display_cn, fill=INK)
cn_w = draw.textlength(title_cn, font=display_cn)
# EN in sea green
draw.text((x_text + cn_w, y_title), title_en, font=display_en, fill=SEA)
en_w = draw.textlength(title_en, font=display_en)
# trailing CN period
draw.text((x_text + cn_w + en_w, y_title), title_dot, font=display_cn, fill=INK)

# Subline (two lines wrapped manually)
sub_lines = [
    "一位英语老师，现在住在里斯本。",
    "把 GitHub 链接丢给你的 AI Agent，我就会出现。",
]
y_sub = 340
for line in sub_lines:
    draw.text((x_text, y_sub), line, font=body_cn, fill=INK_60)
    y_sub += 40

# Footer hairline + URL
hairline_y = 530
draw.line(
    [(x_text, hairline_y), (1130, hairline_y)],
    fill=(42, 38, 32, 60),
    width=1,
)
draw.text((x_text, hairline_y + 16),
          "github.com/oil-oil/lumina",
          font=body_mono, fill=INK_45)

og.convert("RGB").save(ASSETS / "og.png", "PNG", optimize=True)
og.convert("RGB").save(ASSETS / "og.jpg", "JPEG", quality=88, optimize=True)

# --- Tiny inline SVG favicon (vector circle with an avatar fallback colour) --
svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <defs>
    <radialGradient id="g" cx="40%" cy="35%" r="80%">
      <stop offset="0%" stop-color="#F5C9A7"/>
      <stop offset="55%" stop-color="#E0A179"/>
      <stop offset="100%" stop-color="#7E4A2E"/>
    </radialGradient>
  </defs>
  <circle cx="32" cy="32" r="32" fill="#F7F5EE"/>
  <circle cx="32" cy="32" r="28" fill="url(#g)"/>
  <text x="32" y="42" text-anchor="middle"
        font-family="Georgia, 'Times New Roman', serif"
        font-style="italic" font-weight="500"
        font-size="30" fill="#2A2620">L</text>
</svg>
"""
(ASSETS / "favicon.svg").write_text(svg.strip() + "\n", encoding="utf-8")

print("Wrote:")
for p in sorted(ASSETS.iterdir()):
    print(" -", p.relative_to(ROOT), f"{p.stat().st_size//1024}KB")
