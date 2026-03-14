"""Generate PWA icons in Sage & Sand color scheme."""

from pathlib import Path
from PIL import Image, ImageDraw


# Sage & Sand palette
BG_DARK = (26, 32, 25)        # #1A2019 forest green
PAPER = (237, 234, 216)       # #EDEAD8 warm cream
ACCENT = (192, 122, 56)       # #C07A38 warm copper
ACCENT_LIGHT = (212, 144, 64) # #D49040 lighter copper


def _draw_rounded_rect(draw, xy, radius, fill):
    """Draw a rounded rectangle (compatible with older Pillow too)."""
    x0, y0, x1, y1 = xy
    r = radius
    # Corners
    draw.ellipse([x0, y0, x0 + 2*r, y0 + 2*r], fill=fill)
    draw.ellipse([x1 - 2*r, y0, x1, y0 + 2*r], fill=fill)
    draw.ellipse([x0, y1 - 2*r, x0 + 2*r, y1], fill=fill)
    draw.ellipse([x1 - 2*r, y1 - 2*r, x1, y1], fill=fill)
    # Fill center
    draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
    draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)


def generate_icon(size: int, maskable: bool = False) -> Image.Image:
    """Generate a newspaper-style app icon.

    maskable: if True, adds extra padding so content fits in the safe zone
              (inner 80% circle for Android adaptive icons).
    """
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Full background (rounded for regular, square for maskable)
    if maskable:
        draw.rectangle([0, 0, size - 1, size - 1], fill=BG_DARK)
        safe_inset = size * 0.1  # extra inset for maskable safe zone
    else:
        corner_r = size // 5
        _draw_rounded_rect(draw, (0, 0, size - 1, size - 1), corner_r, BG_DARK)
        safe_inset = 0

    # Paper card — cream rectangle
    margin_x = size * 0.22 + safe_inset
    margin_top = size * 0.18 + safe_inset
    margin_bot = size * 0.18 + safe_inset
    paper_r = size // 24

    _draw_rounded_rect(
        draw,
        (margin_x, margin_top, size - margin_x, size - margin_bot),
        paper_r,
        PAPER,
    )

    # Content area bounds (inside the paper card)
    cx0 = margin_x + size * 0.06
    cx1 = size - margin_x - size * 0.06
    cy0 = margin_top + size * 0.06

    # Headline bar — thick copper line
    headline_h = size * 0.045
    _draw_rounded_rect(
        draw,
        (cx0, cy0, cx1, cy0 + headline_h),
        max(2, size // 128),
        ACCENT,
    )

    # Thin separator under headline
    sep_y = cy0 + headline_h + size * 0.025
    draw.rectangle(
        [cx0, sep_y, cx1, sep_y + max(1, size * 0.005)],
        fill=ACCENT_LIGHT,
    )

    # Body text lines — thinner, lighter copper
    body_y = sep_y + size * 0.04
    line_h = size * 0.028
    line_gap = size * 0.035

    for i in range(5):
        y = body_y + i * (line_h + line_gap)
        # Vary line widths for realism
        if i == 4:
            end_x = cx0 + (cx1 - cx0) * 0.55  # short last line
        elif i == 2:
            end_x = cx0 + (cx1 - cx0) * 0.82
        else:
            end_x = cx1

        _draw_rounded_rect(
            draw,
            (cx0, y, end_x, y + line_h),
            max(1, size // 200),
            ACCENT,
        )

    return img


def main():
    icons_dir = Path(__file__).resolve().parent.parent / "static" / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)

    for size in (192, 512):
        # Regular icon (rounded corners, for home screen)
        icon = generate_icon(size, maskable=False)
        icon.save(icons_dir / f"icon-{size}.png")
        print(f"  Created icon-{size}.png")

        # Maskable icon (full bleed, for Android adaptive icons)
        icon_m = generate_icon(size, maskable=True)
        icon_m.save(icons_dir / f"icon-maskable-{size}.png")
        print(f"  Created icon-maskable-{size}.png")


if __name__ == "__main__":
    main()
