import os
import sys
from PIL import Image

src_path = "assets/logo.png"
res_dir = "android/app/src/main/res"

sizes_legacy = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192,
}

sizes_foreground = {
    "mipmap-mdpi": 108,
    "mipmap-hdpi": 162,
    "mipmap-xhdpi": 216,
    "mipmap-xxhdpi": 324,
    "mipmap-xxxhdpi": 432,
}

if not os.path.exists(src_path):
    print(f"ERROR: Source file {src_path} not found!")
    sys.exit(1)

try:
    print(f"Loading source icon: {src_path}")
    im = Image.open(src_path)
    
    # Generate legacy/round square icons
    for folder, size in sizes_legacy.items():
        target_folder = os.path.join(res_dir, folder)
        os.makedirs(target_folder, exist_ok=True)
        
        # Legacy square launcher icon
        out_square = os.path.join(target_folder, "ic_launcher.png")
        print(f"Generating legacy icon: {out_square} ({size}x{size})")
        im.resize((size, size), Image.Resampling.LANCZOS).save(out_square, "PNG")
        
        # Legacy round launcher icon
        out_round = os.path.join(target_folder, "ic_launcher_round.png")
        print(f"Generating round icon: {out_round} ({size}x{size})")
        im.resize((size, size), Image.Resampling.LANCZOS).save(out_round, "PNG")

    # Generate adaptive foreground icons
    for folder, size in sizes_foreground.items():
        target_folder = os.path.join(res_dir, folder)
        os.makedirs(target_folder, exist_ok=True)
        
        # Adaptive foreground launcher icon
        out_fore = os.path.join(target_folder, "ic_launcher_foreground.png")
        print(f"Generating adaptive foreground: {out_fore} ({size}x{size})")
        im.resize((size, size), Image.Resampling.LANCZOS).save(out_fore, "PNG")
        
    print("SUCCESS: Successfully updated all Android launcher icons!")
except Exception as e:
    print(f"ERROR during icon generation: {e}")
    sys.exit(2)
