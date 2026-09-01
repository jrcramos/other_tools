"""
Generates high-resolution multi-layer icon and splash assets for Power Tools.
"""
import os
from PIL import Image, ImageDraw, ImageFilter

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

def create_app_icon():
    size = 512
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Outer rounded container background with subtle gradient
    margin = 32
    radius = 96
    
    # Shadow/glow layer
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.rounded_rectangle(
        [margin - 8, margin - 8, size - margin + 8, size - margin + 8],
        radius=radius + 8,
        fill=(59, 130, 246, 60)  # Blue glow
    )
    glow = glow.filter(ImageFilter.GaussianBlur(16))
    img.paste(glow, (0, 0), glow)

    # Base card background
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=radius,
        fill=(18, 20, 26, 255),
        outline=(59, 130, 246, 200),
        width=6
    )

    # 2. Draw Lightning / Power Bolt with vibrant gradient colors
    bolt_points = [
        (280, 80),   # Top point
        (160, 260),  # Left middle point
        (250, 260),  # Inner right
        (210, 430),  # Bottom tip
        (360, 220),  # Right middle point
        (270, 220),  # Inner left
    ]

    # Inner Glow
    bolt_glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bg_draw = ImageDraw.Draw(bolt_glow)
    bg_draw.polygon(bolt_points, fill=(56, 189, 248, 120))
    bolt_glow = bolt_glow.filter(ImageFilter.GaussianBlur(12))
    img.paste(bolt_glow, (0, 0), bolt_glow)

    # Main Bolt (Cyan to Electric Blue Gradient effect)
    draw.polygon(bolt_points, fill=(56, 189, 248, 255))
    
    # Highlight accent on bolt
    highlight_points = [
        (275, 95),
        (185, 250),
        (255, 250),
        (225, 380),
        (260, 230),
    ]
    draw.polygon(highlight_points, fill=(255, 255, 255, 220))

    # Save PNG
    png_path = os.path.join(ASSETS_DIR, "icon.png")
    img.save(png_path, "PNG")
    print(f"[+] Created icon PNG: {png_path}")

    # Save Multi-size ICO
    ico_path = os.path.join(ASSETS_DIR, "icon.ico")
    icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save(ico_path, format="ICO", sizes=icon_sizes)
    print(f"[+] Created icon ICO: {ico_path}")


def create_splash_asset():
    w, h = 480, 270
    img = Image.new("RGBA", (w, h), (18, 19, 24, 255))
    draw = ImageDraw.Draw(img)

    # Border
    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=16, outline=(59, 130, 246, 180), width=2)

    # Inner subtle glow
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow)
    g_draw.ellipse([w//2 - 120, h//2 - 90, w//2 + 120, h//2 + 90], fill=(59, 130, 246, 30))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    img.paste(glow, (0, 0), glow)

    # Save Splash PNG
    splash_path = os.path.join(ASSETS_DIR, "splash.png")
    img.save(splash_path, "PNG")
    print(f"[+] Created splash asset: {splash_path}")


if __name__ == "__main__":
    create_app_icon()
    create_splash_asset()
