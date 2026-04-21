"""
把 lumina-cafe-v2 / lumina-biscuit-v2 的浅色背景统一替换为站点底色 #F7F5EE。

策略：
- 把原图转为 RGB
- 计算每个像素与"目标纸色"和"原图近白背景色"的距离
- 对接近背景色的像素，按"距离阈值 + 软过渡"线性混合到目标纸色
- 这样既能消除生成图里偏白的色块，又不会破坏人物水彩晕染的边缘

输出：覆盖原文件 + 生成 .jpg 供站点使用。
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

PAPER = (247, 245, 238)  # #F7F5EE 站点底色

# 生成图的"原始背景近白"参考色（在两张图角落取样得到，整体近 #FBF7EF）
SRC_BG = (251, 247, 239)


def soft_replace(src: Path, dst_png: Path, dst_jpg: Path) -> None:
    img = Image.open(src).convert("RGB")
    arr = np.asarray(img, dtype=np.float32)

    # 与原始背景近白色的欧氏距离
    diff = arr - np.array(SRC_BG, dtype=np.float32)
    dist = np.sqrt((diff ** 2).sum(axis=-1))

    # 距离 < lo 的像素：完全替换为 PAPER
    # 距离 > hi 的像素：完全保留原色
    # 中间：线性过渡，避免硬边
    lo, hi = 6.0, 28.0
    blend = np.clip((hi - dist) / (hi - lo), 0.0, 1.0)[..., None]  # H,W,1

    target = np.array(PAPER, dtype=np.float32)
    out = arr * (1 - blend) + target * blend
    out = np.clip(out, 0, 255).astype(np.uint8)

    out_img = Image.fromarray(out, "RGB")
    out_img.save(dst_png, "PNG")
    out_img.save(dst_jpg, "JPEG", quality=88, optimize=True)
    print(f"  -> {dst_png}  ({dst_png.stat().st_size // 1024} KB)")
    print(f"  -> {dst_jpg}  ({dst_jpg.stat().st_size // 1024} KB)")


def main() -> None:
    src_dir = Path("/home/ubuntu/webdev-static-assets")
    out_dir = Path("/home/ubuntu/lumina/docs/assets")
    out_dir.mkdir(parents=True, exist_ok=True)

    pairs = [
        ("lumina-cafe-v2.png", "lumina-cafe.jpg"),
        ("lumina-biscuit-v2.png", "lumina-biscuit.jpg"),
    ]

    for src_name, jpg_name in pairs:
        src = src_dir / src_name
        if not src.exists():
            print(f"!! missing {src}")
            continue
        dst_png = out_dir / src_name  # 留一份高清 PNG 作存档
        dst_jpg = out_dir / jpg_name  # 站点用 jpg
        print(f"[{src_name}]")
        soft_replace(src, dst_png, dst_jpg)


if __name__ == "__main__":
    main()
