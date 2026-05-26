"""Generate roku_remote.ico with a purple remote on a dark purple background."""

from PIL import Image, ImageDraw

SIZE = 256
BG_COLOR = "#2d1f5e"
REMOTE_COLOR = "#7a4fd6"
BTN_COLOR = "#f4f2fb"
BTN_DARK = "#3a2f57"
ACCENT_GREEN = "#2e7d4f"

img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Rounded square background
draw.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=48, fill=BG_COLOR)

# Remote body
rx, ry = 78, 28
rw, rh = SIZE - 78, SIZE - 28
draw.rounded_rectangle([rx, ry, rw, rh], radius=32, fill=REMOTE_COLOR)

# D-pad
cx, cy = SIZE // 2, 82
draw.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=BTN_DARK)
cross_w = 7
draw.rectangle([cx - cross_w, cy - 24, cx + cross_w, cy + 24], fill=BTN_COLOR)
draw.rectangle([cx - 24, cy - cross_w, cx + 24, cy + cross_w], fill=BTN_COLOR)
draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=ACCENT_GREEN)

# Nav buttons
nav_y = 124
for offset in [-24, 0, 24]:
    bx = cx + offset
    draw.ellipse([bx - 6, nav_y - 6, bx + 6, nav_y + 6], fill=BTN_DARK)
    draw.ellipse([bx - 4, nav_y - 4, bx + 4, nav_y + 4], fill=BTN_COLOR)

# Volume -
vol_y = 156
minus_x = cx - 24
draw.rounded_rectangle(
    [minus_x - 14, vol_y - 10, minus_x + 14, vol_y + 10], radius=5, fill=BTN_DARK
)
draw.rectangle([minus_x - 6, vol_y - 2, minus_x + 6, vol_y + 2], fill=BTN_COLOR)

# Volume +
plus_x = cx + 24
draw.rounded_rectangle(
    [plus_x - 14, vol_y - 10, plus_x + 14, vol_y + 10], radius=5, fill=BTN_DARK
)
draw.rectangle([plus_x - 6, vol_y - 2, plus_x + 6, vol_y + 2], fill=BTN_COLOR)
draw.rectangle([plus_x - 2, vol_y - 6, plus_x + 2, vol_y + 6], fill=BTN_COLOR)

# Power button
pw_y = 188
draw.ellipse([cx - 10, pw_y - 10, cx + 10, pw_y + 10], fill="#9b3535")

img.save(
    "roku_remote.ico",
    format="ICO",
    sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
)
print("Generated roku_remote.ico")
