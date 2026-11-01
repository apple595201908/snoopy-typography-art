"""
build_snoopy_dataset.py
Refined geometric model for Snoopy poses with minimum distance enforcement
and clean typographic spacing so every '閻', '姿', '桂' character is
clearly legible, vibrant, and perfectly assembled into Snoopy.
"""

import math
import random
import json
import os

TOTAL_PARTICLES = 420
CHARS = ['閻', '姿', '桂']

def bezier_cubic(p0, p1, p2, p3, steps=30):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts

def line_pts(p0, p1, steps=20):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = p0[0] + (p1[0] - p0[0]) * t
        y = p0[1] + (p1[1] - p0[1]) * t
        pts.append((x, y))
    return pts

def circle_pts(center, radius, count=20, start_angle=0, end_angle=360):
    pts = []
    span = end_angle - start_angle
    for i in range(count):
        deg = start_angle + (i / max(1, count - (1 if span < 360 else 0))) * span
        rad = math.radians(deg)
        x = center[0] + radius * math.cos(rad)
        y = center[1] + radius * math.sin(rad)
        pts.append((x, y))
    return pts

def relax_points(raw_list, min_dist=20.0):
    """Enforce minimum spacing between points while preserving highest priority features."""
    # Priority order for roles: features (nose, eye, glasses, woodstock) > contours > fills
    priority_map = {
        'nose': 10, 'eye': 10, 'sunglasses': 9, 'woodstock_beak': 9, 'mini_heart': 8,
        'love_heart': 8, 'woodstock_head': 8, 'ear': 7, 'collar': 7, 'paw': 6,
        'head': 6, 'scarf_knot': 6, 'visor_brim': 6, 'golf_ball': 6
    }
    
    # Sort by priority descending
    sorted_pts = sorted(raw_list, key=lambda p: priority_map.get(p.get('role', ''), 1), reverse=True)
    kept = []
    
    for p in sorted_pts:
        role = p.get('role', '')
        # Special smaller min_dist for dense details
        eff_min = min_dist * 0.7 if ('nose' in role or 'eye' in role or 'woodstock' in role) else min_dist
        
        collision = False
        for kp in kept:
            d = math.hypot(p['x'] - kp['x'], p['y'] - kp['y'])
            if d < eff_min:
                collision = True
                break
        if not collision:
            kept.append(p)
            
    return kept

def pad_or_trim(particles, target_count=TOTAL_PARTICLES, min_dist=18.0):
    """Bring particle count to exactly target_count."""
    filtered = relax_points(particles, min_dist=min_dist)
    
    if len(filtered) > target_count:
        # Uniform subsample
        step = len(filtered) / target_count
        res = [filtered[int(i * step)] for i in range(target_count)]
        return res
    elif len(filtered) < target_count:
        needed = target_count - len(filtered)
        res = list(filtered)
        # Select existing particles with largest local empty space to add child particles
        for i in range(needed):
            base_p = filtered[i % len(filtered)]
            ang = random.uniform(0, math.pi * 2)
            dist = random.uniform(8, 16)
            new_p = dict(base_p)
            new_p['x'] += math.cos(ang) * dist
            new_p['y'] += math.sin(ang) * dist
            res.append(new_p)
        return res
    return filtered

def finalize_pose(raw_pts, min_dist=18.0):
    pts = pad_or_trim(raw_pts, TOTAL_PARTICLES, min_dist=min_dist)
    final_list = []
    for idx, p in enumerate(pts):
        char = CHARS[idx % 3]
        final_list.append({
            'idx': idx,
            'char': char,
            'x': round(p['x'], 1),
            'y': round(p['y'], 1),
            'role': p.get('role', 'body'),
            'color': p.get('color', '#1e293b'),
            'size': p.get('size', 18)
        })
    return final_list

# ==========================================
# POSE 1: Daydreaming on Doghouse (趴臥狗屋白日夢)
# ==========================================
def build_pose_1():
    raw = []
    # Doghouse Roof: Peak at (0, 20), left (-180, 85), right (180, 85)
    for p in line_pts((-180, 85), (0, 20), 22):
        raw.append({'x': p[0], 'y': p[1], 'role': 'roof', 'color': '#ef4444', 'size': 19})
    for p in line_pts((0, 20), (180, 85), 22):
        raw.append({'x': p[0], 'y': p[1], 'role': 'roof', 'color': '#ef4444', 'size': 19})
    # Roof thickness & crossbeam
    for p in line_pts((-170, 98), (170, 98), 24):
        raw.append({'x': p[0], 'y': p[1], 'role': 'roof_beam', 'color': '#dc2626', 'size': 18})
    for p in line_pts((-150, 112), (150, 112), 20):
        raw.append({'x': p[0], 'y': p[1], 'role': 'roof_beam', 'color': '#b91c1c', 'size': 17})

    # Doghouse Body Wall & Door
    for x in range(-130, 140, 32):
        for y in range(125, 235, 30):
            if abs(x) < 45 and y > 155:
                continue
            raw.append({'x': x, 'y': y, 'role': 'house_wall', 'color': '#991b1b', 'size': 17})
    # Door Arch (Black)
    for p in circle_pts((0, 165), 42, count=12, start_angle=180, end_angle=360):
        raw.append({'x': p[0], 'y': p[1], 'role': 'door', 'color': '#1c1917', 'size': 19})
    for y in range(175, 235, 25):
        for dx in [-28, 0, 28]:
            raw.append({'x': dx, 'y': y, 'role': 'door_fill', 'color': '#1c1917', 'size': 18})

    # Snoopy lying horizontally on roof ridge
    # Back arch
    for p in bezier_cubic((-120, -5), (-70, -38), (0, -38), (55, -20), 20):
        raw.append({'x': p[0], 'y': p[1], 'role': 'body_outline', 'color': '#0f172a', 'size': 19})
    # Head & Snout (pointing right)
    for p in bezier_cubic((55, -20), (90, -35), (145, -30), (160, -10), 18):
        raw.append({'x': p[0], 'y': p[1], 'role': 'head', 'color': '#0f172a', 'size': 19})
    # Black Nose
    raw.append({'x': 166, 'y': -10, 'role': 'nose', 'color': '#020617', 'size': 24})
    raw.append({'x': 163, 'y': -16, 'role': 'nose', 'color': '#020617', 'size': 20})
    raw.append({'x': 163, 'y': -4, 'role': 'nose', 'color': '#020617', 'size': 20})
    # Jaw / Under snout
    for p in bezier_cubic((158, 2), (135, 12), (95, 10), (65, 0), 14):
        raw.append({'x': p[0], 'y': p[1], 'role': 'chin', 'color': '#0f172a', 'size': 18})
    # Sleeping smiling eye
    raw.append({'x': 105, 'y': -16, 'role': 'eye', 'color': '#0f172a', 'size': 18})
    raw.append({'x': 113, 'y': -14, 'role': 'eye', 'color': '#0f172a', 'size': 18})
    # Floppy ear (Draped over roof)
    for ex in range(45, 80, 14):
        for ey in range(-25, 25, 15):
            raw.append({'x': ex, 'y': ey, 'role': 'ear', 'color': '#020617', 'size': 20})
    # Red Collar
    raw.append({'x': 52, 'y': -10, 'role': 'collar', 'color': '#ef4444', 'size': 19})
    raw.append({'x': 56, 'y': 2, 'role': 'collar', 'color': '#ef4444', 'size': 19})
    # Spot on back
    raw.append({'x': -40, 'y': -18, 'role': 'spot', 'color': '#020617', 'size': 20})
    raw.append({'x': -26, 'y': -18, 'role': 'spot', 'color': '#020617', 'size': 20})
    raw.append({'x': -33, 'y': -10, 'role': 'spot', 'color': '#020617', 'size': 20})
    # Tail
    raw.append({'x': -132, 'y': -14, 'role': 'tail', 'color': '#0f172a', 'size': 18})
    raw.append({'x': -144, 'y': -24, 'role': 'tail', 'color': '#0f172a', 'size': 18})
    # Front paws resting forward
    for p in [ (75, 18), (92, 20), (110, 18) ]:
        raw.append({'x': p[0], 'y': p[1], 'role': 'paw', 'color': '#0f172a', 'size': 18})
    # Back legs dangling left
    for p in [ (-115, 10), (-120, 26), (-95, 12), (-100, 28) ]:
        raw.append({'x': p[0], 'y': p[1], 'role': 'leg', 'color': '#0f172a', 'size': 18})
    # White body fill
    for bx in range(-90, 45, 24):
        for by in range(-22, 6, 16):
            raw.append({'x': bx, 'y': by, 'role': 'body_fill', 'color': '#ffffff', 'size': 18})

    # Woodstock perched on left
    woodstock_pts = [
        (-148, -48), (-140, -56), (-132, -54), (-126, -46), # head & tuft
        (-118, -46), # beak
        (-138, -36), (-130, -34), (-144, -30), # body & tail
        (-134, -24), (-128, -24) # feet
    ]
    for p in woodstock_pts:
        raw.append({'x': p[0], 'y': p[1], 'role': 'woodstock', 'color': '#f59e0b', 'size': 18})

    # Thought bubbles "Zzz"
    for cx, cy, r in [ (130, -55, 12), (160, -90, 18), (195, -135, 24), (230, -180, 28) ]:
        for p in circle_pts((cx, cy), r, count=7):
            raw.append({'x': p[0], 'y': p[1], 'role': 'bubble', 'color': '#38bdf8', 'size': 17})

    return finalize_pose(raw, min_dist=20.0)

# ==========================================
# POSE 2: Joe Cool with Sunglasses (墨鏡酷哥喬酷兒)
# ==========================================
def build_pose_2():
    raw = []
    # Wall column on right
    for y in range(-200, 230, 30):
        raw.append({'x': 140, 'y': y, 'role': 'wall', 'color': '#94a3b8', 'size': 18})
        raw.append({'x': 170, 'y': y, 'role': 'wall', 'color': '#cbd5e1', 'size': 18})

    # Snoopy Head (Snout pointing left)
    for p in bezier_cubic((10, -155), (-40, -170), (-115, -145), (-150, -110), 18):
        raw.append({'x': p[0], 'y': p[1], 'role': 'head', 'color': '#0f172a', 'size': 19})
    # Black Nose at tip
    raw.append({'x': -158, 'y': -110, 'role': 'nose', 'color': '#020617', 'size': 24})
    raw.append({'x': -155, 'y': -118, 'role': 'nose', 'color': '#020617', 'size': 20})
    raw.append({'x': -155, 'y': -102, 'role': 'nose', 'color': '#020617', 'size': 20})
    # Chin & Smirk
    for p in bezier_cubic((-145, -95), (-120, -75), (-55, -70), (-15, -85), 16):
        raw.append({'x': p[0], 'y': p[1], 'role': 'jaw', 'color': '#0f172a', 'size': 18})
    # Smirk upturn
    raw.append({'x': -75, 'y': -76, 'role': 'smirk', 'color': '#0f172a', 'size': 18})
    raw.append({'x': -60, 'y': -80, 'role': 'smirk', 'color': '#0f172a', 'size': 18})

    # SLEEK SUNGLASSES (Dark double lens & frame)
    # Left lens
    for sx in range(-125, -75, 15):
        for sy in range(-125, -95, 14):
            raw.append({'x': sx, 'y': sy, 'role': 'sunglasses', 'color': '#020617', 'size': 20})
    # Right lens & bridge
    for sx in range(-70, -25, 15):
        for sy in range(-125, -95, 14):
            raw.append({'x': sx, 'y': sy, 'role': 'sunglasses', 'color': '#020617', 'size': 20})
    # Sunglasses temples to ear
    for p in line_pts((-25, -112), (25, -115), 5):
        raw.append({'x': p[0], 'y': p[1], 'role': 'sunglasses_frame', 'color': '#0f172a', 'size': 18})

    # Floppy ear hanging down behind head
    for ex in range(20, 60, 14):
        for ey in range(-130, -35, 16):
            raw.append({'x': ex, 'y': ey, 'role': 'ear', 'color': '#020617', 'size': 20})

    # RED COLLEGE SWEATER ("JOE COOL")
    for p in line_pts((-25, -85), (20, -85), 5):
        raw.append({'x': p[0], 'y': p[1], 'role': 'collar', 'color': '#ef4444', 'size': 18})
    for sx in range(-55, 55, 20):
        for sy in range(-75, 45, 20):
            raw.append({'x': sx, 'y': sy, 'role': 'sweater', 'color': '#ef4444', 'size': 18})
    # Arms crossed / tucked
    for p in bezier_cubic((-55, -45), (-85, -10), (-60, 25), (-25, 15), 14):
        raw.append({'x': p[0], 'y': p[1], 'role': 'arm', 'color': '#dc2626', 'size': 18})
    for p in bezier_cubic((35, -45), (65, -10), (45, 25), (10, 15), 14):
        raw.append({'x': p[0], 'y': p[1], 'role': 'arm', 'color': '#dc2626', 'size': 18})

    # Legs & Cool leaning posture
    # Left leg straight down
    for p in line_pts((-30, 45), (-35, 160), 10):
        raw.append({'x': p[0], 'y': p[1], 'role': 'leg', 'color': '#0f172a', 'size': 18})
    raw.append({'x': -48, 'y': 170, 'role': 'shoe', 'color': '#0f172a', 'size': 20})
    raw.append({'x': -32, 'y': 172, 'role': 'shoe', 'color': '#0f172a', 'size': 20})
    # Right leg crossed over
    for p in bezier_cubic((15, 45), (35, 100), (0, 140), (-15, 165), 12):
        raw.append({'x': p[0], 'y': p[1], 'role': 'leg_crossed', 'color': '#0f172a', 'size': 18})
    raw.append({'x': -15, 'y': 175, 'role': 'shoe', 'color': '#0f172a', 'size': 20})
    # Tail wagging
    for p in bezier_cubic((50, 25), (75, 15), (90, -5), (85, -20), 6):
        raw.append({'x': p[0], 'y': p[1], 'role': 'tail', 'color': '#0f172a', 'size': 18})

    # Sparkle stars
    for (sx, sy) in [(-175, -155), (-165, 10), (95, -145)]:
        for p in [(sx, sy), (sx-14, sy), (sx+14, sy), (sx, sy-14), (sx, sy+14)]:
            raw.append({'x': p[0], 'y': p[1], 'role': 'sparkle', 'color': '#f59e0b', 'size': 18})

    return finalize_pose(raw, min_dist=20.0)

# ==========================================
# POSE 3: The Happy Dance (踢踏舞快樂大歡呼)
# ==========================================
def build_pose_3():
    raw = []
    # Both ears flying high up in kinetic joy!
    # Left ear
    for p in bezier_cubic((-10, -115), (-50, -175), (-80, -215), (-95, -245), 18):
        raw.append({'x': p[0], 'y': p[1], 'role': 'ear_left', 'color': '#020617', 'size': 20})
    for p in bezier_cubic((-95, -245), (-65, -215), (-35, -155), (5, -110), 16):
        raw.append({'x': p[0], 'y': p[1], 'role': 'ear_left', 'color': '#020617', 'size': 20})
    # Right ear
    for p in bezier_cubic((10, -110), (45, -165), (75, -205), (90, -240), 18):
        raw.append({'x': p[0], 'y': p[1], 'role': 'ear_right', 'color': '#020617', 'size': 20})
    for p in bezier_cubic((90, -240), (65, -195), (35, -145), (15, -105), 16):
        raw.append({'x': p[0], 'y': p[1], 'role': 'ear_right', 'color': '#020617', 'size': 20})

    # Head thrown back laughing
    for p in bezier_cubic((-15, -120), (20, -150), (65, -170), (85, -160), 16):
        raw.append({'x': p[0], 'y': p[1], 'role': 'head', 'color': '#0f172a', 'size': 19})
    # Black Nose
    raw.append({'x': 92, 'y': -160, 'role': 'nose', 'color': '#020617', 'size': 24})
    # Wide open mouth / jaw
    for p in bezier_cubic((82, -150), (60, -115), (15, -90), (-10, -80), 18):
        raw.append({'x': p[0], 'y': p[1], 'role': 'jaw', 'color': '#0f172a', 'size': 19})
    # Tongue inside open mouth
    raw.append({'x': 45, 'y': -118, 'role': 'mouth_open', 'color': '#f43f5e', 'size': 18})
    raw.append({'x': 55, 'y': -125, 'role': 'mouth_open', 'color': '#f43f5e', 'size': 18})
    # Laughing closed eyes `^`
    raw.append({'x': 10, 'y': -138, 'role': 'eye', 'color': '#0f172a', 'size': 18})
    raw.append({'x': 25, 'y': -142, 'role': 'eye', 'color': '#0f172a', 'size': 18})
    raw.append({'x': 40, 'y': -135, 'role': 'eye', 'color': '#0f172a', 'size': 18})
    # Head fill
    for hx in range(5, 55, 18):
        for hy in range(-140, -105, 16):
            raw.append({'x': hx, 'y': hy, 'role': 'head_fill', 'color': '#ffffff', 'size': 18})

    # Flung Arms & Torso
    raw.append({'x': 2, 'y': -75, 'role': 'collar', 'color': '#ef4444', 'size': 19})
    # Left Arm outstretched
    for p in bezier_cubic((-15, -65), (-65, -90), (-115, -80), (-140, -55), 16):
        raw.append({'x': p[0], 'y': p[1], 'role': 'arm_left', 'color': '#0f172a', 'size': 18})
    # Right Arm outstretched
    for p in bezier_cubic((20, -60), (70, -75), (110, -60), (135, -35), 16):
        raw.append({'x': p[0], 'y': p[1], 'role': 'arm_right', 'color': '#0f172a', 'size': 18})
    # Torso
    for p in bezier_cubic((-25, -60), (-45, 0), (-35, 40), (-15, 60), 14):
        raw.append({'x': p[0], 'y': p[1], 'role': 'body_back', 'color': '#0f172a', 'size': 18})
    for p in bezier_cubic((25, -55), (45, -10), (35, 30), (10, 55), 14):
        raw.append({'x': p[0], 'y': p[1], 'role': 'body_front', 'color': '#0f172a', 'size': 18})
    for bx in range(-15, 20, 16):
        for by in range(-45, 45, 18):
            raw.append({'x': bx, 'y': by, 'role': 'body_fill', 'color': '#ffffff', 'size': 18})
    # Back patch & tail
    raw.append({'x': -30, 'y': -5, 'role': 'spot', 'color': '#020617', 'size': 20})
    raw.append({'x': -75, 'y': 15, 'role': 'tail', 'color': '#0f172a', 'size': 18})
    raw.append({'x': -88, 'y': 0, 'role': 'tail', 'color': '#0f172a', 'size': 18})

    # High kicking leg & standing balancing leg
    for p in bezier_cubic((-20, 50), (-60, 65), (-110, 75), (-145, 55), 16):
        raw.append({'x': p[0], 'y': p[1], 'role': 'kick_leg', 'color': '#0f172a', 'size': 19})
    raw.append({'x': -155, 'y': 52, 'role': 'paw_kick', 'color': '#0f172a', 'size': 20})
    # Standing balancing leg on tiptoe
    for p in bezier_cubic((10, 50), (15, 100), (20, 140), (22, 175), 14):
        raw.append({'x': p[0], 'y': p[1], 'role': 'standing_leg', 'color': '#0f172a', 'size': 19})
    raw.append({'x': 24, 'y': 185, 'role': 'tiptoe', 'color': '#0f172a', 'size': 20})

    # Musical Notes (♪, ♫) floating
    for p in [(115, -110), (120, -125), (120, -142), (132, -145), (135, -132)]:
        raw.append({'x': p[0], 'y': p[1], 'role': 'note', 'color': '#ec4899', 'size': 19})
    for p in [(-145, -120), (-140, -120), (-140, -142), (-120, -142), (-120, -120)]:
        raw.append({'x': p[0], 'y': p[1], 'role': 'note', 'color': '#8b5cf6', 'size': 19})
    for p in [(-25, 195), (0, 195), (25, 195), (50, 195)]:
        raw.append({'x': p[0], 'y': p[1], 'role': 'dust', 'color': '#f59e0b', 'size': 17})

    return finalize_pose(raw, min_dist=20.0)

# ==========================================
# POSE 4: World War I Flying Ace (一戰王牌飛行員)
# ==========================================
def build_pose_4():
    raw = []
    # Aviator helmet & goggles
    for p in bezier_cubic((-50, -110), (-40, -170), (20, -170), (45, -120), 18):
        raw.append({'x': p[0], 'y': p[1], 'role': 'aviator_cap', 'color': '#78350f', 'size': 19})
    # Goggles lenses (double round rims on forehead)
    for p in circle_pts((-15, -135), 14, count=10):
        raw.append({'x': p[0], 'y': p[1], 'role': 'goggles_left', 'color': '#0284c7', 'size': 18})
    for p in circle_pts((22, -135), 14, count=10):
        raw.append({'x': p[0], 'y': p[1], 'role': 'goggles_right', 'color': '#0284c7', 'size': 18})

    # Snout thrust forward
    for p in bezier_cubic((30, -115), (75, -125), (120, -115), (135, -95), 16):
        raw.append({'x': p[0], 'y': p[1], 'role': 'snout', 'color': '#0f172a', 'size': 19})
    # Nose (Black tip)
    raw.append({'x': 142, 'y': -95, 'role': 'nose', 'color': '#020617', 'size': 24})
    # Jaw
    for p in bezier_cubic((130, -85), (105, -70), (70, -70), (45, -80), 14):
        raw.append({'x': p[0], 'y': p[1], 'role': 'jaw', 'color': '#0f172a', 'size': 18})

    # Ear blown backward by 100mph wind
    for p in bezier_cubic((-35, -115), (-85, -120), (-135, -105), (-165, -90), 16):
        raw.append({'x': p[0], 'y': p[1], 'role': 'ear_wind', 'color': '#020617', 'size': 20})
    for p in bezier_cubic((-165, -90), (-135, -80), (-85, -90), (-35, -95), 14):
        raw.append({'x': p[0], 'y': p[1], 'role': 'ear_wind', 'color': '#020617', 'size': 20})

    # LONG FLOWING RED SCARF (Waving furiously in propeller wind)
    # Wave 1
    for p in bezier_cubic((0, -60), (-45, -75), (-85, -45), (-125, -70), 18):
        raw.append({'x': p[0], 'y': p[1], 'role': 'scarf', 'color': '#ef4444', 'size': 19})
    for p in bezier_cubic((0, -48), (-45, -63), (-85, -33), (-125, -58), 16):
        raw.append({'x': p[0], 'y': p[1], 'role': 'scarf', 'color': '#dc2626', 'size': 19})
    # Wave 2
    for p in bezier_cubic((-125, -70), (-165, -90), (-205, -65), (-235, -80), 18):
        raw.append({'x': p[0], 'y': p[1], 'role': 'scarf', 'color': '#ef4444', 'size': 19})
    for p in bezier_cubic((-125, -58), (-165, -78), (-205, -53), (-235, -68), 16):
        raw.append({'x': p[0], 'y': p[1], 'role': 'scarf', 'color': '#dc2626', 'size': 19})
    # Scarf tassels
    for p in [(-244, -85), (-248, -74), (-244, -62)]:
        raw.append({'x': p[0], 'y': p[1], 'role': 'scarf_fringe', 'color': '#f87171', 'size': 18})

    # Cockpit rim & Paws
    for p in circle_pts((55, -25), 12, count=8):
        raw.append({'x': p[0], 'y': p[1], 'role': 'paw_pilot', 'color': '#0f172a', 'size': 19})
    for p in bezier_cubic((-20, -10), (30, -15), (80, -15), (130, 0), 16):
        raw.append({'x': p[0], 'y': p[1], 'role': 'cockpit_edge', 'color': '#991b1b', 'size': 19})
    # Sopwith Camel Red fuselage
    for x in range(-50, 130, 26):
        for y in range(15, 110, 26):
            raw.append({'x': x, 'y': y, 'role': 'plane_body', 'color': '#dc2626', 'size': 18})
    # Clouds drifting below
    for c_pt, r in [((-110, 160), 28), ((-40, 175), 36), ((50, 165), 32), ((120, 175), 28)]:
        for p in circle_pts(c_pt, r, count=7):
            raw.append({'x': p[0], 'y': p[1], 'role': 'sky_cloud', 'color': '#93c5fd', 'size': 17})

    return finalize_pose(raw, min_dist=20.0)

# ==========================================
# POSE 5: Love & Hugs (雙手擁抱大愛心)
# ==========================================
def build_pose_5():
    raw = []
    # Parametric heart shape
    heart_pts = []
    for deg in range(0, 360, 5):
        t = math.radians(deg)
        hx = 16 * (math.sin(t)**3) * 8.6
        hy = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)) * 8.6 + 30
        heart_pts.append((hx, hy))

    # Heart perimeter
    for p in heart_pts[::2]:
        raw.append({'x': p[0], 'y': p[1], 'role': 'heart_border', 'color': '#e11d48', 'size': 19})
    # Heart interior fill
    for scale in [0.75, 0.5, 0.25]:
        for p in heart_pts[::4]:
            raw.append({'x': p[0] * scale, 'y': (p[1] - 30) * scale + 30, 'role': 'heart_fill', 'color': '#f43f5e', 'size': 18})

    # Snoopy peeking over top-right of heart
    for p in bezier_cubic((10, -110), (45, -135), (95, -125), (115, -100), 16):
        raw.append({'x': p[0], 'y': p[1], 'role': 'head', 'color': '#0f172a', 'size': 19})
    # Nose
    raw.append({'x': 122, 'y': -100, 'role': 'nose', 'color': '#020617', 'size': 24})
    # Jaw
    for p in bezier_cubic((112, -92), (90, -75), (55, -75), (30, -85), 14):
        raw.append({'x': p[0], 'y': p[1], 'role': 'jaw', 'color': '#0f172a', 'size': 18})
    # Peaceful sleeping eye & blushing cheek
    raw.append({'x': 65, 'y': -110, 'role': 'eye', 'color': '#0f172a', 'size': 18})
    raw.append({'x': 75, 'y': -108, 'role': 'eye', 'color': '#0f172a', 'size': 18})
    raw.append({'x': 86, 'y': -95, 'role': 'blush', 'color': '#f472b6', 'size': 18})
    # Ear hanging down
    for ex in range(45, 80, 14):
        for ey in range(-120, -45, 18):
            raw.append({'x': ex, 'y': ey, 'role': 'ear', 'color': '#020617', 'size': 20})
    # Collar
    raw.append({'x': 22, 'y': -75, 'role': 'collar', 'color': '#ef4444', 'size': 18})
    raw.append({'x': 28, 'y': -65, 'role': 'collar', 'color': '#ef4444', 'size': 18})

    # Paws hugging sides of heart
    # Left paw
    for p in bezier_cubic((-25, -35), (-70, -45), (-110, -15), (-115, 25), 16):
        raw.append({'x': p[0], 'y': p[1], 'role': 'hug_paw_left', 'color': '#0f172a', 'size': 19})
    raw.append({'x': -112, 'y': 35, 'role': 'hug_paw_left', 'color': '#0f172a', 'size': 20})
    # Right paw
    for p in bezier_cubic((25, -35), (70, -40), (105, -10), (110, 30), 16):
        raw.append({'x': p[0], 'y': p[1], 'role': 'hug_paw_right', 'color': '#0f172a', 'size': 19})
    raw.append({'x': 108, 'y': 40, 'role': 'hug_paw_right', 'color': '#0f172a', 'size': 20})

    # Floating mini hearts
    for (ox, oy), sc in [((-130, -110), 0.35), ((-100, -170), 0.5), ((130, -150), 0.4), ((140, -80), 0.3)]:
        for p in heart_pts[::10]:
            raw.append({'x': p[0] * sc + ox, 'y': p[1] * sc + oy, 'role': 'mini_heart', 'color': '#fb7185', 'size': 16})

    return finalize_pose(raw, min_dist=20.0)

# ==========================================
# POSE 6: Woodstock Friendship (與糊塗塌客鼻尖對視)
# ==========================================
def build_pose_6():
    raw = []
    # Snoopy Sitting Upright
    for p in bezier_cubic((0, -115), (-45, -125), (-95, -110), (-125, -85), 18):
        raw.append({'x': p[0], 'y': p[1], 'role': 'head', 'color': '#0f172a', 'size': 19})
    # Nose (Woodstock balances here!)
    raw.append({'x': -132, 'y': -85, 'role': 'nose', 'color': '#020617', 'size': 24})
    # Jaw
    for p in bezier_cubic((-122, -75), (-95, -55), (-45, -55), (-10, -70), 16):
        raw.append({'x': p[0], 'y': p[1], 'role': 'jaw', 'color': '#0f172a', 'size': 18})
    # Loving eye looking down at nose
    raw.append({'x': -58, 'y': -90, 'role': 'tender_eye', 'color': '#0f172a', 'size': 18})
    # Ear hanging down back
    for ex in range(10, 48, 14):
        for ey in range(-115, -25, 18):
            raw.append({'x': ex, 'y': ey, 'role': 'ear', 'color': '#020617', 'size': 20})
    # Collar
    raw.append({'x': -10, 'y': -65, 'role': 'collar', 'color': '#ef4444', 'size': 18})
    raw.append({'x': 10, 'y': -65, 'role': 'collar', 'color': '#ef4444', 'size': 18})
    # Sitting Torso
    for p in bezier_cubic((10, -50), (45, 20), (50, 80), (35, 140), 16):
        raw.append({'x': p[0], 'y': p[1], 'role': 'back', 'color': '#0f172a', 'size': 18})
    for p in bezier_cubic((-20, -50), (-35, 10), (-30, 60), (-15, 110), 14):
        raw.append({'x': p[0], 'y': p[1], 'role': 'chest', 'color': '#0f172a', 'size': 18})
    for bx in range(-20, 30, 18):
        for by in range(-40, 110, 22):
            raw.append({'x': bx, 'y': by, 'role': 'body_fill', 'color': '#ffffff', 'size': 17})
    # Folded hind leg & paw
    for p in bezier_cubic((35, 140), (20, 175), (-30, 175), (-50, 160), 14):
        raw.append({'x': p[0], 'y': p[1], 'role': 'hind_leg', 'color': '#0f172a', 'size': 19})
    for p in bezier_cubic((-15, 110), (-25, 145), (-40, 160), (-60, 165), 12):
        raw.append({'x': p[0], 'y': p[1], 'role': 'front_paw', 'color': '#0f172a', 'size': 19})
    # Tail & Spot
    raw.append({'x': 75, 'y': 95, 'role': 'tail', 'color': '#0f172a', 'size': 18})
    raw.append({'x': 26, 'y': 25, 'role': 'spot', 'color': '#020617', 'size': 20})

    # Woodstock perched on Snoopy's nose!
    for p in circle_pts((-135, -125), 14, count=12):
        raw.append({'x': p[0], 'y': p[1], 'role': 'woodstock_head', 'color': '#fbbf24', 'size': 18})
    # Spiky crest
    for p in [(-142, -145), (-135, -150), (-128, -148)]:
        raw.append({'x': p[0], 'y': p[1], 'role': 'woodstock_crest', 'color': '#f59e0b', 'size': 17})
    # Beak singing to Snoopy
    raw.append({'x': -116, 'y': -122, 'role': 'woodstock_beak', 'color': '#ea580c', 'size': 18})
    # Body & fluttering wings
    for p in circle_pts((-145, -110), 12, count=9):
        raw.append({'x': p[0], 'y': p[1], 'role': 'woodstock_body', 'color': '#fbbf24', 'size': 18})
    for p in [(-165, -115), (-172, -105), (-160, -98)]:
        raw.append({'x': p[0], 'y': p[1], 'role': 'woodstock_wing', 'color': '#f59e0b', 'size': 17})
    # Bird feet on nose
    raw.append({'x': -134, 'y': -94, 'role': 'woodstock_feet', 'color': '#ea580c', 'size': 17})

    # Musical chirp & red love heart
    for p in [(-95, -150), (-85, -162), (-75, -155)]:
        raw.append({'x': p[0], 'y': p[1], 'role': 'chirp', 'color': '#ec4899', 'size': 18})
    raw.append({'x': -95, 'y': -108, 'role': 'love_heart', 'color': '#ef4444', 'size': 20})

    # Green Grass ground
    for gx in range(-150, 150, 24):
        raw.append({'x': gx, 'y': 178, 'role': 'grass', 'color': '#10b981', 'size': 17})

    return finalize_pose(raw, min_dist=20.0)

# ==========================================
# POSE 7: Championship Golfer (高爾夫優雅揮桿出擊)
# ==========================================
def build_pose_7():
    raw = []
    # Visor cap
    for p in bezier_cubic((-20, -135), (20, -145), (65, -140), (85, -130), 16):
        raw.append({'x': p[0], 'y': p[1], 'role': 'visor_brim', 'color': '#0284c7', 'size': 18})
    for p in bezier_cubic((-25, -130), (0, -155), (35, -155), (55, -135), 14):
        raw.append({'x': p[0], 'y': p[1], 'role': 'visor_crown', 'color': '#0284c7', 'size': 18})
    # Snout looking up toward sky
    for p in bezier_cubic((30, -125), (65, -135), (105, -120), (120, -100), 16):
        raw.append({'x': p[0], 'y': p[1], 'role': 'snout', 'color': '#0f172a', 'size': 19})
    # Nose
    raw.append({'x': 128, 'y': -100, 'role': 'nose', 'color': '#020617', 'size': 24})
    # Jaw
    for p in bezier_cubic((115, -92), (90, -75), (55, -75), (30, -85), 14):
        raw.append({'x': p[0], 'y': p[1], 'role': 'jaw', 'color': '#0f172a', 'size': 18})
    # Eye looking up at the ball
    raw.append({'x': 70, 'y': -108, 'role': 'eye', 'color': '#0f172a', 'size': 18})
    # Ear swinging
    for p in bezier_cubic((-10, -115), (-45, -125), (-80, -100), (-100, -75), 14):
        raw.append({'x': p[0], 'y': p[1], 'role': 'ear_swing', 'color': '#020617', 'size': 20})
    for p in bezier_cubic((-100, -75), (-75, -65), (-40, -80), (-5, -95), 12):
        raw.append({'x': p[0], 'y': p[1], 'role': 'ear_swing', 'color': '#020617', 'size': 20})

    # Golf Club Shaft & Head
    raw.append({'x': -35, 'y': -100, 'role': 'golf_grip', 'color': '#0f172a', 'size': 20})
    for p in line_pts((-35, -100), (95, -220), 22):
        raw.append({'x': p[0], 'y': p[1], 'role': 'club_shaft', 'color': '#94a3b8', 'size': 18})
    raw.append({'x': 105, 'y': -225, 'role': 'club_head', 'color': '#334155', 'size': 22})

    # Collar & Torso
    raw.append({'x': 20, 'y': -65, 'role': 'collar', 'color': '#ef4444', 'size': 18})
    for p in bezier_cubic((-10, -65), (-35, -10), (-30, 40), (-15, 80), 16):
        raw.append({'x': p[0], 'y': p[1], 'role': 'torso_back', 'color': '#0f172a', 'size': 18})
    for p in bezier_cubic((25, -60), (45, -10), (35, 40), (10, 80), 16):
        raw.append({'x': p[0], 'y': p[1], 'role': 'torso_front', 'color': '#0f172a', 'size': 18})
    # Planted left foot
    for p in line_pts((10, 80), (15, 170), 12):
        raw.append({'x': p[0], 'y': p[1], 'role': 'leg_planted', 'color': '#0f172a', 'size': 19})
    raw.append({'x': 20, 'y': 178, 'role': 'shoe', 'color': '#0f172a', 'size': 20})
    # Right foot on toe
    for p in bezier_cubic((-15, 80), (-35, 120), (-50, 150), (-45, 175), 14):
        raw.append({'x': p[0], 'y': p[1], 'role': 'leg_finish', 'color': '#0f172a', 'size': 19})
    raw.append({'x': -45, 'y': 182, 'role': 'shoe_toe', 'color': '#0f172a', 'size': 20})

    # Flying golf ball trajectory & White golf ball
    for p in bezier_cubic((-40, 175), (50, 120), (140, 0), (190, -140), 20):
        raw.append({'x': p[0], 'y': p[1], 'role': 'ball_trail', 'color': '#38bdf8', 'size': 17})
    raw.append({'x': 196, 'y': -145, 'role': 'golf_ball', 'color': '#f8fafc', 'size': 24})
    raw.append({'x': -40, 'y': 175, 'role': 'golf_tee', 'color': '#ef4444', 'size': 18})

    return finalize_pose(raw, min_dist=20.0)

def main():
    print("Building Refined Snoopy 7-Pose Typographic Dataset...")
    poses = [
        {
            'id': 'pose_doghouse',
            'title': '趴臥狗屋白日夢',
            'englishTitle': 'Daydreaming on the Doghouse',
            'quote': '「幸福就是……躺在屋頂思考人生的美好哲理。」',
            'particles': build_pose_1()
        },
        {
            'id': 'pose_joecool',
            'title': '墨鏡酷哥喬酷兒',
            'englishTitle': 'Joe Cool with Sunglasses',
            'quote': '「戴上墨鏡，整個宇宙都是我的伸展台。」',
            'particles': build_pose_2()
        },
        {
            'id': 'pose_happydance',
            'title': '快樂開懷踢踏舞',
            'englishTitle': 'The Joyful Happy Dance',
            'quote': '「不需要特別的理由，只要活著就值得大跳踢踏舞！」',
            'particles': build_pose_3()
        },
        {
            'id': 'pose_flyingace',
            'title': '一戰王牌飛行員',
            'englishTitle': 'World War I Flying Ace',
            'quote': '「紅色圍巾迎風狂飆！看我衝破雲層擊退紅男爵！」',
            'particles': build_pose_4()
        },
        {
            'id': 'pose_bighug',
            'title': '暖暖擁抱大愛心',
            'englishTitle': 'Love & Big Warm Hug',
            'quote': '「把最溫暖的心送給姿桂，滿滿的愛意永不褪色。」',
            'particles': build_pose_5()
        },
        {
            'id': 'pose_woodstock',
            'title': '與糊塗塌客悄悄話',
            'englishTitle': 'Snoopy & Woodstock Whispers',
            'quote': '「你站在我的鼻尖輕唱，就是世間最甜美的悄悄話。」',
            'particles': build_pose_6()
        },
        {
            'id': 'pose_golfer',
            'title': '高爾夫優雅揮桿',
            'englishTitle': 'Championship Golfer Ace',
            'quote': '「瞄準夢想的果嶺，優雅揮出一桿進洞！」',
            'particles': build_pose_7()
        }
    ]

    for pose in poses:
        cnt = len(pose['particles'])
        y_cnt = sum(1 for p in pose['particles'] if p['char'] == '閻')
        t_cnt = sum(1 for p in pose['particles'] if p['char'] == '姿')
        k_cnt = sum(1 for p in pose['particles'] if p['char'] == '桂')
        print(f"[{pose['title']}] Total: {cnt} | 閻: {y_cnt}, 姿: {t_cnt}, 桂: {k_cnt}")
        assert cnt == TOTAL_PARTICLES, f"Error in {pose['title']}: {cnt} != {TOTAL_PARTICLES}"
        assert y_cnt == 140 and t_cnt == 140 and k_cnt == 140

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(base_dir, 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    json_path = os.path.join(assets_dir, 'snoopy_poses.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(poses, f, ensure_ascii=False, indent=2)

    js_path = os.path.join(base_dir, 'posesData.js')
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write("// Auto-generated Snoopy Kinetic Typography Dataset\n")
        f.write("// Strictly formatted with 420 particles (140 閻, 140 姿, 140 桂)\n")
        f.write("window.SNOOPY_POSES = ")
        json.dump(poses, f, ensure_ascii=False)
        f.write(";\n")
    print(f"Dataset successfully compiled to {json_path} and {js_path}")

if __name__ == '__main__':
    main()
