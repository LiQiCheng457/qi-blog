"""Split Qi After Work composite artwork into web-ready PNG layers.

Usage:
    python scripts/split_qi_after_work_assets.py

Edit ``qi_after_work_slices.json`` when an image is regenerated or a crop needs
adjustment. The script never changes the original composite images.
"""
from __future__ import annotations

import json
from collections import deque
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "scripts" / "qi_after_work_slices.json"


def trim_transparency(image: Image.Image, padding: int) -> Image.Image:
    """Remove unused transparent margins while retaining a little breathing room."""
    alpha = image.getchannel("A")
    bounds = alpha.getbbox()
    if not bounds:
        return image
    left, top, right, bottom = bounds
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(image.width, right + padding)
    bottom = min(image.height, bottom + padding)
    return image.crop((left, top, right, bottom))


def remove_checkerboard(image: Image.Image) -> Image.Image:
    """Remove only the edge-connected neutral checkerboard background.

    Furniture itself contains cream-white highlights, so a blanket white-key
    would damage it. Flooding from the crop's outer edge preserves isolated
    light areas inside the furniture while clearing the surrounding board.
    """
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size
    queue = deque()
    visited: set[tuple[int, int]] = set()

    def is_checker_pixel(x: int, y: int) -> bool:
        red, green, blue, _ = pixels[x, y]
        return min(red, green, blue) >= 214 and max(red, green, blue) - min(red, green, blue) <= 18

    for x in range(width):
        queue.extend(((x, 0), (x, height - 1)))
    for y in range(height):
        queue.extend(((0, y), (width - 1, y)))

    while queue:
        x, y = queue.popleft()
        if (x, y) in visited or not is_checker_pixel(x, y):
            continue
        visited.add((x, y))
        red, green, blue, _ = pixels[x, y]
        pixels[x, y] = (red, green, blue, 0)
        for next_x, next_y in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= next_x < width and 0 <= next_y < height:
                queue.append((next_x, next_y))
    return rgba


def process_slice(source: Image.Image, item: dict, output_dir: Path) -> Path:
    left, top, right, bottom = item["box"]
    cropped = source.crop((left, top, right, bottom)).convert("RGBA")
    if item.get("remove_checkerboard", False):
        cropped = remove_checkerboard(cropped)
    if item.get("trim", True):
        cropped = trim_transparency(cropped, item.get("padding", 10))

    target = output_dir / item["output"]
    target.parent.mkdir(parents=True, exist_ok=True)
    cropped.save(target, optimize=True)
    return target


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    written: list[Path] = []
    for sheet in manifest["sheets"]:
        source_path = ROOT / sheet["source"]
        output_dir = ROOT / sheet["output_dir"]
        with Image.open(source_path) as source:
            for item in sheet["slices"]:
                written.append(process_slice(source, item, output_dir))

    print(f"Generated {len(written)} assets:")
    for path in written:
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
