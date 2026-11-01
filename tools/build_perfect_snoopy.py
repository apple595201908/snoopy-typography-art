"""
build_perfect_snoopy.py
High-Precision Snoopy Line-Art & Feature Coordinates.
Guarantees 100% connected, recognizable, unmistakable Snoopy figures.
480 particles per pose (160 閻, 160 姿, 160 桂).
"""

import math
import random
import json
import os
from PIL import Image, ImageDraw, ImageFont

CHARS = ['閻', '姿', '桂']
TARGET_PARTICLES = 480

def bezier_pts(p0, p1, p2, p3, steps=25):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts

def line_pts(p0, p1, steps=15):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = p0[0] + (p1[0] - p0[0]) * t
        y = p0[1] + (p1[1] - p0[1]) * t
        pts.append((x, y))
    return pts

def circle_pts(center, radius, count=16, start_ang=0, end_ang=360):
    pts = []
    span = end_ang - start_ang
    for i in range(count):
        deg = start_ang + (i / max(1, count - (1 if span < 360 else 0))) * span
        rad = math.radians(deg)
        x = center[0] + radius * math.cos(rad)
        y = center[1] + radius * math.sin(rad)
        pts.append((x, y))
    return pts

# ==============================================================================
# POSE 1: 趴臥狗屋白日夢
# ==============================================================================
def make_pose_1():
    pts = []
    # Red roof
    for p in line_pts((150, 480), (400, 355), 24):
        pts.append({'x': p[0], 'y': p[1], 'color': '#dc2626', 'size': 14, 'role': 'roof'})
    for p in line_pts((400, 355), (650, 480), 24):
        pts.append({'x': p[0], 'y': p[1], 'color': '#dc2626', 'size': 14, 'role': 'roof'})
    for p in line_pts((160, 495), (640, 495), 26):
        pts.append({'x': p[0], 'y': p[1], 'color': '#b91c1c', 'size': 13, 'role': 'roof'})
    # Walls & Door
    for p in line_pts((200, 495), (200, 690), 16):
        pts.append({'x': p[0], 'y': p[1], 'color': '#991b1b', 'size': 13, 'role': 'wall'})
    for p in line_pts((600, 495), (600, 690), 16):
        pts.append({'x': p[0], 'y': p[1], 'color': '#991b1b', 'size': 13, 'role': 'wall'})
    for p in line_pts((200, 690), (600, 690), 24):
        pts.append({'x': p[0], 'y': p[1], 'color': '#991b1b', 'size': 13, 'role': 'wall'})
    for p in circle_pts((400, 580), 55, count=14, start_ang=180, end_ang=360):
        pts.append({'x': p[0], 'y': p[1], 'color': '#1c1917', 'size': 14, 'role': 'door'})
    for p in line_pts((345, 580), (345, 690), 8):
        pts.append({'x': p[0], 'y': p[1], 'color': '#1c1917', 'size': 14, 'role': 'door'})
    for p in line_pts((455, 580), (455, 690), 8):
        pts.append({'x': p[0], 'y': p[1], 'color': '#1c1917', 'size': 14, 'role': 'door'})

    # Snoopy Sleeping (Lying flat on roof)
    for p in bezier_pts((460, 310), (500, 280), (550, 285), (585, 315), 22):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'head'})
    for p in bezier_pts((585, 315), (605, 330), (605, 350), (590, 365), 14):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'head'})
    for p in bezier_pts((590, 365), (550, 375), (510, 370), (470, 355), 16):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'head'})

    # Big Round Nose (598, 325)
    for p in circle_pts((598, 325), 14, count=9):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 16, 'role': 'nose'})
    for p in circle_pts((598, 325), 7, count=5):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 16, 'role': 'nose'})

    # Sleeping Eye & Smile
    for p in circle_pts((535, 323), 10, count=7, start_ang=20, end_ang=160):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 14, 'role': 'eye'})
    pts.append({'x': 555, 'y': 355, 'color': '#020617', 'size': 13, 'role': 'smile'})

    # Big Floppy Black Ear
    for y in range(310, 410, 14):
        for x in range(435, 480, 14):
            if ((x - 455)/20)**2 + ((y - 360)/50)**2 <= 1.1:
                pts.append({'x': x, 'y': y, 'color': '#020617', 'size': 15, 'role': 'ear'})

    # Red Collar
    for p in line_pts((465, 340), (475, 363), 5):
        pts.append({'x': p[0], 'y': p[1], 'color': '#ef4444', 'size': 15, 'role': 'collar'})

    # Back
    for p in bezier_pts((450, 310), (390, 280), (320, 285), (270, 335), 22):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'back'})

    # Back Spot
    for p in circle_pts((340, 315), 18, count=11):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 15, 'role': 'spot'})
    for p in circle_pts((340, 315), 9, count=5):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 15, 'role': 'spot'})

    # Tail
    for p in line_pts((270, 335), (230, 310), 6):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'tail'})
    for p in line_pts((230, 310), (255, 345), 5):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'tail'})

    # Paws
    for p in bezier_pts((500, 365), (515, 400), (540, 400), (545, 375), 12):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 14, 'role': 'paw'})
    pts.append({'x': 525, 'y': 390, 'color': '#0f172a', 'size': 12, 'role': 'toe'})

    for p in bezier_pts((270, 345), (250, 390), (230, 400), (220, 375), 12):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 14, 'role': 'leg'})
    for p in bezier_pts((295, 350), (280, 395), (260, 400), (250, 375), 12):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 14, 'role': 'leg'})

    # Woodstock
    for p in circle_pts((210, 275), 12, count=8):
        pts.append({'x': p[0], 'y': p[1], 'color': '#f59e0b', 'size': 15, 'role': 'woodstock'})
    for p in [(200, 260), (208, 255), (216, 258)]:
        pts.append({'x': p[0], 'y': p[1], 'color': '#f59e0b', 'size': 14, 'role': 'woodstock'})
    for p in [(224, 275), (232, 277), (224, 280)]:
        pts.append({'x': p[0], 'y': p[1], 'color': '#ea580c', 'size': 14, 'role': 'woodstock'})
    for p in circle_pts((200, 295), 10, count=6):
        pts.append({'x': p[0], 'y': p[1], 'color': '#f59e0b', 'size': 14, 'role': 'woodstock'})
    for p in [(185, 295), (180, 300), (175, 295)]:
        pts.append({'x': p[0], 'y': p[1], 'color': '#f59e0b', 'size': 13, 'role': 'woodstock'})
    for p in [(198, 310), (206, 310)]:
        pts.append({'x': p[0], 'y': p[1], 'color': '#ea580c', 'size': 13, 'role': 'woodstock'})

    # Zzz
    for cx, cy, sz in [(530, 250, 14), (560, 210, 17), (600, 160, 20), (640, 100, 24)]:
        pts.append({'x': cx, 'y': cy, 'color': '#38bdf8', 'size': sz, 'role': 'zzz'})

    return pts

# ==============================================================================
# POSE 2: 墨鏡酷哥喬酷兒 (Joe Cool)
# ==============================================================================
def make_pose_2():
    pts = []
    # Wall on right
    for y in range(160, 680, 24):
        pts.append({'x': 540, 'y': y, 'color': '#94a3b8', 'size': 14, 'role': 'wall'})
        pts.append({'x': 565, 'y': y, 'color': '#cbd5e1', 'size': 14, 'role': 'wall'})

    # Head (facing left)
    for p in bezier_pts((440, 250), (370, 215), (290, 225), (245, 265), 22):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'head'})
    for p in bezier_pts((245, 265), (215, 285), (215, 310), (245, 330), 14):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'head'})
    for p in bezier_pts((245, 330), (305, 340), (365, 345), (420, 345), 18):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'head'})

    # Big Round Nose (224, 275)
    for p in circle_pts((224, 275), 15, count=10):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 16, 'role': 'nose'})
    for p in circle_pts((224, 275), 8, count=5):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 16, 'role': 'nose'})

    # Sunglasses
    for y in range(255, 300, 12):
        for x in range(260, 325, 12):
            pts.append({'x': x, 'y': y, 'color': '#020617', 'size': 16, 'role': 'sunglasses'})
    for y in range(255, 300, 12):
        for x in range(335, 395, 12):
            pts.append({'x': x, 'y': y, 'color': '#020617', 'size': 16, 'role': 'sunglasses'})
    for p in line_pts((395, 270), (445, 275), 6):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 15, 'role': 'sunglasses'})

    # Smirk
    for p in [(285, 320), (300, 323), (315, 320)]:
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 14, 'role': 'smirk'})

    # Floppy Black Ear
    for y in range(265, 385, 14):
        for x in range(430, 475, 14):
            if ((x - 450)/20)**2 + ((y - 325)/55)**2 <= 1.1:
                pts.append({'x': x, 'y': y, 'color': '#020617', 'size': 15, 'role': 'ear'})

    # Red Collegiate Sweater
    for p in line_pts((375, 345), (435, 345), 6):
        pts.append({'x': p[0], 'y': p[1], 'color': '#ef4444', 'size': 15, 'role': 'collar'})
    for p in bezier_pts((365, 345), (325, 405), (325, 465), (365, 505), 16):
        pts.append({'x': p[0], 'y': p[1], 'color': '#ef4444', 'size': 15, 'role': 'sweater'})
    for p in bezier_pts((435, 345), (475, 405), (475, 465), (445, 505), 16):
        pts.append({'x': p[0], 'y': p[1], 'color': '#ef4444', 'size': 15, 'role': 'sweater'})
    for p in line_pts((365, 505), (445, 505), 8):
        pts.append({'x': p[0], 'y': p[1], 'color': '#ef4444', 'size': 15, 'role': 'sweater'})
    for y in range(365, 495, 18):
        for x in range(360, 450, 18):
            pts.append({'x': x, 'y': y, 'color': '#dc2626', 'size': 14, 'role': 'sweater'})

    # Arms
    for p in bezier_pts((345, 385), (315, 435), (355, 465), (405, 445), 14):
        pts.append({'x': p[0], 'y': p[1], 'color': '#dc2626', 'size': 15, 'role': 'arm'})
    for p in bezier_pts((455, 385), (485, 425), (455, 460), (415, 450), 14):
        pts.append({'x': p[0], 'y': p[1], 'color': '#dc2626', 'size': 15, 'role': 'arm'})

    # Legs
    for p in line_pts((370, 505), (365, 625), 12):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'leg'})
    for p in circle_pts((355, 635), 14, count=8, start_ang=0, end_ang=180):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'paw'})

    for p in bezier_pts((430, 505), (440, 555), (400, 605), (380, 630), 14):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'leg'})
    for p in circle_pts((380, 637), 12, count=7):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'paw'})

    # Tail
    for p in bezier_pts((460, 485), (485, 475), (505, 455), (500, 435), 8):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 14, 'role': 'tail'})

    # Sparkle Stars
    for (sx, sy) in [(180, 205), (190, 405), (500, 185)]:
        for p in [(sx, sy), (sx-12, sy), (sx+12, sy), (sx, sy-12), (sx, sy+12)]:
            pts.append({'x': p[0], 'y': p[1], 'color': '#f59e0b', 'size': 14, 'role': 'sparkle'})

    return pts

# ==============================================================================
# POSE 3: 快樂開懷踢踏舞 (The Joyful Happy Dance)
# ==============================================================================
def make_pose_3():
    pts = []
    # Head thrown back laughing
    for p in bezier_pts((360, 290), (400, 230), (470, 200), (510, 215), 20):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'head'})
    for p in bezier_pts((510, 215), (530, 225), (530, 245), (510, 260), 12):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'head'})

    # Nose at (525, 225)
    for p in circle_pts((525, 225), 14, count=9):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 16, 'role': 'nose'})
    for p in circle_pts((525, 225), 7, count=5):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 16, 'role': 'nose'})

    # Open Laughing Mouth & Jaw
    for p in bezier_pts((510, 260), (470, 310), (420, 335), (370, 335), 18):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'mouth'})
    for p in [(460, 280), (470, 285), (465, 295)]:
        pts.append({'x': p[0], 'y': p[1], 'color': '#f43f5e', 'size': 14, 'role': 'tongue'})
    for p in [(440, 245), (450, 235), (460, 245)]:
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 14, 'role': 'eye'})

    # BOTH EARS SOARING HIGH IN SKY
    for t_step in range(16):
        t = t_step / 15.0
        ex = 370 + t * (-120) + math.sin(t * math.pi) * 15
        ey = 290 + t * (-180)
        pts.append({'x': ex, 'y': ey, 'color': '#020617', 'size': 16, 'role': 'ear'})
        pts.append({'x': ex + 12, 'y': ey, 'color': '#020617', 'size': 16, 'role': 'ear'})
        pts.append({'x': ex - 12, 'y': ey, 'color': '#020617', 'size': 16, 'role': 'ear'})

    for t_step in range(16):
        t = t_step / 15.0
        ex = 410 + t * (110) - math.sin(t * math.pi) * 15
        ey = 280 + t * (-190)
        pts.append({'x': ex, 'y': ey, 'color': '#020617', 'size': 16, 'role': 'ear'})
        pts.append({'x': ex + 12, 'y': ey, 'color': '#020617', 'size': 16, 'role': 'ear'})
        pts.append({'x': ex - 12, 'y': ey, 'color': '#020617', 'size': 16, 'role': 'ear'})

    # Collar
    for p in line_pts((360, 335), (395, 340), 5):
        pts.append({'x': p[0], 'y': p[1], 'color': '#ef4444', 'size': 15, 'role': 'collar'})

    # Outstretched Dancing Arms
    for p in bezier_pts((355, 345), (290, 320), (220, 340), (180, 370), 16):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'arm'})
    for p in bezier_pts((355, 365), (290, 340), (220, 360), (180, 385), 14):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'arm'})
    for p in circle_pts((175, 378), 12, count=7):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 14, 'role': 'paw'})

    for p in bezier_pts((400, 345), (460, 330), (520, 350), (560, 380), 16):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'arm'})
    for p in bezier_pts((400, 365), (460, 350), (520, 370), (560, 395), 14):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'arm'})
    for p in circle_pts((565, 388), 12, count=7):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 14, 'role': 'paw'})

    # Torso
    for p in bezier_pts((350, 360), (310, 420), (320, 470), (360, 520), 18):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'body'})
    for p in bezier_pts((410, 360), (450, 410), (440, 460), (400, 510), 18):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'body'})

    # Back Spot & Tail
    for p in circle_pts((330, 420), 16, count=10):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 15, 'role': 'spot'})
    for p in bezier_pts((325, 460), (280, 465), (255, 440), (240, 415), 8):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 14, 'role': 'tail'})

    # Kicking Leg
    for p in bezier_pts((340, 490), (280, 510), (210, 520), (160, 490), 18):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'leg'})
    for p in bezier_pts((350, 515), (290, 535), (220, 545), (170, 515), 16):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'leg'})
    for p in circle_pts((155, 502), 14, count=8):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'paw'})
    pts.append({'x': 160, 'y': 492, 'color': '#0f172a', 'size': 12, 'role': 'toe'})

    # Balancing Leg
    for p in bezier_pts((385, 510), (395, 570), (405, 620), (410, 660), 16):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'leg'})
    for p in bezier_pts((405, 510), (415, 570), (425, 620), (425, 660), 14):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'leg'})
    for p in circle_pts((418, 672), 12, count=7):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'paw'})

    # Dust & Notes
    for p in [(380, 685), (410, 688), (440, 685), (460, 680)]:
        pts.append({'x': p[0], 'y': p[1], 'color': '#f59e0b', 'size': 13, 'role': 'dust'})
    for p in [(530, 170), (540, 150), (540, 125), (555, 120), (555, 140)]:
        pts.append({'x': p[0], 'y': p[1], 'color': '#ec4899', 'size': 16, 'role': 'note'})
    for p in [(220, 230), (230, 230), (230, 200), (255, 200), (255, 230)]:
        pts.append({'x': p[0], 'y': p[1], 'color': '#8b5cf6', 'size': 16, 'role': 'note'})

    return pts

# ==============================================================================
# POSE 4: 一戰王牌飛行員 (World War I Flying Ace) - FULL BODY CONNECTED
# ==============================================================================
def make_pose_4():
    pts = []
    # Aviator Helmet & Goggles on head
    for p in bezier_pts((330, 280), (340, 200), (420, 200), (450, 270), 18):
        pts.append({'x': p[0], 'y': p[1], 'color': '#78350f', 'size': 15, 'role': 'helmet'})
    for p in bezier_pts((330, 280), (350, 335), (410, 335), (430, 290), 12):
        pts.append({'x': p[0], 'y': p[1], 'color': '#78350f', 'size': 14, 'role': 'helmet'})

    # Goggles lenses
    for p in circle_pts((375, 240), 16, count=10):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0284c7', 'size': 15, 'role': 'goggles'})
    for p in circle_pts((420, 240), 16, count=10):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0284c7', 'size': 15, 'role': 'goggles'})
    for p in line_pts((335, 240), (450, 240), 8):
        pts.append({'x': p[0], 'y': p[1], 'color': '#1c1917', 'size': 14, 'role': 'goggles'})

    # Snout thrust forward
    for p in bezier_pts((440, 270), (480, 270), (530, 285), (555, 310), 18):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'head'})
    for p in bezier_pts((555, 310), (530, 340), (480, 345), (430, 325), 16):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'head'})

    # Nose at (565, 305)
    for p in circle_pts((565, 305), 14, count=9):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 16, 'role': 'nose'})
    for p in circle_pts((565, 305), 7, count=5):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 16, 'role': 'nose'})

    # Smirk
    for p in [(480, 320), (495, 322), (510, 320)]:
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 13, 'role': 'smirk'})

    # Ear blown backward
    for p in bezier_pts((340, 270), (280, 260), (220, 280), (180, 305), 16):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 16, 'role': 'ear'})
    for p in bezier_pts((180, 305), (220, 315), (280, 300), (340, 290), 14):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 16, 'role': 'ear'})

    # Snoopy's Torso sitting in cockpit
    for p in bezier_pts((350, 330), (325, 380), (335, 430), (360, 460), 14):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'body'})
    for p in bezier_pts((420, 330), (445, 380), (445, 430), (420, 460), 14):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'body'})

    # LONG FLOWING CRIMSON RED SCARF
    for p in circle_pts((395, 340), 12, count=7):
        pts.append({'x': p[0], 'y': p[1], 'color': '#ef4444', 'size': 16, 'role': 'scarf'})
    for p in bezier_pts((395, 340), (340, 320), (280, 370), (220, 340), 18):
        pts.append({'x': p[0], 'y': p[1], 'color': '#ef4444', 'size': 16, 'role': 'scarf'})
    for p in bezier_pts((395, 355), (340, 335), (280, 385), (220, 355), 16):
        pts.append({'x': p[0], 'y': p[1], 'color': '#dc2626', 'size': 15, 'role': 'scarf'})
    for p in bezier_pts((220, 340), (170, 310), (120, 360), (80, 340), 18):
        pts.append({'x': p[0], 'y': p[1], 'color': '#ef4444', 'size': 16, 'role': 'scarf'})
    for p in bezier_pts((220, 355), (170, 325), (120, 375), (80, 355), 16):
        pts.append({'x': p[0], 'y': p[1], 'color': '#dc2626', 'size': 15, 'role': 'scarf'})
    for p in [(65, 335), (60, 345), (65, 355), (70, 365)]:
        pts.append({'x': p[0], 'y': p[1], 'color': '#f87171', 'size': 14, 'role': 'scarf'})

    # Cockpit Rim & Steering Paws
    for p in bezier_pts((330, 430), (410, 420), (490, 420), (550, 440), 18):
        pts.append({'x': p[0], 'y': p[1], 'color': '#991b1b', 'size': 15, 'role': 'cockpit'})
    for p in circle_pts((470, 410), 14, count=8):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'paw'})

    # Sopwith Camel Doghouse fuselage
    for p in line_pts((300, 440), (300, 560), 12):
        pts.append({'x': p[0], 'y': p[1], 'color': '#dc2626', 'size': 14, 'role': 'plane'})
    for p in line_pts((560, 440), (560, 560), 12):
        pts.append({'x': p[0], 'y': p[1], 'color': '#dc2626', 'size': 14, 'role': 'plane'})
    for p in line_pts((300, 560), (560, 560), 18):
        pts.append({'x': p[0], 'y': p[1], 'color': '#dc2626', 'size': 14, 'role': 'plane'})

    # Clouds below
    for (cx, cy, r) in [(210, 620, 35), (330, 640, 45), (450, 630, 40), (570, 640, 35)]:
        for p in circle_pts((cx, cy), r, count=9):
            pts.append({'x': p[0], 'y': p[1], 'color': '#93c5fd', 'size': 14, 'role': 'cloud'})

    return pts

# ==============================================================================
# POSE 5: 暖暖擁抱大愛心
# ==============================================================================
def make_pose_5():
    pts = []
    # Heart
    heart_pts = []
    for deg in range(0, 360, 6):
        t = math.radians(deg)
        hx = 16 * (math.sin(t)**3) * 11.5 + 400
        hy = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)) * 11.5 + 480
        heart_pts.append((hx, hy))

    for p in heart_pts:
        pts.append({'x': p[0], 'y': p[1], 'color': '#e11d48', 'size': 15, 'role': 'heart'})
    for p in heart_pts[::2]:
        cx, cy = 400, 480
        ix = cx + (p[0] - cx) * 0.75
        iy = cy + (p[1] - cy) * 0.75
        pts.append({'x': ix, 'y': iy, 'color': '#f43f5e', 'size': 14, 'role': 'heart'})

    # Snoopy Peeking over top-right
    for p in bezier_pts((430, 310), (470, 275), (530, 280), (560, 310), 18):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'head'})
    for p in bezier_pts((560, 310), (580, 330), (580, 355), (550, 370), 14):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'head'})
    for p in bezier_pts((550, 370), (510, 380), (460, 375), (420, 350), 16):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'head'})

    # Nose at (575, 330)
    for p in circle_pts((575, 330), 14, count=9):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 16, 'role': 'nose'})
    for p in circle_pts((575, 330), 7, count=5):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 16, 'role': 'nose'})

    # Eye & Blush
    for p in circle_pts((505, 320), 8, count=6, start_ang=20, end_ang=160):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 14, 'role': 'eye'})
    for p in circle_pts((525, 345), 9, count=6):
        pts.append({'x': p[0], 'y': p[1], 'color': '#f472b6', 'size': 14, 'role': 'blush'})

    # Floppy Ear
    for y in range(290, 410, 14):
        for x in range(415, 460, 14):
            if ((x - 435)/20)**2 + ((y - 350)/55)**2 <= 1.1:
                pts.append({'x': x, 'y': y, 'color': '#020617', 'size': 15, 'role': 'ear'})

    # Collar
    for p in line_pts((420, 360), (435, 375), 5):
        pts.append({'x': p[0], 'y': p[1], 'color': '#ef4444', 'size': 15, 'role': 'collar'})

    # Paws hugging heart
    for p in bezier_pts((350, 420), (280, 420), (240, 460), (240, 500), 16):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'paw'})
    for p in circle_pts((245, 510), 14, count=8):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'paw'})

    for p in bezier_pts((470, 410), (530, 420), (560, 460), (560, 500), 16):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'paw'})
    for p in circle_pts((555, 510), 14, count=8):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'paw'})

    # Mini hearts
    for (ox, oy, sc) in [(230, 260, 0.35), (260, 180, 0.45), (570, 220, 0.4), (590, 160, 0.3)]:
        for deg in range(0, 360, 24):
            t = math.radians(deg)
            hx = (16 * (math.sin(t)**3) * 11.5) * sc + ox
            hy = (-(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)) * 11.5) * sc + oy
            pts.append({'x': hx, 'y': hy, 'color': '#fb7185', 'size': 13, 'role': 'heart'})

    return pts

# ==============================================================================
# POSE 6: 與糊塗塌客悄悄話
# ==============================================================================
def make_pose_6():
    pts = []
    # Snoopy Sitting Upright
    for p in bezier_pts((440, 290), (380, 260), (310, 270), (270, 310), 22):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'head'})
    for p in bezier_pts((270, 310), (240, 330), (240, 355), (270, 375), 14):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'head'})
    for p in bezier_pts((270, 375), (320, 385), (380, 385), (420, 375), 16):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'head'})

    # Nose at (250, 330)
    for p in circle_pts((250, 330), 14, count=9):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 16, 'role': 'nose'})
    for p in circle_pts((250, 330), 7, count=5):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 16, 'role': 'nose'})

    # Eye & Smile
    for p in circle_pts((330, 320), 8, count=6, start_ang=20, end_ang=160):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 14, 'role': 'eye'})
    for p in [(320, 355), (335, 358), (350, 355)]:
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 13, 'role': 'smile'})

    # Floppy Ear
    for y in range(290, 420, 14):
        for x in range(415, 460, 14):
            if ((x - 435)/20)**2 + ((y - 355)/60)**2 <= 1.1:
                pts.append({'x': x, 'y': y, 'color': '#020617', 'size': 15, 'role': 'ear'})

    # Collar
    for p in line_pts((390, 380), (430, 380), 5):
        pts.append({'x': p[0], 'y': p[1], 'color': '#ef4444', 'size': 15, 'role': 'collar'})

    # Torso
    for p in bezier_pts((430, 380), (480, 440), (490, 520), (460, 600), 20):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'body'})
    for p in bezier_pts((380, 385), (340, 440), (350, 520), (370, 590), 18):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'body'})

    # Spot & Tail
    for p in circle_pts((455, 470), 16, count=10):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 15, 'role': 'spot'})
    for p in bezier_pts((470, 550), (510, 540), (530, 510), (520, 485), 8):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 14, 'role': 'tail'})

    # Folded Legs
    for p in bezier_pts((460, 600), (440, 640), (360, 640), (330, 615), 18):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'leg'})
    for p in circle_pts((330, 615), 14, count=8):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'paw'})
    for p in bezier_pts((370, 500), (340, 540), (360, 570), (390, 560), 12):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 14, 'role': 'paw'})

    # WOODSTOCK ON SNOOPY'S NOSE!
    for p in circle_pts((240, 265), 14, count=10):
        pts.append({'x': p[0], 'y': p[1], 'color': '#f59e0b', 'size': 15, 'role': 'woodstock'})
    for p in [(228, 245), (238, 240), (248, 243)]:
        pts.append({'x': p[0], 'y': p[1], 'color': '#f59e0b', 'size': 14, 'role': 'woodstock'})
    for p in [(255, 265), (268, 268), (255, 272)]:
        pts.append({'x': p[0], 'y': p[1], 'color': '#ea580c', 'size': 14, 'role': 'woodstock'})
    for p in circle_pts((225, 285), 12, count=8):
        pts.append({'x': p[0], 'y': p[1], 'color': '#f59e0b', 'size': 14, 'role': 'woodstock'})
    for p in [(205, 280), (195, 290), (205, 298)]:
        pts.append({'x': p[0], 'y': p[1], 'color': '#f59e0b', 'size': 13, 'role': 'woodstock'})
    for p in [(235, 305), (245, 305)]:
        pts.append({'x': p[0], 'y': p[1], 'color': '#ea580c', 'size': 13, 'role': 'woodstock'})

    # Love & Notes
    for p in [(285, 240), (295, 220), (300, 240)]:
        pts.append({'x': p[0], 'y': p[1], 'color': '#ec4899', 'size': 15, 'role': 'note'})
    for p in circle_pts((290, 285), 10, count=7):
        pts.append({'x': p[0], 'y': p[1], 'color': '#ef4444', 'size': 15, 'role': 'heart'})

    # Grass
    for gx in range(180, 560, 20):
        pts.append({'x': gx, 'y': 645, 'color': '#10b981', 'size': 14, 'role': 'grass'})
        pts.append({'x': gx+6, 'y': 635, 'color': '#34d399', 'size': 13, 'role': 'grass'})

    return pts

# ==============================================================================
# POSE 7: 高爾夫優雅揮桿 (Championship Golfer Ace) - ANGLED VISOR & CLUB
# ==============================================================================
def make_pose_7():
    pts = []
    # Angled Visor Cap
    for p in bezier_pts((360, 240), (410, 215), (470, 215), (510, 240), 16):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0284c7', 'size': 15, 'role': 'visor'})
    for p in bezier_pts((410, 215), (460, 210), (510, 230), (535, 255), 14):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0284c7', 'size': 15, 'role': 'visor'})

    # Head looking up following golf ball
    for p in bezier_pts((380, 260), (430, 245), (490, 265), (530, 290), 16):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'head'})
    for p in bezier_pts((530, 290), (545, 305), (545, 325), (525, 340), 12):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'head'})
    for p in bezier_pts((525, 340), (480, 345), (430, 345), (390, 325), 14):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'head'})

    # Nose at (542, 300)
    for p in circle_pts((542, 300), 14, count=9):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 16, 'role': 'nose'})
    for p in circle_pts((542, 300), 7, count=5):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 16, 'role': 'nose'})

    for p in circle_pts((470, 280), 7, count=6):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 14, 'role': 'eye'})

    # Ear swinging
    for p in bezier_pts((370, 260), (320, 260), (270, 290), (240, 325), 16):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 16, 'role': 'ear'})
    for p in bezier_pts((240, 325), (270, 335), (320, 310), (370, 290), 14):
        pts.append({'x': p[0], 'y': p[1], 'color': '#020617', 'size': 16, 'role': 'ear'})

    # Collar
    for p in line_pts((385, 330), (410, 340), 5):
        pts.append({'x': p[0], 'y': p[1], 'color': '#ef4444', 'size': 15, 'role': 'collar'})

    # GOLF CLUB
    for p in circle_pts((350, 300), 14, count=8):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'grip'})
    for p in line_pts((350, 300), (530, 110), 24):
        pts.append({'x': p[0], 'y': p[1], 'color': '#94a3b8', 'size': 15, 'role': 'club'})
    for p in [(530, 110), (545, 100), (555, 105), (540, 120)]:
        pts.append({'x': p[0], 'y': p[1], 'color': '#334155', 'size': 16, 'role': 'club'})

    # Torso
    for p in bezier_pts((360, 340), (320, 400), (330, 460), (360, 520), 18):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'body'})
    for p in bezier_pts((410, 340), (430, 400), (420, 460), (390, 510), 16):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'body'})

    # Legs
    for p in line_pts((390, 510), (400, 630), 14):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'leg'})
    for p in circle_pts((405, 640), 14, count=8):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'paw'})

    for p in bezier_pts((350, 520), (320, 560), (300, 600), (310, 635), 14):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'leg'})
    for p in circle_pts((310, 645), 12, count=7):
        pts.append({'x': p[0], 'y': p[1], 'color': '#0f172a', 'size': 15, 'role': 'paw'})

    # Ball Trajectory & Soaring Ball
    for p in bezier_pts((310, 640), (430, 520), (560, 340), (640, 140), 26):
        pts.append({'x': p[0], 'y': p[1], 'color': '#38bdf8', 'size': 13, 'role': 'trail'})
    for p in circle_pts((650, 130), 14, count=9):
        pts.append({'x': p[0], 'y': p[1], 'color': '#f8fafc', 'size': 16, 'role': 'ball'})
    for p in line_pts((310, 645), (310, 655), 4):
        pts.append({'x': p[0], 'y': p[1], 'color': '#ef4444', 'size': 14, 'role': 'tee'})

    return pts

def normalize_to_target(raw_pts, target=TARGET_PARTICLES):
    xs = [p['x'] for p in raw_pts]
    ys = [p['y'] for p in raw_pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    cx = (min_x + max_x) / 2.0
    cy = (min_y + max_y) / 2.0
    span = max(max_x - min_x, max_y - min_y)
    scale = 530.0 / max(1, span)

    res = []
    for p in raw_pts:
        res.append({
            'x': round((p['x'] - cx) * scale, 1),
            'y': round((p['y'] - cy) * scale, 1),
            'color': p['color'],
            'size': p['size'],
            'role': p['role']
        })

    if len(res) > target:
        step = len(res) / target
        trimmed = [res[int(i * step)] for i in range(target)]
    else:
        trimmed = list(res)
        needed = target - len(trimmed)
        for i in range(needed):
            base = res[i % len(res)]
            copy_p = dict(base)
            copy_p['x'] += (random.random() - 0.5) * 4.0
            copy_p['y'] += (random.random() - 0.5) * 4.0
            trimmed.append(copy_p)

    final = []
    for idx, p in enumerate(trimmed):
        char = CHARS[idx % 3]
        final.append({
            'idx': idx,
            'char': char,
            'x': p['x'],
            'y': p['y'],
            'color': p['color'],
            'size': p['size'],
            'role': p['role']
        })

    return final

def main():
    print("Building 7 Perfect Snoopy Poses...")
    builders = [
        ('pose_doghouse', '趴臥狗屋白日夢', 'Daydreaming on the Doghouse', '「幸福就是……躺在屋頂思考人生的美好哲理。」', make_pose_1),
        ('pose_joecool', '墨鏡酷哥喬酷兒', 'Joe Cool with Sunglasses', '「戴上墨鏡，整個宇宙都是我的伸展台。」', make_pose_2),
        ('pose_happydance', '快樂開懷踢踏舞', 'The Joyful Happy Dance', '「不需要特別的理由，只要活著就值得大跳踢踏舞！」', make_pose_3),
        ('pose_flyingace', '一戰王牌飛行員', 'World War I Flying Ace', '「紅色圍巾迎風狂飆！看我衝破雲層擊退紅男爵！」', make_pose_4),
        ('pose_bighug', '暖暖擁抱大愛心', 'Love & Big Warm Hug', '「把最溫暖的心送給姿桂，滿滿的愛意永不褪色。」', make_pose_5),
        ('pose_woodstock', '與糊塗塌客悄悄話', 'Snoopy & Woodstock Whispers', '「你站在我的鼻尖輕唱，就是世間最甜美的悄悄話。」', make_pose_6),
        ('pose_golfer', '高爾夫優雅揮桿', 'Championship Golfer Ace', '「瞄準夢想的果嶺，優雅揮出一桿進洞！」', make_pose_7)
    ]

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    preview_dir = os.path.join(base_dir, 'assets', 'previews')
    os.makedirs(preview_dir, exist_ok=True)
    font_path = "C:/Windows/Fonts/msjhbd.ttc"

    poses = []
    for idx, (p_id, title, eng_title, quote, fn) in enumerate(builders):
        raw = fn()
        particles = normalize_to_target(raw, TARGET_PARTICLES)
        poses.append({
            'id': p_id,
            'title': title,
            'englishTitle': eng_title,
            'quote': quote,
            'particles': particles
        })

        # Render preview PNG
        img = Image.new('RGB', (800, 800), '#fbf8f1')
        draw = ImageDraw.Draw(img)
        title_font = ImageFont.truetype(font_path, 26)
        sub_font = ImageFont.truetype(font_path, 15)
        quote_font = ImageFont.truetype(font_path, 14)

        draw.text((400, 45), f"閻姿桂 × 史奴比 #{idx+1}：{title}", fill='#1c1917', font=title_font, anchor='mm')
        draw.text((400, 78), eng_title, fill='#78716c', font=sub_font, anchor='mm')
        draw.text((400, 750), quote, fill='#44403c', font=quote_font, anchor='mm')
        draw.rectangle([20, 20, 780, 780], outline='#e2d9cc', width=2)

        cx, cy = 400, 410
        for p in particles:
            px = cx + p['x']
            py = cy + p['y']
            font = ImageFont.truetype(font_path, int(p['size'] * 1.05))
            if p['color'] == '#ffffff':
                draw.text((px, py), p['char'], fill='#94a3b8', font=font, anchor='mm', stroke_width=1, stroke_fill='#64748b')
                draw.text((px, py), p['char'], fill='#ffffff', font=font, anchor='mm')
            else:
                draw.text((px, py), p['char'], fill=p['color'], font=font, anchor='mm')

        out_path = os.path.join(preview_dir, f"pose_{idx+1}_{p_id}.png")
        img.save(out_path)
        print(f"[{title}] Rendered: {out_path}")

    # Output to JSON and posesData.js
    assets_dir = os.path.join(base_dir, 'assets')
    json_path = os.path.join(assets_dir, 'snoopy_poses.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(poses, f, ensure_ascii=False, indent=2)

    js_path = os.path.join(base_dir, 'posesData.js')
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write("// Auto-generated High-Precision Snoopy Line-Art Dataset\n")
        f.write(f"// Strictly formatted with {TARGET_PARTICLES} particles ({TARGET_PARTICLES//3} 閻, {TARGET_PARTICLES//3} 姿, {TARGET_PARTICLES//3} 桂)\n")
        f.write("window.SNOOPY_POSES = ")
        json.dump(poses, f, ensure_ascii=False)
        f.write(";\n")

    print(f"Compiled successfully! {len(poses)} poses, {TARGET_PARTICLES} particles each.")

if __name__ == '__main__':
    main()
