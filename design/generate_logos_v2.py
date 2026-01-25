"""
Tech Digest Daily Logo Generator V2
Generate 10 additional logo concepts
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

os.makedirs("D:/MyIdea/github-trending-daily/design/logos", exist_ok=True)

def get_font(size, bold=False):
    """Get system font with fallback"""
    fonts_to_try = [
        "C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for font_path in fonts_to_try:
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
    return ImageFont.load_default()


def draw_rounded_rect(draw, xy, radius, fill):
    """Draw a rounded rectangle"""
    x1, y1, x2, y2 = xy
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    draw.pieslice([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=fill)
    draw.pieslice([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=fill)
    draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=fill)


# ============================================================
# LOGO 5: Geometric Abstract Style
# ============================================================
def create_geometric_logo():
    """Geometric abstract style"""
    width, height = 800, 400
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = 180, 200

    # Overlapping geometric shapes representing data convergence
    colors = [
        (255, 99, 71, 180),   # Tomato
        (30, 144, 255, 180),  # Dodger blue
        (50, 205, 50, 180),   # Lime green
        (255, 215, 0, 180),   # Gold
    ]

    # Four overlapping circles
    positions = [
        (cx - 40, cy - 40),
        (cx + 20, cy - 40),
        (cx - 40, cy + 20),
        (cx + 20, cy + 20),
    ]

    for (px, py), color in zip(positions, colors):
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.ellipse([px - 50, py - 50, px + 50, py + 50], fill=color)
        img = Image.alpha_composite(img, overlay)

    draw = ImageDraw.Draw(img)

    # Central "T" or "D" letter
    draw.ellipse([cx - 25, cy - 25, cx + 25, cy + 25], fill=(255, 255, 255))
    title_font = get_font(32, bold=True)
    draw.text((cx - 12, cy - 18), "TD", fill=(50, 50, 50), font=title_font)

    # Text
    title_font = get_font(48, bold=True)
    sub_font = get_font(16)

    draw.text((340, 140), "Tech Digest", fill=(50, 50, 50), font=title_font)
    draw.text((340, 200), "Daily", fill=(30, 144, 255), font=title_font)
    draw.text((340, 270), "Where information converges", fill=(128, 128, 128), font=sub_font)

    img.save("D:/MyIdea/github-trending-daily/design/logos/logo_5_geometric.png", "PNG")
    print("Logo 5 (Geometric) created!")


# ============================================================
# LOGO 6: Line Art Style
# ============================================================
def create_lineart_logo():
    """Elegant line art style"""
    width, height = 800, 400
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = 180, 200
    line_color = (45, 55, 72)

    # Hexagon outline
    hex_points = []
    for i in range(6):
        angle = i * math.pi / 3 - math.pi / 6
        hex_points.append((
            cx + 80 * math.cos(angle),
            cy + 80 * math.sin(angle)
        ))

    draw.polygon(hex_points, outline=line_color, width=3)

    # Inner connecting lines
    for i in range(6):
        draw.line([hex_points[i], (cx, cy)], fill=line_color, width=2)

    # Central circle
    draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], outline=line_color, width=3)

    # Data dots on hexagon vertices
    for point in hex_points:
        draw.ellipse([point[0] - 8, point[1] - 8, point[0] + 8, point[1] + 8], fill=line_color)

    # Pulse lines emanating outward
    for i in range(0, 6, 2):
        angle = i * math.pi / 3 - math.pi / 6
        for offset in [100, 115, 130]:
            x = cx + offset * math.cos(angle)
            y = cy + offset * math.sin(angle)
            draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=line_color)

    # Text
    title_font = get_font(44, bold=True)
    sub_font = get_font(14)

    draw.text((320, 145), "TECH DIGEST", fill=line_color, font=title_font)
    draw.text((320, 205), "DAILY", fill=(100, 100, 100), font=title_font)
    draw.text((320, 280), "Precision • Clarity • Insight", fill=(150, 150, 150), font=sub_font)

    img.save("D:/MyIdea/github-trending-daily/design/logos/logo_6_lineart.png", "PNG")
    print("Logo 6 (Line Art) created!")


# ============================================================
# LOGO 7: 3D Isometric Style
# ============================================================
def create_isometric_logo():
    """3D isometric cube style"""
    width, height = 800, 400
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = 180, 200

    # Isometric cube faces
    # Top face
    top_points = [
        (cx, cy - 70),
        (cx + 60, cy - 35),
        (cx, cy),
        (cx - 60, cy - 35),
    ]
    draw.polygon(top_points, fill=(102, 126, 234))

    # Left face
    left_points = [
        (cx - 60, cy - 35),
        (cx, cy),
        (cx, cy + 70),
        (cx - 60, cy + 35),
    ]
    draw.polygon(left_points, fill=(76, 94, 175))

    # Right face
    right_points = [
        (cx, cy),
        (cx + 60, cy - 35),
        (cx + 60, cy + 35),
        (cx, cy + 70),
    ]
    draw.polygon(right_points, fill=(118, 75, 162))

    # Stacked smaller cubes on top
    small_offset = 25
    for dx, dy in [(-25, -45), (25, -45), (0, -80)]:
        size = 20
        scx, scy = cx + dx, cy + dy

        # Mini top
        mini_top = [
            (scx, scy - size),
            (scx + size * 0.8, scy - size * 0.5),
            (scx, scy),
            (scx - size * 0.8, scy - size * 0.5),
        ]
        draw.polygon(mini_top, fill=(255, 159, 67))

        # Mini left
        mini_left = [
            (scx - size * 0.8, scy - size * 0.5),
            (scx, scy),
            (scx, scy + size * 0.5),
            (scx - size * 0.8, scy),
        ]
        draw.polygon(mini_left, fill=(230, 126, 34))

        # Mini right
        mini_right = [
            (scx, scy),
            (scx + size * 0.8, scy - size * 0.5),
            (scx + size * 0.8, scy),
            (scx, scy + size * 0.5),
        ]
        draw.polygon(mini_right, fill=(211, 84, 0))

    # Text
    title_font = get_font(48, bold=True)
    sub_font = get_font(16)

    draw.text((330, 130), "Tech Digest", fill=(50, 50, 50), font=title_font)
    draw.text((330, 195), "Daily", fill=(102, 126, 234), font=title_font)
    draw.text((330, 270), "Building knowledge, block by block", fill=(128, 128, 128), font=sub_font)

    img.save("D:/MyIdea/github-trending-daily/design/logos/logo_7_isometric.png", "PNG")
    print("Logo 7 (Isometric) created!")


# ============================================================
# LOGO 8: Vintage Badge Style
# ============================================================
def create_badge_logo():
    """Vintage badge/emblem style"""
    width, height = 800, 400
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = 200, 200

    # Outer circle
    draw.ellipse([cx - 110, cy - 110, cx + 110, cy + 110], fill=(36, 41, 46))

    # Inner circle
    draw.ellipse([cx - 95, cy - 95, cx + 95, cy + 95], fill=(45, 55, 72))

    # Badge ring
    draw.ellipse([cx - 85, cy - 85, cx + 85, cy + 85], outline=(255, 215, 0), width=4)

    # Inner decorative circle
    draw.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], fill=(36, 41, 46))

    # Center icon - stylized "TD"
    title_font = get_font(50, bold=True)
    draw.text((cx - 35, cy - 30), "TD", fill=(255, 215, 0), font=title_font)

    # Est. year
    small_font = get_font(12)
    draw.text((cx - 25, cy + 30), "EST. 2025", fill=(200, 200, 200), font=small_font)

    # Circular text simulation with dots
    for i in range(12):
        angle = i * math.pi / 6 - math.pi / 2
        x = cx + 78 * math.cos(angle)
        y = cy + 78 * math.sin(angle)
        draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(255, 215, 0))

    # Text
    title_font = get_font(44, bold=True)
    sub_font = get_font(14)

    draw.text((350, 130), "TECH DIGEST", fill=(36, 41, 46), font=title_font)
    draw.text((350, 190), "DAILY", fill=(255, 159, 67), font=title_font)
    draw.text((350, 260), "★ Premium Tech Curation ★", fill=(128, 128, 128), font=sub_font)

    img.save("D:/MyIdea/github-trending-daily/design/logos/logo_8_badge.png", "PNG")
    print("Logo 8 (Badge) created!")


# ============================================================
# LOGO 9: Neon Glow Style
# ============================================================
def create_neon_logo():
    """Neon glow cyberpunk style"""
    width, height = 800, 400
    img = Image.new('RGBA', (width, height), (15, 15, 35, 255))
    draw = ImageDraw.Draw(img)

    cx, cy = 180, 200

    # Glow effect - multiple layers
    neon_pink = (255, 0, 128)
    neon_cyan = (0, 255, 255)

    # Outer glow layers
    for r, alpha in [(70, 30), (65, 50), (60, 80), (55, 120)]:
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        glow_color = (255, 0, 128, alpha)
        overlay_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=glow_color)
        img = Image.alpha_composite(img, overlay)

    draw = ImageDraw.Draw(img)

    # Main shape outline
    draw.ellipse([cx - 50, cy - 50, cx + 50, cy + 50], outline=neon_pink, width=4)

    # Inner lightning bolt / signal icon
    bolt_points = [
        (cx - 15, cy - 30),
        (cx + 5, cy - 5),
        (cx - 5, cy - 5),
        (cx + 15, cy + 30),
        (cx - 5, cy + 5),
        (cx + 5, cy + 5),
    ]
    draw.polygon(bolt_points, fill=neon_cyan)

    # Scanning lines
    for y_offset in [-80, -60, 60, 80]:
        draw.line([(cx - 100, cy + y_offset), (cx + 100, cy + y_offset)],
                  fill=(0, 255, 255, 50), width=1)

    # Text with glow effect
    title_font = get_font(52, bold=True)
    sub_font = get_font(14)

    # Glow behind text
    for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
        draw.text((318 + offset[0], 128 + offset[1]), "TECH", fill=(255, 0, 128, 100), font=title_font)
        draw.text((318 + offset[0], 188 + offset[1]), "DIGEST", fill=(0, 255, 255, 100), font=title_font)

    draw.text((320, 130), "TECH", fill=neon_pink, font=title_font)
    draw.text((320, 190), "DIGEST", fill=neon_cyan, font=title_font)
    draw.text((320, 270), "/ / / DAILY FEED / / /", fill=(150, 150, 150), font=sub_font)

    img.save("D:/MyIdea/github-trending-daily/design/logos/logo_9_neon.png", "PNG")
    print("Logo 9 (Neon) created!")


# ============================================================
# LOGO 10: Pixel Art Style
# ============================================================
def create_pixel_logo():
    """Retro pixel art style"""
    width, height = 800, 400
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = 180, 200
    pixel = 12

    # Pixel newspaper/document icon
    colors = {
        'bg': (45, 55, 72),
        'paper': (255, 255, 255),
        'text': (100, 100, 100),
        'accent': (255, 99, 71),
        'highlight': (102, 126, 234),
    }

    # Paper background (pixel grid)
    paper_grid = [
        "  ########  ",
        " ########## ",
        "############",
        "############",
        "############",
        "############",
        "############",
        "############",
        "############",
        " ########## ",
        "  ########  ",
    ]

    start_x = cx - len(paper_grid[0]) * pixel // 2
    start_y = cy - len(paper_grid) * pixel // 2

    for row_idx, row in enumerate(paper_grid):
        for col_idx, char in enumerate(row):
            if char == '#':
                x = start_x + col_idx * pixel
                y = start_y + row_idx * pixel
                draw.rectangle([x, y, x + pixel - 2, y + pixel - 2], fill=colors['paper'])

    # Content lines on paper
    content_grid = [
        "  ######  ",
        "          ",
        " ######## ",
        " ######## ",
        "          ",
        " ####     ",
        " ######## ",
        " ######   ",
    ]

    content_start_y = start_y + pixel * 2
    for row_idx, row in enumerate(content_grid):
        for col_idx, char in enumerate(row):
            if char == '#':
                x = start_x + col_idx * pixel + pixel
                y = content_start_y + row_idx * pixel
                color = colors['accent'] if row_idx == 0 else colors['text']
                draw.rectangle([x, y, x + pixel - 3, y + pixel - 4], fill=color)

    # Pixel sparkle (AI indicator)
    sparkle_pos = [(cx + 50, cy - 60), (cx - 70, cy - 50), (cx + 70, cy + 40)]
    for sx, sy in sparkle_pos:
        draw.rectangle([sx, sy, sx + pixel - 2, sy + pixel - 2], fill=colors['highlight'])

    # Text
    title_font = get_font(48, bold=True)
    sub_font = get_font(16)

    draw.text((330, 130), "Tech Digest", fill=colors['bg'], font=title_font)
    draw.text((330, 195), "Daily", fill=colors['accent'], font=title_font)
    draw.text((330, 270), "8-bit news for modern devs", fill=(128, 128, 128), font=sub_font)

    img.save("D:/MyIdea/github-trending-daily/design/logos/logo_10_pixel.png", "PNG")
    print("Logo 10 (Pixel) created!")


# ============================================================
# LOGO 11: Space/Cosmic Style
# ============================================================
def create_space_logo():
    """Space and cosmic style"""
    width, height = 800, 400
    img = Image.new('RGBA', (width, height), (10, 10, 30, 255))
    draw = ImageDraw.Draw(img)

    cx, cy = 180, 200

    # Stars background
    import random
    random.seed(42)
    for _ in range(50):
        x = random.randint(40, 320)
        y = random.randint(40, 360)
        size = random.randint(1, 3)
        brightness = random.randint(100, 255)
        draw.ellipse([x, y, x + size, y + size], fill=(brightness, brightness, brightness))

    # Planet/orbit ring
    draw.ellipse([cx - 90, cy - 30, cx + 90, cy + 30], outline=(100, 100, 150), width=2)

    # Central planet
    for r in range(60, 0, -1):
        ratio = r / 60
        color = (
            int(102 + (200 - 102) * (1 - ratio)),
            int(126 + (100 - 126) * (1 - ratio)),
            int(234 + (180 - 234) * (1 - ratio)),
        )
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    # Orbiting satellites (data sources)
    satellites = [
        (cx - 85, cy, (255, 102, 0)),     # HN orange
        (cx + 85, cy, (218, 85, 47)),     # PH red
        (cx, cy - 50, (36, 41, 46)),      # GitHub dark
        (cx, cy + 50, (59, 73, 223)),     # Dev.to blue
    ]

    for sx, sy, color in satellites:
        draw.ellipse([sx - 10, sy - 10, sx + 10, sy + 10], fill=color)
        draw.ellipse([sx - 6, sy - 6, sx + 6, sy + 6], fill=(255, 255, 255, 180))

    # Text
    title_font = get_font(48, bold=True)
    sub_font = get_font(14)

    draw.text((330, 130), "Tech Digest", fill=(220, 220, 255), font=title_font)
    draw.text((330, 195), "Daily", fill=(180, 160, 255), font=title_font)
    draw.text((330, 270), "Explore the tech universe", fill=(150, 150, 180), font=sub_font)

    img.save("D:/MyIdea/github-trending-daily/design/logos/logo_11_space.png", "PNG")
    print("Logo 11 (Space) created!")


# ============================================================
# LOGO 12: Minimalist Letter Style
# ============================================================
def create_letter_logo():
    """Ultra minimalist letter style"""
    width, height = 800, 400
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = 180, 200

    # Single bold letter with accent
    letter_font = get_font(140, bold=True)
    draw.text((cx - 50, cy - 80), "T", fill=(45, 55, 72), font=letter_font)

    # Accent dot
    draw.ellipse([cx + 50, cy - 60, cx + 80, cy - 30], fill=(255, 99, 71))

    # Underline
    draw.rectangle([cx - 55, cy + 65, cx + 85, cy + 75], fill=(45, 55, 72))

    # Text
    title_font = get_font(36, bold=True)
    sub_font = get_font(16)

    draw.text((330, 120), "tech", fill=(150, 150, 150), font=title_font)
    draw.text((330, 165), "digest", fill=(45, 55, 72), font=title_font)
    draw.text((330, 210), "daily", fill=(255, 99, 71), font=title_font)

    draw.text((330, 280), "Less noise. More signal.", fill=(180, 180, 180), font=sub_font)

    img.save("D:/MyIdea/github-trending-daily/design/logos/logo_12_letter.png", "PNG")
    print("Logo 12 (Letter) created!")


# ============================================================
# LOGO 13: Data Visualization Style
# ============================================================
def create_dataviz_logo():
    """Data visualization / chart style"""
    width, height = 800, 400
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = 180, 200

    # Bar chart representation
    bars = [
        (40, 120, (36, 41, 46)),      # GitHub
        (30, 100, (255, 102, 0)),     # HN
        (25, 80, (218, 85, 47)),      # PH
        (30, 90, (59, 73, 223)),      # Dev.to
    ]

    bar_width = 35
    bar_x = cx - 90

    for i, (_, bar_height, color) in enumerate(bars):
        x = bar_x + i * (bar_width + 10)
        y = cy + 60 - bar_height
        draw_rounded_rect(draw, (x, y, x + bar_width, cy + 60), 5, color)

    # Trend line
    points = [
        (bar_x + 17, cy + 60 - 120),
        (bar_x + 62, cy + 60 - 100),
        (bar_x + 107, cy + 60 - 80),
        (bar_x + 152, cy + 60 - 90),
    ]
    for i in range(len(points) - 1):
        draw.line([points[i], points[i + 1]], fill=(102, 126, 234), width=3)

    for point in points:
        draw.ellipse([point[0] - 5, point[1] - 5, point[0] + 5, point[1] + 5], fill=(102, 126, 234))

    # Upward arrow
    arrow_x = cx + 70
    draw.polygon([
        (arrow_x, cy - 80),
        (arrow_x - 15, cy - 50),
        (arrow_x + 15, cy - 50),
    ], fill=(50, 205, 50))

    # Text
    title_font = get_font(44, bold=True)
    sub_font = get_font(14)

    draw.text((330, 130), "Tech Digest", fill=(45, 55, 72), font=title_font)
    draw.text((330, 190), "Daily", fill=(102, 126, 234), font=title_font)

    # Mini legend
    legend_y = 270
    legend_items = [("GH", (36, 41, 46)), ("HN", (255, 102, 0)), ("PH", (218, 85, 47)), ("Dev", (59, 73, 223))]
    legend_x = 330
    small_font = get_font(11)

    for name, color in legend_items:
        draw.rectangle([legend_x, legend_y, legend_x + 12, legend_y + 12], fill=color)
        draw.text((legend_x + 16, legend_y - 2), name, fill=(100, 100, 100), font=small_font)
        legend_x += 55

    img.save("D:/MyIdea/github-trending-daily/design/logos/logo_13_dataviz.png", "PNG")
    print("Logo 13 (DataViz) created!")


# ============================================================
# LOGO 14: Wave/Flow Style
# ============================================================
def create_wave_logo():
    """Flowing wave/stream style"""
    width, height = 800, 400
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = 180, 200

    # Multiple flowing waves
    wave_colors = [
        (102, 126, 234, 200),
        (118, 75, 162, 180),
        (255, 99, 71, 160),
        (50, 205, 50, 140),
    ]

    for idx, color in enumerate(wave_colors):
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)

        points = []
        amplitude = 30 - idx * 5
        frequency = 0.05
        y_offset = idx * 25 - 40

        for x in range(50, 310):
            y = cy + y_offset + amplitude * math.sin(frequency * x + idx * 0.5)
            points.append((x, y))

        # Add bottom points to close the shape
        points.append((310, cy + 100))
        points.append((50, cy + 100))

        overlay_draw.polygon(points, fill=color)
        img = Image.alpha_composite(img, overlay)

    draw = ImageDraw.Draw(img)

    # Circular focal point
    draw.ellipse([cx - 35, cy - 35, cx + 35, cy + 35], fill=(255, 255, 255))
    draw.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=(102, 126, 234))

    # Arrow in center
    arrow_points = [
        (cx, cy - 15),
        (cx + 12, cy + 8),
        (cx, cy + 3),
        (cx - 12, cy + 8),
    ]
    draw.polygon(arrow_points, fill=(255, 255, 255))

    # Text
    title_font = get_font(48, bold=True)
    sub_font = get_font(14)

    draw.text((350, 130), "Tech Digest", fill=(45, 55, 72), font=title_font)
    draw.text((350, 195), "Daily", fill=(102, 126, 234), font=title_font)
    draw.text((350, 270), "Ride the information wave", fill=(150, 150, 150), font=sub_font)

    img.save("D:/MyIdea/github-trending-daily/design/logos/logo_14_wave.png", "PNG")
    print("Logo 14 (Wave) created!")


# ============================================================
# Create combined showcase for new logos
# ============================================================
def create_showcase_v2():
    """Create a combined showcase of all new logos"""
    width, height = 1600, 1400
    img = Image.new('RGBA', (width, height), (248, 250, 252))
    draw = ImageDraw.Draw(img)

    # Title
    title_font = get_font(36, bold=True)
    sub_font = get_font(18)

    draw.text((width // 2 - 220, 30), "Tech Digest Daily - More Logo Concepts", fill=(51, 51, 51), font=title_font)
    draw.text((width // 2 - 100, 75), "10 Additional Styles", fill=(128, 128, 128), font=sub_font)

    # Logo list
    logos = [
        ("logo_5_geometric.png", "Option E: Geometric", "几何抽象风格"),
        ("logo_6_lineart.png", "Option F: Line Art", "线条艺术风格"),
        ("logo_7_isometric.png", "Option G: Isometric 3D", "等距3D风格"),
        ("logo_8_badge.png", "Option H: Vintage Badge", "复古徽章风格"),
        ("logo_9_neon.png", "Option I: Neon Glow", "霓虹灯风格"),
        ("logo_10_pixel.png", "Option J: Pixel Art", "像素艺术风格"),
        ("logo_11_space.png", "Option K: Cosmic", "宇宙太空风格"),
        ("logo_12_letter.png", "Option L: Minimalist", "极简字母风格"),
        ("logo_13_dataviz.png", "Option M: Data Viz", "数据可视化风格"),
        ("logo_14_wave.png", "Option N: Wave Flow", "流动波浪风格"),
    ]

    # 5 columns x 2 rows layout
    cols, rows = 2, 5
    card_w, card_h = 720, 220
    margin_x, margin_y = 60, 40
    start_y = 130

    label_font = get_font(18, bold=True)
    cn_font = get_font(13)

    for i, (filename, en_label, cn_label) in enumerate(logos):
        col = i % cols
        row = i // cols

        px = margin_x + col * (card_w + margin_x)
        py = start_y + row * (card_h + margin_y)

        # Background card
        draw_rounded_rect(draw, (px, py, px + card_w, py + card_h), 12, (255, 255, 255))
        draw.rounded_rectangle([px, py, px + card_w, py + card_h], radius=12, outline=(226, 232, 240), width=2)

        # Load and paste logo
        try:
            logo = Image.open(f"D:/MyIdea/github-trending-daily/design/logos/{filename}")
            logo = logo.resize((card_w - 20, card_h - 50), Image.Resampling.LANCZOS)
            img.paste(logo, (px + 10, py + 5), logo if logo.mode == 'RGBA' else None)
        except Exception as e:
            print(f"Could not load {filename}: {e}")

        # Labels
        draw.text((px + 10, py + card_h - 35), en_label, fill=(51, 51, 51), font=label_font)
        draw.text((px + 300, py + card_h - 33), cn_label, fill=(128, 128, 128), font=cn_font)

    img.save("D:/MyIdea/github-trending-daily/design/logos/logo_showcase_v2.png", "PNG")
    print("Showcase V2 created!")


# Generate all logos
if __name__ == "__main__":
    print("Generating 10 additional Tech Digest Daily logos...")
    create_geometric_logo()
    create_lineart_logo()
    create_isometric_logo()
    create_badge_logo()
    create_neon_logo()
    create_pixel_logo()
    create_space_logo()
    create_letter_logo()
    create_dataviz_logo()
    create_wave_logo()
    create_showcase_v2()
    print("\nAll 10 new logos generated!")
