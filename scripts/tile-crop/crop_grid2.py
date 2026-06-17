"""
裁剪第二组 3x3 九宫格图片为 9 张独立 tile 图
源图：frontend/public/tiles/grid2.png
"""
from PIL import Image
import os, sys

SOURCE     = "frontend/public/tiles/grid2.png"
OUTPUT_DIR = "frontend/public/tiles"
OUT_SIZE   = 256

TILES = [
    ("qi-tile-read",   "128",  "阅读"),
    ("qi-tile-snack",  "512",  "吃零食"),
    ("qi-tile-sleep",  "16",   "睡觉"),
    ("qi-tile-yawn",   "8",    "起床伸懒腰"),
    ("qi-tile-music",  "32",   "弹琴"),
    ("qi-tile-garden", "64",   "浇花"),
    ("qi-tile-star",   "256",  "看星星"),
    ("qi-tile-bike",   "4",    "骑车"),
    ("qi-tile-rain",   "2",    "雨天"),
]

GAP   = 6   # 格子间隙 px
INSET = 20  # 每格四边各向内缩 px，去除白边

def crop(source: str, gap: int = GAP, inset: int = INSET):
    img = Image.open(source).convert("RGBA")
    W, H = img.size
    print(f"源图尺寸：{W} x {H}  gap={gap}  inset={inset}")

    cell_w = (W - gap * 2) // 3
    cell_h = (H - gap * 2) // 3
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for idx, (name, tile_val, label) in enumerate(TILES):
        row, col = divmod(idx, 3)
        left   = col * (cell_w + gap) + inset
        top    = row * (cell_h + gap) + inset
        right  = left + cell_w - inset * 2
        bottom = top  + cell_h - inset * 2

        cell = img.crop((left, top, right, bottom))
        cell = cell.resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS)
        path = os.path.join(OUTPUT_DIR, f"{name}.png")
        cell.save(path, "PNG")
        print(f"  [{tile_val:>4}] {label:<12} → {path}")

    print(f"\n完成！9 张 tile 已保存到 {OUTPUT_DIR}/")

if __name__ == "__main__":
    if not os.path.exists(SOURCE):
        print(f"[错误] 找不到 {SOURCE}")
        sys.exit(1)
    crop(SOURCE)
