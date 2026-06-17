"""
裁剪 3x3 九宫格图片为 9 张独立 tile 图
源图：frontend/public/tiles/grid1.png
"""
from PIL import Image
import os

SOURCE     = "frontend/public/tiles/grid1.png"
OUTPUT_DIR = "frontend/public/tiles"
OUT_SIZE   = 256

TILES = [
    ("qi-tile-write",  "2",    "随笔"),
    ("qi-tile-code",   "4",    "前端"),
    ("qi-tile-photo",  "16",   "摄影"),
    ("qi-tile-relax",  "8",    "生活"),
    ("qi-tile-bath",   "64",   "摸鱼/泡澡"),
    ("qi-tile-think",  "32",   "折腾"),
    ("qi-tile-cheer",  "256",  "心情"),
    ("qi-tile-trophy", "1024", "精选"),
    ("qi-tile-wind",   "2048", "起风了"),
]

GAP   = 6   # 格子间隙 px
INSET = 20  # 每格四边各向内缩 px，去除白边

def crop_grid(source: str, gap: int = GAP, inset: int = INSET):
    img = Image.open(source).convert("RGBA")
    W, H = img.size
    print(f"源图尺寸：{W}x{H}  gap={gap}  inset={inset}")

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
        print(f"  [{tile_val:>4}] {label:<10} → {path}")

    print(f"\n完成！9 张 tile 已保存到 {OUTPUT_DIR}/")

if __name__ == "__main__":
    if not os.path.exists(SOURCE):
        print(f"找不到源图：{SOURCE}")
    else:
        crop_grid(SOURCE)
