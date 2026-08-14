"""Split the transparent Qi After Work UI sprite sheets into named PNG assets."""

from pathlib import Path

from PIL import Image


WORKSPACE = Path(__file__).resolve().parents[1]
SOURCE_DIR = WORKSPACE / "frontend/public/games/qi-after-work/ui"
OUTPUT_DIR = WORKSPACE / "frontend/public/games/qi-after-work/assets/ui"
SHEETS = {
    "Game_UI_1.png": ["energy", "warm-drink", "happy", "rain", "clock"],
    "Game_UI_2.png": ["checklist", "memory-box", "settings", "music", "volume", "sparkles"],
}
ALPHA_THRESHOLD = 8
PADDING = 6


def crop_with_padding(image: Image.Image, start: int, end: int) -> Image.Image:
    alpha = image.getchannel("A")
    bbox = alpha.crop((start, 0, end, image.height)).getbbox()
    if bbox is None:
        raise ValueError("Sprite region has no visible pixels")
    left = max(0, start + bbox[0] - PADDING)
    top = max(0, bbox[1] - PADDING)
    right = min(image.width, start + bbox[2] + PADDING)
    bottom = min(image.height, bbox[3] + PADDING)
    return image.crop((left, top, right, bottom))


def split_sheet(filename: str, names: list[str]) -> None:
    source = SOURCE_DIR / filename
    image = Image.open(source).convert("RGBA")
    column_width = image.width / len(names)

    for index, name in enumerate(names):
        run = (round(index * column_width), round((index + 1) * column_width))
        target = OUTPUT_DIR / f"{name}.png"
        crop_with_padding(image, *run).save(target)
        print(f"{target.relative_to(WORKSPACE)}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for filename, names in SHEETS.items():
        split_sheet(filename, names)


if __name__ == "__main__":
    main()
