"""
Tech Digest Daily Logo Generator
Generate 4 different style logo concepts
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

# Create output directory
os.makedirs("D:/MyIdea/github-trending-daily/design/logos", exist_ok=True)

def get_font(size, bold=False):
    """Get system font with fallback"""
    fonts_to_try = [
        "C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
    ]
    for font_path in fonts_to_try:
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
    return ImageFont.load_default()


def draw_gradient_rect(draw, x1, y1, x2, y2, color1, color2, direction='horizontal'):
    """Draw a gradient rectangle"""
    if direction == 'horizontal':
        for x in range(int(x1), int(x2)):
            ratio = (x - x1) / (x2 - x1)
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
            draw.line([(x, y1), (x, y2)], fill=(r, g, b))
    else:
        for y in range(int(y1), int(y2)):
            ratio = (y - y1) / (y2 - y1)
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
            draw.line([(x1, y), (x2, y)], fill=(r, g, b))


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
# LOGO 1: Modern Gradient Tech Style
# ============================================================
def create_gradient_logo():
    """Modern gradient tech style logo"""
    width, height = 800, 400
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Background gradient circle
    cx, cy = 200, 200
    radius = 140

    # Draw gradient circle with multiple layers
    for r in range(radius, 0, -1):
        ratio = r / radius
        # Gradient from purple to blue to cyan
        if ratio > 0.5:
            r_color = int(102 + (118 - 102) * (1 - ratio) * 2)
            g_color = int(126 + (75 - 126) * (1 - ratio) * 2)
            b_color = int(234 + (162 - 234) * (1 - ratio) * 2)
        else:
            r_color = int(118 + (6 - 118) * (0.5 - ratio) * 2)
            g_color = int(75 + (182 - 75) * (0.5 - ratio) * 2)
            b_color = int(162 + (212 - 162) * (0.5 - ratio) * 2)

        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(r_color, g_color, b_color))

    # Draw converging lines (representing data streams)
    lines_data = [
        ((60, 80), (cx - 30, cy - 20)),
        ((60, 320), (cx - 30, cy + 20)),
        ((cx - 80, 40), (cx - 10, cy - 30)),
        ((cx - 80, 360), (cx - 10, cy + 30)),
    ]

    for start, end in lines_data:
        for offset in range(-2, 3):
            draw.line([start, end], fill=(255, 255, 255, 150), width=3)

    # Central icon - stylized "TD" or flame/rocket
    # Draw a stylized upward arrow/flame
    flame_points = [
        (cx - 40, cy + 50),
        (cx, cy - 60),
        (cx + 40, cy + 50),
        (cx + 20, cy + 30),
        (cx, cy + 50),
        (cx - 20, cy + 30),
    ]
    draw.polygon(flame_points, fill=(255, 255, 255))

    # Inner flame detail
    inner_flame = [
        (cx - 15, cy + 30),
        (cx, cy - 20),
        (cx + 15, cy + 30),
    ]
    draw.polygon(inner_flame, fill=(102, 126, 234))

    # Text
    title_font = get_font(48, bold=True)
    sub_font = get_font(18)

    draw.text((370, 150), "Tech Digest", fill=(51, 51, 51), font=title_font)
    draw.text((370, 210), "Daily", fill=(102, 126, 234), font=title_font)
    draw.text((370, 280), "AI-Powered Tech News Aggregator", fill=(128, 128, 128), font=sub_font)

    img.save("D:/MyIdea/github-trending-daily/design/logos/logo_1_gradient.png", "PNG")
    print("Logo 1 (Gradient) created!")
    return img


# ============================================================
# LOGO 2: Flat Minimalist Icon Style
# ============================================================
def create_flat_logo():
    """Clean flat icon style logo"""
    width, height = 800, 400
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Colors
    primary = (45, 55, 72)       # Dark blue-gray
    accent = (56, 161, 105)      # Green
    secondary = (237, 137, 54)   # Orange

    # Icon - Stack of cards representing aggregated content
    cx, cy = 180, 200
    card_width, card_height = 120, 80

    # Back card (GitHub - dark)
    draw_rounded_rect(draw, (cx - 50, cy - 30, cx + 70, cy + 50), 8, (36, 41, 46))

    # Middle card (HN - orange)
    draw_rounded_rect(draw, (cx - 40, cy - 40, cx + 80, cy + 40), 8, secondary)

    # Front card (main - primary)
    draw_rounded_rect(draw, (cx - 30, cy - 50, cx + 90, cy + 30), 8, primary)

    # AI sparkle on front card
    sparkle_cx, sparkle_cy = cx + 30, cy - 10
    sparkle_size = 20

    # 4-point star
    points = []
    for i in range(8):
        angle = i * math.pi / 4
        r = sparkle_size if i % 2 == 0 else sparkle_size * 0.4
        points.append((
            sparkle_cx + r * math.sin(angle),
            sparkle_cy - r * math.cos(angle)
        ))
    draw.polygon(points, fill=(255, 255, 255))

    # Small dots representing data
    for dx, dy in [(-20, -30), (50, -30), (-20, 10), (50, 10)]:
        draw.ellipse([cx + dx - 4, cy + dy - 4, cx + dx + 4, cy + dy + 4], fill=(255, 255, 255, 180))

    # Text
    title_font = get_font(52, bold=True)
    sub_font = get_font(16)

    draw.text((320, 130), "Tech Digest", fill=primary, font=title_font)
    draw.text((320, 195), "Daily", fill=accent, font=title_font)

    # Source badges
    badge_y = 290
    badges = [
        ("GitHub", (36, 41, 46)),
        ("HN", (255, 102, 0)),
        ("PH", (218, 85, 47)),
        ("Dev.to", (59, 73, 223)),
    ]

    badge_x = 320
    small_font = get_font(12, bold=True)
    for name, color in badges:
        text_width = len(name) * 8 + 16
        draw_rounded_rect(draw, (badge_x, badge_y, badge_x + text_width, badge_y + 24), 4, color)
        draw.text((badge_x + 8, badge_y + 4), name, fill=(255, 255, 255), font=small_font)
        badge_x += text_width + 8

    img.save("D:/MyIdea/github-trending-daily/design/logos/logo_2_flat.png", "PNG")
    print("Logo 2 (Flat) created!")
    return img


# ============================================================
# LOGO 3: Terminal/Code Retro Style
# ============================================================
def create_terminal_logo():
    """Terminal/code retro style logo"""
    width, height = 800, 400
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Terminal window background
    term_x, term_y = 40, 60
    term_w, term_h = 720, 280

    # Terminal frame
    draw_rounded_rect(draw, (term_x, term_y, term_x + term_w, term_y + term_h), 12, (30, 30, 30))

    # Title bar
    draw_rounded_rect(draw, (term_x, term_y, term_x + term_w, term_y + 36), 12, (50, 50, 50))
    draw.rectangle([term_x, term_y + 24, term_x + term_w, term_y + 36], fill=(50, 50, 50))

    # Window buttons
    draw.ellipse([term_x + 16, term_y + 10, term_x + 28, term_y + 22], fill=(255, 95, 86))
    draw.ellipse([term_x + 36, term_y + 10, term_x + 48, term_y + 22], fill=(255, 189, 46))
    draw.ellipse([term_x + 56, term_y + 10, term_x + 68, term_y + 22], fill=(39, 201, 63))

    # Terminal content
    mono_font = get_font(20)
    small_mono = get_font(14)

    green = (0, 255, 136)
    cyan = (0, 255, 255)
    yellow = (255, 255, 0)
    white = (220, 220, 220)
    gray = (128, 128, 128)

    y_pos = term_y + 56
    line_height = 28

    # Line 1: Command
    draw.text((term_x + 20, y_pos), "$ ", fill=green, font=mono_font)
    draw.text((term_x + 50, y_pos), "tech-digest --fetch-all --ai-summary", fill=white, font=mono_font)

    # Line 2: Fetching
    y_pos += line_height
    draw.text((term_x + 20, y_pos), "[INFO]", fill=cyan, font=small_mono)
    draw.text((term_x + 80, y_pos), " Fetching sources...", fill=gray, font=small_mono)

    # Line 3-6: Source results
    sources = [
        ("GitHub Trending", "15", green),
        ("Hacker News", "10", (255, 102, 0)),
        ("Product Hunt", "8", (218, 85, 47)),
        ("Dev.to", "10", (59, 73, 223)),
    ]

    for name, count, color in sources:
        y_pos += line_height - 6
        draw.text((term_x + 20, y_pos), "  ✓ ", fill=color, font=small_mono)
        draw.text((term_x + 55, y_pos), f"{name}: {count} items", fill=white, font=small_mono)

    # Line 7: AI Summary
    y_pos += line_height
    draw.text((term_x + 20, y_pos), "[AI]", fill=yellow, font=small_mono)
    draw.text((term_x + 60, y_pos), " Generating smart summary...", fill=gray, font=small_mono)
    draw.text((term_x + 290, y_pos), "Done!", fill=green, font=small_mono)

    # Big title overlay
    title_font = get_font(56, bold=True)

    # Glowing text effect
    draw.text((term_x + 320, term_y + 90), "TECH", fill=(0, 200, 100), font=title_font)
    draw.text((term_x + 320, term_y + 150), "DIGEST", fill=(0, 255, 136), font=title_font)

    img.save("D:/MyIdea/github-trending-daily/design/logos/logo_3_terminal.png", "PNG")
    print("Logo 3 (Terminal) created!")
    return img


# ============================================================
# LOGO 4: Cute Mascot Style
# ============================================================
def create_mascot_logo():
    """Cute mascot style logo"""
    width, height = 800, 400
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Colors
    body_color = (102, 126, 234)      # Purple-blue
    face_color = (255, 255, 255)
    blush = (255, 182, 193)
    accent = (255, 159, 67)

    cx, cy = 180, 200

    # Body - rounded robot/creature
    # Main body
    draw.ellipse([cx - 80, cy - 70, cx + 80, cy + 90], fill=body_color)

    # Face area
    draw.ellipse([cx - 60, cy - 50, cx + 60, cy + 50], fill=face_color)

    # Eyes - cute anime style
    # Left eye
    draw.ellipse([cx - 40, cy - 25, cx - 10, cy + 15], fill=(40, 40, 40))
    draw.ellipse([cx - 35, cy - 18, cx - 20, cy - 5], fill=(255, 255, 255))

    # Right eye
    draw.ellipse([cx + 10, cy - 25, cx + 40, cy + 15], fill=(40, 40, 40))
    draw.ellipse([cx + 15, cy - 18, cx + 30, cy - 5], fill=(255, 255, 255))

    # Blush
    draw.ellipse([cx - 55, cy + 10, cx - 35, cy + 25], fill=blush)
    draw.ellipse([cx + 35, cy + 10, cx + 55, cy + 25], fill=blush)

    # Smile
    draw.arc([cx - 20, cy + 15, cx + 20, cy + 40], 0, 180, fill=(40, 40, 40), width=3)

    # Antenna with data signal
    draw.rectangle([cx - 5, cy - 95, cx + 5, cy - 70], fill=body_color)
    draw.ellipse([cx - 15, cy - 110, cx + 15, cy - 85], fill=accent)

    # Signal waves
    for i, offset in enumerate([15, 25, 35]):
        alpha = 255 - i * 60
        draw.arc([cx - offset, cy - 130, cx + offset, cy - 100], 220, 320, fill=accent, width=3)

    # Little floating icons around
    # GitHub octocat hint
    draw.ellipse([cx + 70, cy - 80, cx + 95, cy - 55], fill=(36, 41, 46))

    # HN
    draw.rectangle([cx - 100, cy - 60, cx - 75, cy - 35], fill=(255, 102, 0))

    # Heart
    heart_x, heart_y = cx + 85, cy + 30
    draw.ellipse([heart_x - 10, heart_y - 10, heart_x, heart_y + 5], fill=(255, 100, 100))
    draw.ellipse([heart_x, heart_y - 10, heart_x + 10, heart_y + 5], fill=(255, 100, 100))
    draw.polygon([(heart_x - 10, heart_y), (heart_x + 10, heart_y), (heart_x, heart_y + 15)], fill=(255, 100, 100))

    # Text
    title_font = get_font(44, bold=True)
    sub_font = get_font(16)
    cute_font = get_font(14)

    draw.text((300, 120), "Tech Digest", fill=(51, 51, 51), font=title_font)
    draw.text((300, 175), "Daily", fill=body_color, font=title_font)

    # Tagline with emoji-style
    draw.text((300, 250), "Your friendly AI tech curator!", fill=(128, 128, 128), font=sub_font)

    # Small decorative elements
    stars = [(320, 290), (400, 280), (480, 295), (550, 285)]
    for sx, sy in stars:
        draw.text((sx, sy), "✦", fill=accent, font=cute_font)

    img.save("D:/MyIdea/github-trending-daily/design/logos/logo_4_mascot.png", "PNG")
    print("Logo 4 (Mascot) created!")
    return img


# ============================================================
# Combined showcase
# ============================================================
def create_showcase():
    """Create a combined showcase of all logos"""
    width, height = 1600, 900
    img = Image.new('RGBA', (width, height), (248, 250, 252))
    draw = ImageDraw.Draw(img)

    # Title
    title_font = get_font(36, bold=True)
    sub_font = get_font(18)

    draw.text((width // 2 - 200, 30), "Tech Digest Daily - Logo Concepts", fill=(51, 51, 51), font=title_font)
    draw.text((width // 2 - 120, 75), "Select your preferred style", fill=(128, 128, 128), font=sub_font)

    # Load and place each logo
    logos = [
        ("logo_1_gradient.png", "Option A: Modern Gradient", "科技渐变风格"),
        ("logo_2_flat.png", "Option B: Flat Minimalist", "扁平简洁风格"),
        ("logo_3_terminal.png", "Option C: Terminal Retro", "终端复古风格"),
        ("logo_4_mascot.png", "Option D: Cute Mascot", "可爱吉祥物风格"),
    ]

    positions = [
        (50, 130),
        (850, 130),
        (50, 520),
        (850, 520),
    ]

    label_font = get_font(20, bold=True)
    cn_font = get_font(14)

    for i, ((filename, en_label, cn_label), (px, py)) in enumerate(zip(logos, positions)):
        # Background card
        draw_rounded_rect(draw, (px - 10, py - 10, px + 710, py + 350), 16, (255, 255, 255))

        # Border
        draw.rounded_rectangle([px - 10, py - 10, px + 710, py + 350], radius=16, outline=(226, 232, 240), width=2)

        # Load and paste logo
        try:
            logo = Image.open(f"D:/MyIdea/github-trending-daily/design/logos/{filename}")
            # Resize to fit
            logo = logo.resize((700, 300), Image.Resampling.LANCZOS)
            img.paste(logo, (px, py + 10), logo if logo.mode == 'RGBA' else None)
        except Exception as e:
            print(f"Could not load {filename}: {e}")

        # Labels
        draw.text((px + 10, py + 315), en_label, fill=(51, 51, 51), font=label_font)
        draw.text((px + 350, py + 318), cn_label, fill=(128, 128, 128), font=cn_font)

    img.save("D:/MyIdea/github-trending-daily/design/logos/logo_showcase.png", "PNG")
    print("Showcase created!")


# Generate all logos
if __name__ == "__main__":
    print("Generating Tech Digest Daily logos...")
    create_gradient_logo()
    create_flat_logo()
    create_terminal_logo()
    create_mascot_logo()
    create_showcase()
    print("\nAll logos generated in design/logos/ directory!")
