"""
render_previews.py
Renders high-resolution preview images of the 7 Snoopy poses
constructed from the characters: '閻', '姿', '桂'.
"""

import json
import os
from PIL import Image, ImageDraw, ImageFont

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, 'assets', 'snoopy_poses.json')
    out_dir = os.path.join(base_dir, 'assets', 'previews')
    os.makedirs(out_dir, exist_ok=True)

    with open(json_path, 'r', encoding='utf-8') as f:
        poses = json.load(f)

    font_path = "C:/Windows/Fonts/msjhbd.ttc"
    
    for idx, pose in enumerate(poses):
        img = Image.new('RGB', (800, 800), '#fbf8f1') # Warm vintage paper
        draw = ImageDraw.Draw(img)

        # Subtle paper border
        draw.rectangle([20, 20, 780, 780], outline='#e2d9cc', width=2)
        draw.rectangle([24, 24, 776, 776], outline='#ece4d8', width=1)

        # Title
        title_font = ImageFont.truetype(font_path, 28)
        sub_font = ImageFont.truetype(font_path, 15)
        quote_font = ImageFont.truetype(font_path, 14)

        draw.text((400, 50), f"閻姿桂 × 史奴比 #{idx+1}：{pose['title']}", fill='#1c1917', font=title_font, anchor='mm')
        draw.text((400, 85), pose['englishTitle'], fill='#78716c', font=sub_font, anchor='mm')
        draw.text((400, 740), pose['quote'], fill='#44403c', font=quote_font, anchor='mm')

        # Center particles at (400, 420)
        cx, cy = 400, 410

        # Sort particles so white/background fills draw first, then contours, then dark features
        sorted_p = sorted(pose['particles'], key=lambda p: 0 if 'fill' in p['role'] else 1)

        for p in sorted_p:
            char = p['char']
            px = cx + p['x'] * 1.25
            py = cy + p['y'] * 1.25
            size = int(p['size'] * 1.25)
            font = ImageFont.truetype(font_path, size)
            color = p['color']

            # If body fill (white), add a gentle soft gray stroke so it pops on cream paper
            if color == '#ffffff':
                draw.text((px, py), char, fill='#cbd5e1', font=font, anchor='mm', stroke_width=2, stroke_fill='#94a3b8')
                draw.text((px, py), char, fill='#ffffff', font=font, anchor='mm')
            else:
                draw.text((px, py), char, fill=color, font=font, anchor='mm')

        out_path = os.path.join(out_dir, f"pose_{idx+1}_{pose['id']}.png")
        img.save(out_path)
        print(f"Rendered: {out_path}")

if __name__ == '__main__':
    main()
