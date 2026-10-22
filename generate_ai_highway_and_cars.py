import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import subprocess
import base64
import io
import json

src_path = "/working_dir/c_53b67bac264f7ccd/user_uploaded_files/ttl=63d/user_uploaded/image.png"
im = Image.open(src_path).convert("RGB")

# 1. Extract Steering Wheel Cockpit Cam PIP & 4K Badge
pip_im = im.crop((3, 3, 292, 222)).resize((160, 120), Image.Resampling.LANCZOS)
buf_pip = io.BytesIO()
pip_im.save(buf_pip, format="JPEG", quality=85)
pip_b64 = "data:image/jpeg;base64," + base64.b64encode(buf_pip.getvalue()).decode("ascii")

badge_im = im.crop((880, 14, 992, 106)).resize((76, 62), Image.Resampling.LANCZOS)
buf_badge = io.BytesIO()
badge_im.save(buf_badge, format="JPEG", quality=88)
badge_b64 = "data:image/jpeg;base64," + base64.b64encode(buf_badge.getvalue()).decode("ascii")

# 2. Extract Rear-Chase Hypercars (A, B, C) with tight masks & smaller crisp dimensions (170x112)
try:
    font_plate = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 19)
except:
    font_plate = ImageFont.load_default()

# Car A (Bugatti Divo Blue/Black)
car_a_crop = im.crop((74, 250, 498, 526)).convert("RGBA")
cw, ch = car_a_crop.size
mask_a = Image.new("L", (cw, ch), 0)
draw_a = ImageDraw.Draw(mask_a)
poly_a = [
    (14, 175), (12, 125), (18, 86), (54, 72), (92, 38),
    (142, 12), (210, 4), (290, 4), (355, 14), (396, 42),
    (418, 58), (420, 88), (416, 150), (412, 228), (395, 260),
    (335, 268), (210, 270), (80, 268), (20, 250), (10, 215)
]
draw_a.polygon(poly_a, fill=255)
mask_a = mask_a.filter(ImageFilter.GaussianBlur(radius=2.5))
car_a_crop.putalpha(mask_a)
draw_ca = ImageDraw.Draw(car_a_crop)
draw_ca.rounded_rectangle([132, 160, 238, 185], radius=3, fill=(234, 195, 36, 255), outline=(15, 15, 15, 255), width=2)
draw_ca.rectangle([132, 160, 144, 185], fill=(20, 70, 180, 255))
draw_ca.text((151, 162), "CAR A", fill=(10, 10, 10, 255), font=font_plate)
car_a_small = car_a_crop.resize((176, 114), Image.Resampling.LANCZOS)
buf_ca = io.BytesIO()
car_a_small.save(buf_ca, format="PNG", optimize=True)
car_a_b64 = "data:image/png;base64," + base64.b64encode(buf_ca.getvalue()).decode("ascii")

# Car B (Koenigsegg RS Crimson/Carbon)
car_b_crop = im.crop((506, 254, 948, 528)).convert("RGBA")
bw, bh = car_b_crop.size
mask_b = Image.new("L", (bw, bh), 0)
draw_b = ImageDraw.Draw(mask_b)
poly_b = [
    (8, 60), (24, 48), (56, 28), (102, 8), (172, 4),
    (248, 8), (308, 32), (356, 70), (418, 64), (438, 82),
    (430, 124), (422, 190), (414, 240), (384, 264), (310, 270),
    (155, 270), (36, 262), (14, 224), (8, 145)
]
draw_b.polygon(poly_b, fill=255)
mask_b = mask_b.filter(ImageFilter.GaussianBlur(radius=2.5))
car_b_crop.putalpha(mask_b)
draw_cb = ImageDraw.Draw(car_b_crop)
draw_cb.rounded_rectangle([178, 158, 292, 184], radius=3, fill=(234, 195, 36, 255), outline=(15, 15, 15, 255), width=2)
draw_cb.rectangle([178, 158, 190, 184], fill=(220, 38, 38, 255))
draw_cb.text((200, 160), "CAR B", fill=(10, 10, 10, 255), font=font_plate)
car_b_small = car_b_crop.resize((176, 114), Image.Resampling.LANCZOS)
buf_cb = io.BytesIO()
car_b_small.save(buf_cb, format="PNG", optimize=True)
car_b_b64 = "data:image/png;base64," + base64.b64encode(buf_cb.getvalue()).decode("ascii")

# Car C (Lambo GT Solar Gold/Emerald)
car_c_crop = im.crop((74, 250, 498, 526)).convert("RGB")
c_np = np.array(car_c_crop).astype(np.float32)
r_ch, g_ch, b_ch = c_np[:,:,0], c_np[:,:,1], c_np[:,:,2]
is_red_light = (r_ch > 140) & (r_ch > b_ch * 1.4)
new_r = np.where(is_red_light, r_ch, np.clip(b_ch * 1.18 + 28, 0, 255))
new_g = np.where(is_red_light, g_ch, np.clip(b_ch * 1.06 + 20, 0, 255))
new_b = np.where(is_red_light, b_ch, np.clip(r_ch * 0.42, 0, 255))
c_np = np.stack([new_r, new_g, new_b], axis=-1).astype(np.uint8)
car_c_rgba = Image.fromarray(c_np).convert("RGBA")
car_c_rgba.putalpha(mask_a)
draw_cc = ImageDraw.Draw(car_c_rgba)
draw_cc.rounded_rectangle([132, 160, 238, 185], radius=3, fill=(234, 195, 36, 255), outline=(15, 15, 15, 255), width=2)
draw_cc.rectangle([132, 160, 144, 185], fill=(22, 163, 74, 255))
draw_cc.text((151, 162), "CAR C", fill=(10, 10, 10, 255), font=font_plate)
car_c_small = car_c_rgba.resize((176, 114), Image.Resampling.LANCZOS)
buf_cc = io.BytesIO()
car_c_small.save(buf_cc, format="PNG", optimize=True)
car_c_b64 = "data:image/png;base64," + base64.b64encode(buf_cc.getvalue()).decode("ascii")

# 3. Generate Wider, AI-Enhanced 3-Lane Coastal Highway Video (so all 3 cars fit 100% inside the road!)
sky_crop = im.crop((295, 0, 880, 204)).resize((560, 106), Image.Resampling.LANCZOS)
sky_bgr = cv2.cvtColor(np.array(sky_crop), cv2.COLOR_RGB2BGR)

W, H = 560, 320
horizon_y = 102
road_h = H - horizon_y
fps = 24
total_frames = 72

raw_video = "raw_ai_highway.mp4"
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = cv2.VideoWriter(raw_video, fourcc, fps, (W, H))

y_indices = np.arange(horizon_y, H, dtype=np.float32)
v = (y_indices - horizon_y + 3.0) / float(road_h + 3.0)
z_depth = 1.0 / v
vp_x = W * 0.50

for f in range(total_frames):
    frame = np.zeros((H, W, 3), dtype=np.uint8)
    frame[:106, :] = sky_bgr
    phase = float(f) / float(total_frames)

    for idx, y in enumerate(range(horizon_y, H)):
        vi = v[idx]
        zi = z_depth[idx]
        # Make the road wider so 3 hypercars have plenty of room inside the asphalt!
        # Road half-width expands from 42px at horizon to 272px at bottom (total road width = 544px out of 560px at bottom!)
        road_hw = 40.0 + vi * 234.0
        left_edge = int(vp_x - road_hw)
        right_edge = int(vp_x + road_hw)

        scroll_val = zi * 3.0 - phase * 6.0
        stripe_mod = scroll_val % 1.0

        # Coastal beach sand outside road edges
        sand_bright = int(216 + 12 * np.sin(scroll_val * 2.0 * np.pi))
        if left_edge > 0:
            frame[y, :left_edge] = (min(255, sand_bright - 30), min(255, sand_bright - 10), min(255, sand_bright + 8))
        if right_edge < W:
            frame[y, right_edge:] = (min(255, sand_bright), min(255, sand_bright + 12), min(255, sand_bright + 22))

        # Rich realistic dark-grey highway asphalt
        asphalt_val = int(92 - vi * 18 + 5 * np.sin(scroll_val * 4.0 * np.pi))
        l_clamped = max(0, left_edge)
        r_clamped = min(W, right_edge)
        if r_clamped > l_clamped:
            frame[y, l_clamped:r_clamped] = (asphalt_val + 4, asphalt_val, asphalt_val - 2)

            # 3 distinct polished racing lane tracks (Lane A: -0.58, Lane B: 0.0, Lane C: +0.58 of road_hw)
            for lane_offset in (-0.58, 0.0, 0.58):
                lx = int(vp_x + lane_offset * road_hw)
                tw = max(2, int(vi * 28))
                x0, x1 = max(l_clamped, lx - tw), min(r_clamped, lx + tw)
                frame[y, x0:x1] = (asphalt_val - 10, asphalt_val - 12, asphalt_val - 12)

        # Crisp Red/White / Solid White Highway Outer Guard Curbs so the road boundary is super clear
        curb_w = max(2, int(vi * 7))
        curb_col = (240, 245, 250) if stripe_mod < 0.5 else (45, 55, 225)
        if 0 <= left_edge < W:
            frame[y, max(0, left_edge):min(W, left_edge + curb_w)] = curb_col
        if 0 <= right_edge < W:
            frame[y, max(0, right_edge - curb_w):min(W, right_edge)] = curb_col

        # Iconic Yellow Center Highway Line + 2 White Dashed 3-Lane Dividers at -0.31 and +0.31 of road_hw
        yel_w = max(1, int(vi * 4.5))
        cx = int(vp_x)
        frame[y, max(0, cx - yel_w):min(W, cx + yel_w)] = (28, 198, 248)

        if stripe_mod < 0.52:
            dash_w = max(1, int(vi * 3.2))
            for div_pos in (-0.31, 0.31):
                dx = int(vp_x + div_pos * road_hw)
                frame[y, max(0, dx - dash_w):min(W, dx + dash_w)] = (235, 240, 245)

    # Roadside utility poles outside the wide highway
    for k in range(6):
        pole_z = 1.15 + ((k + (1.0 - phase)) * 1.8) % 10.5
        pole_v = 1.0 / pole_z
        py = int(horizon_y + pole_v * road_h)
        if horizon_y < py < H - 25:
            road_hw_p = 40.0 + pole_v * 234.0
            px_left = int(vp_x - road_hw_p * 1.04)
            pole_h = int(pole_v * 130)
            pole_w = max(1, int(pole_v * 3.5))
            if 3 <= px_left < W - 3:
                cv2.line(frame, (px_left, py), (px_left, max(6, py - pole_h)), (48, 62, 78), pole_w)
                cbar_y = max(8, py - pole_h + int(pole_v * 10))
                cbar_w = max(3, int(pole_v * 18))
                cv2.line(frame, (px_left - cbar_w, cbar_y), (px_left + cbar_w, cbar_y), (42, 55, 70), max(1, pole_w - 1))

    writer.write(frame)

writer.release()

subprocess.run([
    "ffmpeg", "-y", "-i", raw_video,
    "-c:v", "libx264", "-pix_fmt", "yuv420p",
    "-profile:v", "baseline", "-level", "3.0",
    "-crf", "26", "-preset", "veryfast",
    "-movflags", "+faststart",
    "race_track_video.mp4"
], check=True)

with open("extracted_4k_assets.json", "w") as jf:
    json.dump({
        "pip": pip_b64,
        "badge": badge_b64,
        "car_a": car_a_b64,
        "car_b": car_b_b64,
        "car_c": car_c_b64
    }, jf)

print("Successfully built wider AI 3-lane highway video & compact hypercar sprites!")
