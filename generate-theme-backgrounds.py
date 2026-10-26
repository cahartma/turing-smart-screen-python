#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Generates background.png for the FedoraAurora (v2), RedAurora and NetPulse themes.
# Not tracked in git: tweak palettes/layouts here and re-run to regenerate.
#
# Usage: python3 generate-theme-backgrounds.py

import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 320, 480
FONT_LABEL = "res/fonts/jetbrains-mono/JetBrainsMono-Medium.ttf"

PALETTES = {
    # base_top, base_bottom, card, card_border, accent, label, track
    "aurora": {
        "base_top": (10, 15, 28), "base_bottom": (16, 27, 44),
        "card": (18, 28, 44), "border": (34, 48, 70),
        "accent": (81, 162, 218), "label": (111, 140, 171), "track": (40, 74, 110),
    },
    "red": {
        "base_top": (17, 10, 12), "base_bottom": (27, 16, 20),
        "card": (30, 19, 23), "border": (58, 34, 40),
        "accent": (238, 0, 0), "label": (166, 110, 116), "track": (96, 32, 34),
    },
    "net": {
        "base_top": (8, 17, 21), "base_bottom": (12, 27, 33),
        "card": (14, 30, 38), "border": (28, 56, 66),
        "accent": (45, 212, 191), "label": (100, 150, 164), "track": (30, 90, 82),
    },
    "bento": {
        "base_top": (13, 17, 21), "base_bottom": (19, 25, 31),
        "card": (24, 30, 36), "border": (42, 52, 60),
        "accent": (81, 162, 218), "label": (124, 140, 152), "track": (44, 74, 100),
    },
    "hud": {
        "base_top": (10, 10, 12), "base_bottom": (14, 14, 16),
        "card": (19, 19, 22), "border": (52, 36, 38),
        "accent": (229, 55, 43), "label": (150, 116, 116), "track": (82, 26, 24),
    },
    "neon": {
        "base_top": (15, 8, 22), "base_bottom": (24, 12, 34),
        "card": (28, 16, 40), "border": (62, 36, 86),
        "accent": (0, 229, 255), "label": (150, 115, 185), "track": (28, 90, 110),
    },
    "cockpit_green": {
        "base_top": (6, 10, 8), "base_bottom": (10, 18, 13),
        "card": (12, 22, 16), "border": (26, 52, 38),
        "accent": (0, 255, 140), "label": (95, 150, 120), "track": (20, 90, 55),
    },
    "cockpit_amber": {
        "base_top": (12, 9, 5), "base_bottom": (20, 15, 9),
        "card": (26, 20, 12), "border": (56, 42, 24),
        "accent": (255, 176, 0), "label": (170, 135, 90), "track": (100, 70, 20),
    },
    "cockpit_ice": {
        "base_top": (8, 11, 16), "base_bottom": (13, 19, 27),
        "card": (16, 24, 34), "border": (36, 52, 68),
        "accent": (160, 220, 255), "label": (120, 150, 180), "track": (40, 70, 95),
    },
    "term": {
        "base_top": (8, 12, 10), "base_bottom": (8, 12, 10),
        "card": (8, 12, 10), "border": (40, 52, 44),
        "accent": (0, 255, 140), "label": (95, 130, 105), "track": (20, 90, 55),
    },
    "chrono": {
        "base_top": (11, 13, 17), "base_bottom": (15, 18, 24),
        "card": (17, 21, 28), "border": (52, 58, 70),
        "accent": (120, 180, 255), "label": (115, 128, 148), "track": (36, 56, 86),
    },
    "car": {
        "base_top": (10, 11, 13), "base_bottom": (14, 16, 19),
        "card": (16, 18, 21), "border": (40, 44, 50),
        "accent": (140, 190, 235), "label": (110, 120, 132), "track": (35, 50, 65),
    },
    "jet": {
        "base_top": (5, 8, 6), "base_bottom": (8, 12, 9),
        "card": (10, 16, 12), "border": (28, 60, 40),
        "accent": (0, 255, 120), "label": (60, 130, 85), "track": (20, 80, 50),
    },
    "jet_amber": {
        "base_top": (12, 9, 4), "base_bottom": (18, 13, 7),
        "card": (22, 16, 9), "border": (60, 42, 20),
        "accent": (255, 176, 0), "label": (150, 115, 60), "track": (100, 70, 20),
    },
    "jet_steel": {
        "base_top": (8, 9, 12), "base_bottom": (11, 13, 17),
        "card": (13, 16, 21), "border": (40, 48, 62),
        "accent": (120, 180, 255), "label": (105, 120, 145), "track": (36, 56, 86),
    },
}


def gradient(p, w=W, h=H):
    img = Image.new("RGB", (w, h))
    for y in range(h):
        t = y / h
        c = tuple(int(a + (b - a) * t) for a, b in zip(p["base_top"], p["base_bottom"]))
        img.paste(c, (0, y, w, y + 1))
    return img


def glow(img, cx, cy, radius, color, max_alpha=42):
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    for r in range(radius, 0, -3):
        a = int(max_alpha * (1 - r / radius))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=a)
    mask = mask.filter(ImageFilter.GaussianBlur(14))
    overlay = Image.new("RGB", (w, h), color)
    img.paste(overlay, (0, 0), mask)


def card(d, box, p, accent_bar=True):
    d.rounded_rectangle(box, radius=12, fill=p["card"], outline=p["border"], width=1)
    if accent_bar:
        # Left accent stripe, nearly full card height (inset only for the rounded corners)
        d.line((box[0] + 2, box[1] + 6, box[0] + 2, box[3] - 6), fill=p["accent"], width=2)


def attitude_face(d, cx, cy, r, p):
    """Artificial-horizon (gyro) dial face: sky over earth with a pitch ladder."""
    sky, earth = (28, 58, 92), (74, 52, 28)
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=sky)
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 0, 180, fill=earth)
    d.line((cx - r, cy, cx + r, cy), fill=(220, 225, 230), width=2)  # horizon line
    for dy in (7, 14):
        w = r - 8 - dy
        d.line((cx - w, cy - dy, cx + w, cy - dy), fill=(150, 160, 175), width=1)  # pitch ladder
        d.line((cx - w, cy + dy, cx + w, cy + dy), fill=(140, 120, 100), width=1)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=p["border"])


def chamfer_card(d, box, p, ch=10):
    """Avionics-style panel: chamfered corners and ruler ticks."""
    x0, y0, x1, y1 = box
    pts = [(x0 + ch, y0), (x1 - ch, y0), (x1, y0 + ch), (x1, y1 - ch),
           (x1 - ch, y1), (x0 + ch, y1), (x0, y1 - ch), (x0, y0 + ch)]
    d.polygon(pts, fill=p["card"])
    d.line(pts + [pts[0]], fill=p["border"], width=1)
    # Ruler ticks along the top edge (major every 100px)
    for x in range(x0 + ch + 8, x1 - ch - 4, 20):
        major = ((x - x0 - ch) % 100) < 20
        d.line((x, y0 + 1, x, y0 + (6 if major else 3)), fill=p["label"])


def trace(d, p0, p1, p, pad=2):
    """PCB-style trace with round pads at both ends."""
    d.line((p0, p1), fill=p["track"], width=2)
    for x, y in (p0, p1):
        d.ellipse([x - pad, y - pad, x + pad, y + pad], fill=p["track"])


def reticle(img, cx, cy, p, r_bar=53):
    """Instrument tick-ring around a radial gauge, with neon bloom.
    The ring is open at the bottom, matching the gauge's 135-to-45-degree sweep."""
    ring_box = [cx - (r_bar + 15), cy - (r_bar + 15), cx + (r_bar + 15), cy + (r_bar + 15)]
    mask_img = Image.new("L", img.size, 0)
    mask = ImageDraw.Draw(mask_img)
    for a in range(0, 360, 10):
        if 45 < a < 135:
            continue  # bottom gap: no ticks where the gauge has no sweep
        major = a % 30 == 0
        r_out = r_bar + 13 if major else r_bar + 9
        rad = math.radians(a)
        mask.line((cx + (r_bar + 3) * math.cos(rad), cy + (r_bar + 3) * math.sin(rad),
                   cx + r_out * math.cos(rad), cy + r_out * math.sin(rad)),
                  fill=140 if major else 80, width=2)
    mask.arc(ring_box, 135, 45, fill=60)
    # Bloom: blurred copy of the tick mask composited in the accent color
    bloom = mask_img.filter(ImageFilter.GaussianBlur(4)).point(lambda v: min(v, 110))
    img.paste(Image.new("RGB", img.size, p["accent"]), (0, 0), bloom)
    # Sharp ticks on top
    d = ImageDraw.Draw(img)
    for a in range(0, 360, 10):
        if 45 < a < 135:
            continue
        major = a % 30 == 0
        r_out = r_bar + 13 if major else r_bar + 9
        rad = math.radians(a)
        d.line((cx + (r_bar + 3) * math.cos(rad), cy + (r_bar + 3) * math.sin(rad),
                cx + r_out * math.cos(rad), cy + r_out * math.sin(rad)),
               fill=p["accent"] if major else p["label"], width=2)
    d.arc(ring_box, 135, 45, fill=p["track"])


def scanlines(img, step=4, alpha=45):
    """CRT scanline pass over the finished image."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for y in range(0, img.size[1], step):
        d.line((0, y, img.size[0], y), fill=(0, 0, 0, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def cockpit_layout(p):
    """Avionics experiment: chamfered panels, gauge reticle with bloom, traces, scanlines."""
    img = gradient(p)
    glow(img, 100, 126, 80, p["accent"], max_alpha=52)
    # Soft bloom behind the big memory/disk values
    glow(img, 60, 268, 44, p["accent"], max_alpha=14)
    glow(img, 60, 396, 44, p["accent"], max_alpha=14)
    d = ImageDraw.Draw(img)

    chamfer_card(d, (16, 56, 304, 196), p)   # CPU: gauge + reticle left, temp/fan right
    chamfer_card(d, (16, 204, 304, 328), p)  # memory
    chamfer_card(d, (16, 336, 304, 448), p)  # disk

    label(d, (30, 68), "CPU", p)
    label(d, (170, 86), "TEMP", p)
    label(d, (170, 138), "FAN", p)
    label(d, (30, 216), "MEMORY", p)
    label(d, (30, 348), "DISK", p)

    # Gyro: artificial-horizon face under the CPU gauge sweep
    attitude_face(d, 100, 126, 38, p)

    # Memory/disk round instrument dials with their own tick reticles
    reticle(img, 250, 266, p, r_bar=36)
    reticle(img, 250, 396, p, r_bar=36)

    # PCB traces routing between panels through the gaps
    trace(d, (160, 49), (160, 56), p)
    trace(d, (44, 196), (44, 204), p)
    trace(d, (276, 196), (276, 204), p)
    trace(d, (44, 328), (44, 336), p)
    trace(d, (276, 328), (276, 336), p)
    trace(d, (291, 200), (296, 204), p)  # 45-degree stub

    d.line((16, 456, 304, 456), fill=p["border"])

    reticle(img, 100, 126, p)
    return scanlines(img)


def track(d, box, p):
    """Dim full-length bar behind theme progress graphs, showing what 100% looks like.

    Must match the GRAPH X/Y/WIDTH/HEIGHT in the theme.yaml exactly."""
    d.rounded_rectangle(box, radius=2, fill=p["track"])


def label(d, xy, text, p, size=9):
    d.text(xy, text, font=ImageFont.truetype(FONT_LABEL, size), fill=p["label"])


def fedora_logo(d, x, y, p):
    """Original simple fedora silhouette (not the Red Hat trademark)."""
    color, band = p["accent"], (120, 0, 0)
    d.rounded_rectangle((x + 5, y, x + 29, y + 17), radius=5, fill=color)   # crown
    d.rectangle((x + 5, y + 11, x + 29, y + 16), fill=band)                 # band
    d.rounded_rectangle((x, y + 15, x + 34, y + 22), radius=3, fill=color)  # brim


def system_layout(p, logo=False):
    """Compact CPU card + large memory/disk cards. Header: user left, battery right."""
    img = gradient(p)
    glow(img, 100, 126, 80, p["accent"])
    d = ImageDraw.Draw(img)

    card(d, (16, 56, 304, 196), p)    # CPU: radial gauge left, temp/fan right
    card(d, (16, 204, 304, 328), p)   # memory
    card(d, (16, 336, 304, 448), p)   # disk

    label(d, (30, 68), "CPU", p)
    label(d, (170, 86), "TEMP", p)
    label(d, (170, 138), "FAN", p)
    label(d, (30, 216), "MEMORY", p)
    label(d, (30, 348), "DISK", p)

    track(d, (30, 298, 290, 308), p)   # memory graph
    track(d, (30, 420, 290, 430), p)   # disk graph

    if logo:
        fedora_logo(d, 20, 12, p)

    d.line((16, 456, 304, 456), fill=p["border"])
    return img


def net_layout(p):
    """Wi-Fi signal, download rate + graph, upload + ping + ping graph, totals strip, clock footer."""
    img = gradient(p)
    glow(img, 160, 220, 110, p["accent"], max_alpha=26)
    d = ImageDraw.Draw(img)

    card(d, (16, 56, 304, 148), p)    # wi-fi signal
    card(d, (16, 156, 304, 288), p)   # download
    card(d, (16, 296, 304, 408), p)   # upload + ping
    card(d, (16, 416, 304, 448), p)   # totals strip

    label(d, (30, 68), "WI-FI SIGNAL", p)
    label(d, (112, 103), "dBm", p)    # static unit, baked (value is drawn left of it)
    label(d, (30, 168), "DOWNLOAD", p)
    label(d, (30, 308), "UPLOAD", p)
    label(d, (178, 308), "PING", p)
    label(d, (30, 428), "UP", p)
    label(d, (118, 428), "DOWN", p)

    track(d, (30, 130, 290, 140), p)  # wi-fi signal graph
    track(d, (30, 232, 290, 282), p)  # download line graph field
    track(d, (30, 362, 290, 404), p)  # ping line graph field

    d.line((16, 456, 304, 456), fill=p["border"])
    return img


def landscape_layout(p):
    """480x320: CPU + memory top row, disk + network bottom row."""
    img = gradient(p, 480, 320)
    glow(img, 86, 108, 70, p["accent"])
    d = ImageDraw.Draw(img)

    card(d, (16, 48, 228, 168), p)    # cpu: radial left, temp/fan right
    card(d, (236, 48, 464, 168), p)   # memory
    card(d, (16, 176, 228, 296), p)   # disk
    card(d, (236, 176, 464, 296), p)  # network: rates + line graph

    label(d, (30, 60), "CPU", p)
    label(d, (140, 68), "TEMP", p)
    label(d, (140, 116), "FAN", p)
    label(d, (250, 60), "MEMORY", p)
    label(d, (30, 188), "DISK", p)
    label(d, (250, 188), "DOWNLOAD", p)
    label(d, (350, 188), "UPLOAD", p)

    track(d, (250, 140, 450, 150), p)  # memory graph
    track(d, (30, 270, 210, 280), p)   # disk graph
    track(d, (250, 240, 450, 286), p)  # download line graph field

    d.line((16, 306, 464, 306), fill=p["border"])
    return img


def chapter_ring(img, cx, cy, p, r_bar, lume=True):
    """Watch-style chapter ring around a dial: fine minute-track ticks, longer majors,
    open at the bottom like the gauge sweep, optional lume dots at 12/9/3."""
    ring_r = r_bar + 11
    mask_img = Image.new("L", img.size, 0)
    mask = ImageDraw.Draw(mask_img)
    for a in range(0, 360, 6):
        if 45 < a < 135:
            continue  # bottom gap
        major = a % 30 == 0
        r_out = r_bar + (9 if major else 5)
        rad = math.radians(a)
        mask.line((cx + (r_bar + 2) * math.cos(rad), cy + (r_bar + 2) * math.sin(rad),
                   cx + r_out * math.cos(rad), cy + r_out * math.sin(rad)),
                  fill=90 if major else 45, width=1)
    bloom = mask_img.filter(ImageFilter.GaussianBlur(3)).point(lambda v: min(v, 60))
    img.paste(Image.new("RGB", img.size, p["accent"]), (0, 0), bloom)
    d = ImageDraw.Draw(img)
    for a in range(0, 360, 6):
        if 45 < a < 135:
            continue
        major = a % 30 == 0
        r_out = r_bar + (9 if major else 5)
        rad = math.radians(a)
        d.line((cx + (r_bar + 2) * math.cos(rad), cy + (r_bar + 2) * math.sin(rad),
                cx + r_out * math.cos(rad), cy + r_out * math.sin(rad)),
               fill=p["accent"] if major else p["label"], width=1)
    if lume:
        # Lume dots at 12 (top), 9 (left), 3 (right)
        lume_color = (190, 255, 200)
        for a in (270, 180, 0):
            rad = math.radians(a)
            lx, ly = cx + ring_r * math.cos(rad), cy + ring_r * math.sin(rad)
            d.ellipse([lx - 2, ly - 2, lx + 2, ly + 2], fill=lume_color)


def sunburst(d, cx, cy, r, p):
    """Ultra-faint radial brushing on a watch dial face."""
    for a in range(0, 360, 15):
        rad = math.radians(a)
        d.line((cx + 8 * math.cos(rad), cy + 8 * math.sin(rad),
                cx + r * math.cos(rad), cy + r * math.sin(rad)),
               fill=(p["card"][0] + 5, p["card"][1] + 5, p["card"][2] + 6))


def chrono_layout(p):
    """Watch face, packed efficiently: main dial, complication strip, subdials, date aperture."""
    img = gradient(p)
    d = ImageDraw.Draw(img)

    # Sunburst brushing on all three dial faces
    sunburst(d, 160, 140, 58, p)
    sunburst(d, 72, 330, 40, p)
    sunburst(d, 248, 330, 40, p)

    # Main dial (CPU) with lume dots; memory/disk subdials below
    chapter_ring(img, 160, 140, p, 63)
    chapter_ring(img, 72, 330, p, 44, lume=False)
    chapter_ring(img, 248, 330, p, 44, lume=False)

    # Complication strip labels under the main dial
    label(d, (34, 226), "TEMP", p)
    label(d, (132, 226), "FAN", p)
    label(d, (222, 226), "WIFI", p)
    label(d, (250, 246), "dBm", p)

    # Tiny subdial labels inside the upper half of each register
    label(d, (58, 300), "MEM", p)
    label(d, (234, 300), "DISK", p)

    # 6 o'clock date aperture between the subdials
    d.rectangle((134, 314, 186, 346), fill=(p["card"][0] + 6, p["card"][1] + 6, p["card"][2] + 8),
                outline=p["border"])
    return img


def car_layout(p):
    """Car instrument cluster (480x320): twin dials with redline/low-zone arcs,
    center TFT panel, warning-light strip."""
    img = gradient(p, 480, 320)
    d = ImageDraw.Draw(img)
    red = (255, 60, 50)

    sunburst(d, 100, 155, 75, p)
    sunburst(d, 380, 155, 75, p)

    # Twin dials: CPU "tach" (left) and memory "fuel" (right)
    chapter_ring(img, 100, 155, p, 80)
    chapter_ring(img, 380, 155, p, 80)
    # Warning zones on both dials, on the ring: amber 0-20%, red 80-100% of the sweep
    amber = (170, 117, 0)
    for cx in (100, 380):
        ring_box = [cx - 91, 155 - 91, cx + 91, 155 + 91]
        d.arc(ring_box, 351, 45, fill=red, width=3)
        d.arc(ring_box, 135, 189, fill=amber, width=3)

    # Brand emblem: double-ring oval above the center panel
    d.ellipse((192, 36, 288, 80), outline=p["border"], width=2)
    d.ellipse((195, 39, 285, 77), outline=(60, 66, 76), width=1)

    # Turn-signal bezels: dim arrow outlines at the cluster corners (blinkers light inside them)
    dim_green = (25, 70, 45)
    d.polygon([(44, 38), (20, 50), (44, 62)], outline=dim_green)   # left bezel points left
    d.polygon([(436, 38), (460, 50), (436, 62)], outline=dim_green)  # right bezel points right

    # Units labels inside the dials, under the big readouts
    label(d, (86, 186), "CPU", p)
    label(d, (366, 186), "MEM", p)

    # Center TFT panel
    d.rounded_rectangle((196, 80, 284, 230), radius=6, fill=p["card"], outline=p["border"])
    label(d, (204, 96), "TEMP", p)
    label(d, (204, 126), "FAN", p)
    label(d, (204, 156), "DISK", p)
    label(d, (204, 186), "NET", p)

    # Warning-light strip: simple dim glyphs (battery, temp, fuel, engine)
    wl = (120, 95, 60)
    x = 196
    d.rounded_rectangle((x, 254, x + 16, 262), radius=2, outline=wl)          # battery
    d.rectangle((x + 16, 256, x + 19, 260), outline=wl)
    d.line((x + 32, 252, x + 32, 262), fill=wl)                                # thermometer
    d.ellipse([x + 29, 260, x + 35, 266], outline=wl)
    d.rectangle((x + 48, 252, x + 62, 266), outline=wl)                        # fuel pump
    d.line((x + 62, 254, x + 68, 258), fill=wl)
    d.rounded_rectangle((x + 80, 252, x + 96, 266), radius=3, outline=wl)      # engine
    d.line((x + 84, 249, x + 84, 252), fill=wl)
    d.line((x + 92, 249, x + 92, 252), fill=wl)
    return img


def terminal_layout(p):
    """Plain terminal-style dump: flat background, separator lines, baked labels."""
    img = gradient(p)  # flat when base_top == base_bottom
    d = ImageDraw.Draw(img)
    for y in (44, 306, 440):
        d.line((12, y, 308, y), fill=p["border"])
    rows = [("CPU", 16, 64), ("TEMP", 170, 64), ("FAN", 16, 94), ("PING", 170, 94),
            ("MEMORY", 16, 124), ("DISK", 16, 154),
            ("DOWN", 16, 184), ("UP", 170, 184), ("RX", 16, 214), ("TX", 170, 214),
            ("WIFI", 16, 244), ("UPTIME", 16, 274)]
    for text, x, y in rows:
        label(d, (x, y + 3), text, p)
    label(d, (100, 247), "dBm", p)
    # "/" separators between used and total values
    for y in (127, 157):
        label(d, (140, y), "/", p)
    # History graph labels below uptime
    label(d, (16, 318), "CPU%", p)
    label(d, (16, 382), "NET", p)
    return img


def jet_layout(p):
    """Fighter-jet HUD: heading tape with data box, radar scope with range rings and blips,
    data blocks, pitch-ladder graph tapes, systems status row. Green monochrome."""
    img = gradient(p)
    d = ImageDraw.Draw(img)
    dim = p["track"]

    # Heading tape: horizontal ruler with ticks and a center data box
    d.line((30, 50, 290, 50), fill=dim)
    for x in range(30, 291, 10):
        major = (x - 30) % 50 == 0
        d.line((x, 50, x, 50 - (8 if major else 4)), fill=dim)
    d.rectangle((132, 36, 188, 64), outline=p["label"])

    # Radar scope: range rings, cross ticks, blips; the theme's radial is the sweep
    for r in (28, 52):
        d.ellipse([160 - r, 210 - r, 160 + r, 210 + r], outline=dim)
    for a in (0, 90, 180, 270):
        rad = math.radians(a)
        d.line((160 + 58 * math.cos(rad), 210 + 58 * math.sin(rad),
                160 + 66 * math.cos(rad), 210 + 66 * math.sin(rad)), fill=dim)
    for bx, by in ((120, 180), (190, 240), (150, 250), (200, 170), (130, 230)):
        d.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=p["label"])
    reticle(img, 160, 210, p, 75)

    # Data blocks overlaying the scope edges (airspeed/altitude style)
    d.rectangle((24, 178, 100, 242), fill=p["card"], outline=p["label"])
    d.rectangle((220, 178, 296, 242), fill=p["card"], outline=p["label"])
    label(d, (30, 182), "MEM", p)
    label(d, (240, 182), "DSK", p)

    # Pitch-ladder graph tapes
    for y0 in (306, 352):
        d.rectangle((40, y0, 280, y0 + 38), outline=dim)
        for gy in range(y0 + 8, y0 + 38, 8):
            d.line((40, gy, 280, gy), fill=(p["base_top"][0] + 6, p["base_top"][1] + 10, p["base_top"][2] + 7))
    label(d, (16, 310), "DWN", p)
    label(d, (16, 356), "UP", p)

    # Systems status row
    label(d, (16, 404), "FAN", p)
    label(d, (120, 404), "WIFI", p)
    label(d, (220, 404), "BAT", p)
    return img


def jet_landscape_layout(p):
    """Fighter-jet HUD in 480x320: heading tape, radar scope, flanking data blocks, footer."""
    img = gradient(p, 480, 320)
    d = ImageDraw.Draw(img)
    dim = p["track"]

    # Heading tape: horizontal ruler with ticks and a center data box
    d.line((40, 50, 440, 50), fill=dim)
    for x in range(40, 441, 10):
        major = (x - 40) % 50 == 0
        d.line((x, 50, x, 50 - (8 if major else 4)), fill=dim)
    d.rectangle((216, 36, 264, 64), outline=p["label"])

    # Radar scope: range rings, cross ticks, blips; the theme's radial is the sweep
    for r in (28, 52):
        d.ellipse([240 - r, 190 - r, 240 + r, 190 + r], outline=dim)
    for a in (0, 90, 180, 270):
        rad = math.radians(a)
        d.line((240 + 58 * math.cos(rad), 190 + 58 * math.sin(rad),
                240 + 66 * math.cos(rad), 190 + 66 * math.sin(rad)), fill=dim)
    for bx, by in ((200, 160), (270, 220), (230, 230), (280, 150), (210, 210)):
        d.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=p["label"])
    reticle(img, 240, 190, p, 75)

    # Flanking data blocks
    for box, tag in (((24, 130, 116, 202), "MEM"), ((24, 222, 116, 294), "DSK"),
                     ((364, 130, 456, 202), "FAN"), ((364, 222, 456, 294), "WIFI")):
        d.rectangle(box, fill=p["card"], outline=p["label"])
        label(d, (box[0] + 6, box[1] + 4), tag, p)
    label(d, (430, 258), "dBm", p)

    # Footer labels
    label(d, (120, 304), "DWN", p)
    label(d, (270, 304), "UP", p)
    return img


def procdash_layout(p):
    """Process dashboard: compact header, ten top-process rows, summary and net rates. No graphs."""
    img = gradient(p)
    d = ImageDraw.Draw(img)
    for y in (34, 336, 436):
        d.line((12, y, 308, y), fill=p["border"])
    label(d, (40, 40), "PROCESS       CPU   MEM", p)
    for i in range(10):
        label(d, (16, 56 + i * 28), str(i + 1), p)
    label(d, (16, 348), "PROCS", p)
    label(d, (120, 348), "CPU", p)
    label(d, (210, 348), "MEM", p)
    label(d, (16, 400), "DOWN", p)
    label(d, (170, 400), "UP", p)
    return img


def procdash_wide_layout(p):
    """Wide ps-style process table (480x320): PID USER CPU% MEM% COMMAND rows."""
    img = gradient(p, 480, 320)
    d = ImageDraw.Draw(img)
    for y in (34, 288):
        d.line((12, y, 468, y), fill=p["border"])
    # Column labels at the pixel offsets of the fixed-width fields (rows are f13: 7.8px/char)
    label(d, (94, 42), "PID", p)       # cols 1-9, right-aligned numbers
    label(d, (118, 42), "USER", p)     # cols 11-18
    label(d, (192, 42), "CPU%", p)     # cols 20-24
    label(d, (243, 42), "MEM%", p)     # cols 26-30
    label(d, (282, 42), "COMMAND", p)  # col 32+
    label(d, (16, 296), "PROCS", p)
    label(d, (110, 296), "CPU", p)
    label(d, (200, 296), "MEM", p)
    return img


def write(theme, img):
    path = os.path.join("res", "themes", theme)
    os.makedirs(path, exist_ok=True)
    img.save(os.path.join(path, "background.png"))
    print("wrote", os.path.join(path, "background.png"))


if __name__ == "__main__":
    write("Aurora", system_layout(PALETTES["aurora"]))
    write("RedFedoraHat", system_layout(PALETTES["red"], logo=True))
    write("NetPulse", net_layout(PALETTES["net"]))
    write("AuroraLandscape", landscape_layout(PALETTES["aurora"]))
    write("RedFedoraHatLandscape", landscape_layout(PALETTES["red"]))
    write("Bento", system_layout(PALETTES["bento"]))
    write("ThinkPadHUD", system_layout(PALETTES["hud"]))
    write("CockpitCyan", cockpit_layout(PALETTES["neon"]))
    write("CockpitGreen", cockpit_layout(PALETTES["cockpit_green"]))
    write("CockpitAmber", cockpit_layout(PALETTES["cockpit_amber"]))
    write("CockpitIce", cockpit_layout(PALETTES["cockpit_ice"]))
    write("TermDash", terminal_layout(PALETTES["term"]))
    write("Chrono", chrono_layout(PALETTES["chrono"]))
    write("CarCluster", car_layout(PALETTES["car"]))
    write("ProcDash", procdash_layout(PALETTES["term"]))
    write("JetHUD", jet_layout(PALETTES["jet"]))
    write("JetAmber", jet_layout(PALETTES["jet_amber"]))
    write("JetSteel", jet_layout(PALETTES["jet_steel"]))
    write("JetHUDLandscape", jet_landscape_layout(PALETTES["jet"]))
    write("ProcDashLandscape", procdash_wide_layout(PALETTES["term"]))
