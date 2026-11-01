import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import json

BASE_DIR = r"C:\Users\yoyo5\.gemini\antigravity\scratch\2026-11-01_閻姿桂文字史奴比動畫藝術館"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
PREVIEWS_DIR = os.path.join(ASSETS_DIR, "previews")
os.makedirs(PREVIEWS_DIR, exist_ok=True)

CHARS = ["閻", "姿", "桂"]
TOTAL_POINTS = 480 # 160 each

def sample_mask_points(mask, count, color="#1e293b", role="core"):
    if count <= 0:
        return []
    ys, xs = np.where(mask > 0)
    if len(xs) == 0:
        return []
    if len(xs) <= count:
        pts = [[float(x), float(y), color, role] for x, y in zip(xs, ys)]
        while len(pts) < count:
            pts.append(list(pts[len(pts) % len(xs)]))
        return pts
    
    coords = np.column_stack([xs, ys])
    if len(coords) > 3000:
        step = len(coords) // 3000
        coords = coords[::step]
        
    min_x, max_x = coords[:,0].min(), coords[:,0].max()
    min_y, max_y = coords[:,1].min(), coords[:,1].max()
    aspect = max(1, (max_x - min_x)) / max(1, (max_y - min_y))
    grid_y = int(np.sqrt(count / aspect)) + 1
    grid_x = int(grid_y * aspect) + 1
    
    bx = np.clip(((coords[:,0] - min_x) / max(1, max_x - min_x) * (grid_x - 1)).astype(int), 0, grid_x - 1)
    by = np.clip(((coords[:,1] - min_y) / max(1, max_y - min_y) * (grid_y - 1)).astype(int), 0, grid_y - 1)
    bins = {}
    for i in range(len(coords)):
        key = (bx[i], by[i])
        if key not in bins:
            bins[key] = []
        bins[key].append(coords[i])
        
    pts = []
    bin_keys = list(bins.keys())
    np.random.seed(42)
    np.random.shuffle(bin_keys)
    k_idx = 0
    while len(pts) < count:
        k = bin_keys[k_idx % len(bin_keys)]
        if len(bins[k]) > 0:
            c = bins[k].pop(0)
            pts.append([float(c[0]), float(c[1]), color, role])
        k_idx += 1
        if all(len(bins[k]) == 0 for k in bin_keys):
            break
            
    while len(pts) < count:
        idx = np.random.randint(len(coords))
        pts.append([float(coords[idx][0]), float(coords[idx][1]), color, role])
    return pts

def sample_contour_points(mask, count, color="#1e293b", role="core"):
    if count <= 0:
        return []
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    valid = [c for c in contours if cv2.arcLength(c, True) > 10]
    if not valid:
        return sample_mask_points(mask, count, color, role)
        
    total_len = sum(cv2.arcLength(c, True) for c in valid)
    pts = []
    for c in valid:
        l = cv2.arcLength(c, True)
        n = max(3, int(round(l / total_len * count)))
        c_pts = c[:, 0, :]
        if len(c_pts) < n:
            idxs = np.linspace(0, len(c_pts)-1, n).astype(int)
        else:
            idxs = np.linspace(0, len(c_pts)-1, n, endpoint=False).astype(int)
        for i in idxs:
            pts.append([float(c_pts[i][0]), float(c_pts[i][1]), color, role])
            
    if len(pts) > count:
        pts = pts[:count]
    while len(pts) < count:
        pts.append(list(pts[len(pts) % max(1, len(pts))]))
    return pts

def normalize_and_center(pts, target_count=480):
    if len(pts) > target_count:
        pts = pts[:target_count]
    while len(pts) < target_count:
        pts.append(list(pts[len(pts) % len(pts)]))
        
    xs = np.array([p[0] for p in pts])
    ys = np.array([p[1] for p in pts])
    min_x, max_x = xs.min(), xs.max()
    min_y, max_y = ys.min(), ys.max()
    cx = (min_x + max_x) / 2.0
    cy = (min_y + max_y) / 2.0
    
    span = max(max_x - min_x, max_y - min_y)
    scale = 520.0 / max(span, 1e-4) # Map to [-260, 260] pixels
    
    normalized = []
    for p in pts:
        nx = float((p[0] - cx) * scale)
        ny = float((p[1] - cy) * scale)
        normalized.append({
            "x": round(nx, 1),
            "y": round(ny, 1),
            "color": p[2],
            "role": p[3],
            "size": 13
        })
    return normalized

def load_grayscale(path):
    return np.array(Image.open(path).convert('L'))

def build_all_poses():
    poses = []
    
    # =========================================================================
    # POSE 1: 趴臥狗屋白日夢 (Classic Snoopy Sleeping on Doghouse)
    # =========================================================================
    print("Building Pose 1: 趴臥狗屋白日夢...")
    # Load clean rotated mask
    im1_m = load_grayscale(os.path.join(ASSETS_DIR, "test_snoopy_clean_mask_rot.png"))
    p1_snoopy = sample_contour_points(im1_m, 290, color="#1e293b", role="core")
    # Ear fill (x in [130..220], y in [240..340])
    ear1_m = np.zeros_like(im1_m)
    ear1_m[240:340, 130:220] = im1_m[240:340, 130:220]
    p1_ear = sample_mask_points(ear1_m, 35, color="#0f172a", role="feature")
    # Nose fill (x in [210..270], y in [170..220])
    nose1_m = np.zeros_like(im1_m)
    nose1_m[170:220, 210:270] = im1_m[170:220, 210:270]
    p1_nose = sample_mask_points(nose1_m, 25, color="#0f172a", role="feature")
    
    # Red Doghouse Roof: peak directly touches his horizontal back at (250, 335)
    p1_roof = []
    for t in np.linspace(0, 1, 35):
        p1_roof.append([250 + (60 - 250)*t, 335 + (500 - 335)*t, "#ef4444", "prop"])
        p1_roof.append([250 + (460 - 250)*t, 335 + (500 - 335)*t, "#ef4444", "prop"])
    for t in np.linspace(0, 1, 30):
        p1_roof.append([40 + 440*t, 500, "#dc2626", "prop"])
    for t in np.linspace(0, 1, 15):
        p1_roof.append([90, 500 + 85*t, "#b91c1c", "prop"])
        p1_roof.append([430, 500 + 85*t, "#b91c1c", "prop"])
    for t in np.linspace(0, 1, 15):
        p1_roof.append([200 + 120*t, 585, "#78350f", "prop"])
    p1_roof.append([180, 150, "#38bdf8", "prop"])
    p1_roof.append([160, 120, "#38bdf8", "prop"])
    p1_roof.append([140, 90, "#38bdf8", "prop"])
    
    p1_all = p1_snoopy + p1_ear + p1_nose + p1_roof
    p1_pts = normalize_and_center(p1_all)
    poses.append({
        "id": "pose_doghouse",
        "title": "趴臥狗屋白日夢",
        "subtitle": "Daydreaming on the Doghouse",
        "quote": "「幸福就是……躺在屋頂思考人生的美好哲理。」",
        "badge": "ARCHIVE 01 / 07",
        "themeHint": "classic",
        "particles": p1_pts,
        "points": p1_pts
    })

    # =========================================================================
    # POSE 2: 墨鏡酷哥喬酷兒 (Joe Cool with Sunglasses)
    # =========================================================================
    print("Building Pose 2: 墨鏡酷哥喬酷兒...")
    im2_m = load_grayscale(os.path.join(ASSETS_DIR, "test_jc_dark.png"))
    p2_snoopy = sample_contour_points(im2_m, 290, color="#1e293b", role="core")
    # Sunglasses lenses (x in [170..270], y in [70..170])
    sg_m = np.zeros_like(im2_m)
    sg_m[70:170, 170:270] = im2_m[70:170, 170:270]
    p2_sg = sample_mask_points(sg_m, 65, color="#0f172a", role="feature")
    # Backwards cap brim (x in [140..250], y in [0..85])
    cap_m = np.zeros_like(im2_m)
    cap_m[0:85, 140:250] = im2_m[0:85, 140:250]
    p2_cap = sample_mask_points(cap_m, 40, color="#2563eb", role="feature")
    # Red collar around neck
    p2_col = []
    for t in np.linspace(0, 1, 25):
        p2_col.append([150 + 50*t, 215 + 10*t, "#ef4444", "feature"])
    # Clean chair back support behind him (orange)
    p2_chair = []
    for t in np.linspace(0, 1, 35):
        p2_chair.append([240 + 70*t, 190 - 70*t, "#f97316", "prop"])
        p2_chair.append([120 - 70*t, 260 + 30*t, "#ea580c", "prop"])
        
    p2_all = p2_snoopy + p2_sg + p2_cap + p2_col + p2_chair
    p2_pts = normalize_and_center(p2_all)
    poses.append({
        "id": "pose_joecool",
        "title": "墨鏡酷哥喬酷兒",
        "subtitle": "Joe Cool with Sunglasses",
        "quote": "「戴上墨鏡，整個宇宙都是我的伸展台。」",
        "badge": "ARCHIVE 02 / 07",
        "themeHint": "cyber",
        "particles": p2_pts,
        "points": p2_pts
    })

    # =========================================================================
    # POSE 3: 快樂開懷跳躍舞 (The Joyful Happy Dance / Leap)
    # =========================================================================
    print("Building Pose 3: 快樂開懷跳躍舞...")
    im3_m = load_grayscale(os.path.join(ASSETS_DIR, "test_leap_clean.png"))
    p3_snoopy = sample_contour_points(im3_m, 330, color="#1e293b", role="core")
    ear3_m = np.zeros_like(im3_m)
    ear3_m[350:580, 160:270] = im3_m[350:580, 160:270]
    p3_ear = sample_mask_points(ear3_m, 50, color="#0f172a", role="feature")
    nose3_m = np.zeros_like(im3_m)
    nose3_m[310:370, 500:600] = im3_m[310:370, 500:600]
    p3_nose = sample_mask_points(nose3_m, 25, color="#0f172a", role="feature")
    im3_rgb = np.array(Image.open(os.path.join(ASSETS_DIR, "crop_18_leap.png")).convert("RGB"))
    b3, r3, g3 = im3_rgb[:,:,2], im3_rgb[:,:,0], im3_rgb[:,:,1]
    cap3_m = ((b3 > 120) & (r3 < 100) & (g3 < 150)).astype(np.uint8) * 255
    p3_cap = sample_mask_points(cap3_m, 45, color="#2563eb", role="prop")
    col3_m = ((r3 > 140) & (g3 < 70) & (b3 < 70)).astype(np.uint8) * 255
    p3_col = sample_mask_points(col3_m, 30, color="#ef4444", role="feature")
    
    p3_all = p3_snoopy + p3_ear + p3_nose + p3_cap + p3_col
    p3_pts = normalize_and_center(p3_all)
    poses.append({
        "id": "pose_happydance",
        "title": "快樂開懷跳躍舞",
        "subtitle": "The Joyful Happy Dance",
        "quote": "「不需要特別的理由，只要活著就值得大跳踢踏舞！」",
        "badge": "ARCHIVE 03 / 07",
        "themeHint": "risograph",
        "particles": p3_pts,
        "points": p3_pts
    })

    # =========================================================================
    # POSE 4: 一戰王牌飛行員 (World War I Flying Ace)
    # =========================================================================
    print("Building Pose 4: 一戰王牌飛行員...")
    im4_m = load_grayscale(os.path.join(ASSETS_DIR, "test_fa_contour.png"))
    p4_snoopy = sample_contour_points(im4_m, 230, color="#1e293b", role="core")
    
    p4_nose = []
    for t in np.linspace(0, 2*np.pi, 25):
        p4_nose.append([45 + 10*np.cos(t), 55 + 8*np.sin(t), "#0f172a", "feature"])
    p4_ear = []
    for t in np.linspace(0, 1, 35):
        p4_ear.append([190 + 20*np.cos(t*np.pi), 110 + 60*t, "#0f172a", "feature"])
        
    im4_rgb = np.array(Image.open(os.path.join(ASSETS_DIR, "crop_08_flyingace.png")).convert("RGB"))
    r4, g4, b4 = im4_rgb[:,:,0], im4_rgb[:,:,1], im4_rgb[:,:,2]
    scarf4_m = ((r4 > 130) & (g4 < 55) & (b4 < 55)).astype(np.uint8) * 255
    scarf4_m[:60, :] = 0
    scarf4_m[220:, :] = 0
    scarf4_m[:, :95] = 0
    scarf4_m[:, 490:] = 0
    p4_scarf = sample_mask_points(scarf4_m, 160, color="#ef4444", role="prop")
    
    gog4_m = ((r4 > 85) & (g4 > 75) & (b4 < 55) & (im4_rgb[:,:,0] < 150)).astype(np.uint8) * 255
    gog4_m[230:, :] = 0
    gog4_m[:, 110:] = 0
    p4_gog = sample_mask_points(gog4_m, 30, color="#d97706", role="feature")
    
    p4_all = p4_snoopy + p4_nose + p4_ear + p4_scarf + p4_gog
    p4_pts = normalize_and_center(p4_all)
    poses.append({
        "id": "pose_flyingace",
        "title": "一戰王牌飛行員",
        "subtitle": "World War I Flying Ace",
        "quote": "「紅色男爵，你逃不過我皇家駱駝式戰鬥機的追擊！」",
        "badge": "ARCHIVE 04 / 07",
        "themeHint": "classic",
        "particles": p4_pts,
        "points": p4_pts
    })

    # =========================================================================
    # POSE 5: 暖暖擁抱大愛心 (Heart Hug with Woodstock)
    # =========================================================================
    print("Building Pose 5: 暖暖擁抱大愛心...")
    im5 = Image.open(os.path.join(ASSETS_DIR, "crop_03_heart.png")).convert("RGB")
    arr5 = np.array(im5)
    gray5 = cv2.cvtColor(arr5, cv2.COLOR_RGB2GRAY)
    dark5 = (gray5 < 60).astype(np.uint8) * 255
    r5, g5, b5 = arr5[:,:,0], arr5[:,:,1], arr5[:,:,2]
    
    p5_heart = sample_contour_points(dark5, 230, color="#ef4444", role="core")
    ear5_m = np.zeros_like(dark5)
    ear5_m[150:330, 20:190] = dark5[150:330, 20:190]
    p5_ear = sample_mask_points(ear5_m, 40, color="#0f172a", role="feature")
    nose5_m = np.zeros_like(dark5)
    nose5_m[80:170, 320:420] = dark5[80:170, 320:420]
    p5_nose = sample_mask_points(nose5_m, 30, color="#0f172a", role="feature")
    wood5_m = ((r5 > 180) & (g5 > 165) & (b5 < 70)).astype(np.uint8) * 255
    p5_wood = sample_mask_points(wood5_m, 140, color="#f59e0b", role="prop")
    blush5_m = ((r5 > 210) & (g5 > 120) & (g5 < 190) & (b5 > 140) & (b5 < 210)).astype(np.uint8) * 255
    p5_blush = sample_mask_points(blush5_m, 40, color="#f472b6", role="feature")
    
    p5_all = p5_heart + p5_ear + p5_nose + p5_wood + p5_blush
    p5_pts = normalize_and_center(p5_all)
    poses.append({
        "id": "pose_bighug",
        "title": "暖暖擁抱大愛心",
        "subtitle": "Love & Big Warm Hug",
        "quote": "「愛就是……給最脆弱的朋友一個毫無保留的溫暖擁抱。」",
        "badge": "ARCHIVE 05 / 07",
        "themeHint": "risograph",
        "particles": p5_pts,
        "points": p5_pts
    })

    # =========================================================================
    # POSE 6: 開心擁抱大自然 (Iconic Standing Snoopy with Open Arms)
    # =========================================================================
    print("Building Pose 6: 開心擁抱大自然...")
    im6 = Image.open(os.path.join(ASSETS_DIR, "crop_01_thumb.png")).convert("RGB")
    arr6 = np.array(im6)
    gray6 = cv2.cvtColor(arr6, cv2.COLOR_RGB2GRAY)
    dark6 = (gray6 < 75).astype(np.uint8) * 255
    
    p6_snoopy = sample_contour_points(dark6, 370, color="#1e293b", role="core")
    ear6_m = np.zeros_like(dark6)
    ear6_m[90:230, 250:340] = dark6[90:230, 250:340]
    p6_ear = sample_mask_points(ear6_m, 55, color="#0f172a", role="feature")
    nose6_m = np.zeros_like(dark6)
    nose6_m[110:150, 70:120] = dark6[110:150, 70:120]
    p6_nose = sample_mask_points(nose6_m, 25, color="#0f172a", role="feature")
    collar6_m = np.zeros_like(dark6)
    collar6_m[250:275, 140:220] = dark6[250:275, 140:220]
    p6_collar = sample_mask_points(collar6_m, 30, color="#ef4444", role="feature")
    
    p6_all = p6_snoopy + p6_ear + p6_nose + p6_collar
    p6_pts = normalize_and_center(p6_all)
    poses.append({
        "id": "pose_woodstock",
        "title": "開心擁抱大自然",
        "subtitle": "Open Arms Welcome",
        "quote": "「放開雙手擁抱世界，每一天都是最可愛的冒險。」",
        "badge": "ARCHIVE 06 / 07",
        "themeHint": "classic",
        "particles": p6_pts,
        "points": p6_pts
    })

    # =========================================================================
    # POSE 7: 好友相伴悄悄話 (Snoopy on Doghouse Reading / with Woodstock)
    # =========================================================================
    print("Building Pose 7: 好友相伴悄悄話...")
    im7_m = load_grayscale(os.path.join(ASSETS_DIR, "test_doghouse_snoopy_clean.png"))
    p7_snoopy = sample_contour_points(im7_m, 240, color="#1e293b", role="core")
    
    ear7_m = np.zeros_like(im7_m)
    ear7_m[120:210, 150:200] = im7_m[120:210, 150:200]
    p7_ear = sample_mask_points(ear7_m, 35, color="#0f172a", role="feature")
    nose7_m = np.zeros_like(im7_m)
    nose7_m[135:155, 260:295] = im7_m[135:155, 260:295]
    p7_nose = sample_mask_points(nose7_m, 20, color="#0f172a", role="feature")
    
    im7_rgb = np.array(Image.open(os.path.join(ASSETS_DIR, "crop_07_doghouse.png")).convert("RGB"))
    r7, g7, b7 = im7_rgb[:,:,0], im7_rgb[:,:,1], im7_rgb[:,:,2]
    wood7_m = ((r7 > 170) & (g7 > 150) & (b7 < 70)).astype(np.uint8) * 255
    wood7_m[85:, :] = 0
    p7_wood = sample_mask_points(wood7_m, 60, color="#f59e0b", role="prop")
    helm7_m = ((r7 > 150) & (g7 < 60) & (b7 < 60)).astype(np.uint8) * 255
    helm7_m[85:, :] = 0
    p7_helm = sample_mask_points(helm7_m, 25, color="#dc2626", role="prop")
    
    book7_m = ((b7 > 120) & (r7 < 110) & (g7 < 170)).astype(np.uint8) * 255
    book7_m[:160, :] = 0
    p7_book = sample_contour_points(book7_m, 65, color="#0284c7", role="prop")
    
    p7_roof = []
    for t in np.linspace(0, 1, 35):
        p7_roof.append([90 + 360*t, 315, "#ef4444", "prop"])
        
    p7_all = p7_snoopy + p7_ear + p7_nose + p7_wood + p7_helm + p7_book + p7_roof
    p7_pts = normalize_and_center(p7_all)
    poses.append({
        "id": "pose_golfer",
        "title": "好友相伴悄悄話",
        "subtitle": "Snoopy & Woodstock Whispers",
        "quote": "「最好的午後時光，就是坐在屋頂和摯友一起閱讀整片天空。」",
        "badge": "ARCHIVE 07 / 07",
        "themeHint": "imperial",
        "particles": p7_pts,
        "points": p7_pts
    })

    # Save to JSON
    json_path = os.path.join(ASSETS_DIR, "snoopy_poses.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(poses, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(poses)} poses to {json_path}")
    
    # Save standalone posesData.js
    js_path = os.path.join(BASE_DIR, "posesData.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("// 高精度 480 粒子均衡（閻/姿/桂 各160）正宗漫畫形態數據集\n")
        f.write("window.SNOOPY_POSES = " + json.dumps(poses, ensure_ascii=False) + ";\n")
    print(f"Saved posesData.js")
    
    # Render preview PNGs
    try:
        font = ImageFont.truetype("msjh.ttc", 13)
        font_title = ImageFont.truetype("msjh.ttc", 22)
        font_sub = ImageFont.truetype("msjh.ttc", 14)
    except:
        font = ImageFont.load_default()
        font_title = font
        font_sub = font
        
    for idx, p in enumerate(poses):
        canvas = Image.new("RGB", (800, 800), "#fbf8f1")
        draw = ImageDraw.Draw(canvas)
        draw.rectangle([20, 20, 780, 780], outline="#e2e8f0", width=2)
        t_text = f"閻姿桂 × 史奴比 #{idx+1}：{p['title']}"
        draw.text((400, 50), t_text, font=font_title, fill="#0f172a", anchor="mm")
        draw.text((400, 80), p['subtitle'], font=font_sub, fill="#64748b", anchor="mm")
        
        pts = p["particles"]
        for i, pt in enumerate(pts):
            ch = CHARS[i % 3]
            sx = 400 + pt["x"]
            sy = 400 + pt["y"]
            draw.text((sx-6, sy-6), ch, font=font, fill=pt["color"])
            
        draw.text((400, 740), p["quote"], font=font, fill="#475569", anchor="mm")
        preview_file = os.path.join(PREVIEWS_DIR, f"pose_{idx+1}_{p['id']}.png")
        canvas.save(preview_file)
        print(f"Rendered preview: {preview_file}")

if __name__ == "__main__":
    build_all_poses()
