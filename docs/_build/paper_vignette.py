"""
Soft-vignette the two scene illustrations into the site's paper color.

We don't repaint the artwork. We just lay a paper-colored overlay
that's 0% opaque in the central area and ramps up to 100% at the
edges, so the picture seems to dissolve into the page.

The radial mask is intentionally generous (large clear center, gentle
falloff) so detail is preserved.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

PAPER = (247, 245, 238)  # site --paper

SRC_DIR = Path("/home/ubuntu/webdev-static-assets")
OUT_DIR = Path("/home/ubuntu/lumina/docs/assets")


def vignette_to_paper(src: Path, dst: Path) -> None:
    img = Image.open(src).convert("RGB")
    w, h = img.size

    # Build a radial alpha mask: 0 in the center clear area, 1 at the edges.
    # Use elliptical normalized distance, soft falloff via smoothstep.
    yy, xx = np.indices((h, w), dtype=np.float32)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    nx = (xx - cx) / cx
    ny = (yy - cy) / cy
    r = np.sqrt(nx * nx + ny * ny)  # 0 at center, ~1 near edges, >1 at corners

    # Clear inside r<inner, fully paper outside r>outer, smooth between.
    inner = 0.55
    outer = 1.05
    t = np.clip((r - inner) / (outer - inner), 0.0, 1.0)
    # smoothstep
    alpha = t * t * (3 - 2 * t)

    # Slight extra vignette on the very corners so the rectangle silhouette dies completely.
    corner = np.maximum(np.abs(nx), np.abs(ny))
    corner_t = np.clip((corner - 0.85) / 0.25, 0.0, 1.0)
    alpha = np.maximum(alpha, corner_t * corner_t * (3 - 2 * corner_t))

    # Composite paper over the image using the alpha mask.
    arr = np.asarray(img, dtype=np.float32)
    paper = np.full_like(arr, PAPER, dtype=np.float32)
    a = alpha[..., None]
    out = arr * (1 - a) + paper * a

    out_img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")

    # A tiny blur on the very outermost ring further softens any seam.
    # Cheap trick: blur the whole thing once and blend the blur in only at the edge.
    blurred = out_img.filter(ImageFilter.GaussianBlur(radius=1.2))
    edge_only = (alpha > 0.05).astype(np.float32)[..., None]
    blended = np.asarray(out_img, dtype=np.float32) * (1 - 0.35 * edge_only) + np.asarray(
        blurred, dtype=np.float32
    ) * (0.35 * edge_only)
    out_img = Image.fromarray(np.clip(blended, 0, 255).astype(np.uint8), "RGB")

    out_img.save(dst, "JPEG", quality=88, optimize=True)
    print(f"  -> {dst}  ({dst.stat().st_size // 1024} KB)")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pairs = [
        ("lumina-cafe.png", "lumina-cafe.jpg"),
        ("lumina-biscuit.png", "lumina-biscuit.jpg"),
    ]
    for src_name, jpg_name in pairs:
        src = SRC_DIR / src_name
        if not src.exists():
            print(f"!! missing {src}")
            continue
        print(f"[{src_name}]")
        vignette_to_paper(src, OUT_DIR / jpg_name)


if __name__ == "__main__":
    main()
