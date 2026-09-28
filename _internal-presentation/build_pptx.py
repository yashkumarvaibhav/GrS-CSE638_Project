#!/usr/bin/env python3
"""Generate CNI benchmark presentation PPTX from 1_presentation_plan.md."""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))

# ------------- Theme -------------
NAVY      = RGBColor(0x0F, 0x2A, 0x47)
NAVY_2    = RGBColor(0x1A, 0x3A, 0x5C)
NAVY_3    = RGBColor(0x24, 0x4E, 0x7A)
WHITE     = RGBColor(0xF8, 0xFA, 0xFC)
GRAY      = RGBColor(0xCB, 0xD5, 0xE1)
GRAY_DIM  = RGBColor(0x94, 0xA3, 0xB8)
ACCENT    = RGBColor(0x2D, 0xD4, 0xBF)   # teal
WIN_GREEN = RGBColor(0x22, 0xC5, 0x5E)
LOSE_RED  = RGBColor(0xEF, 0x44, 0x44)
WARN      = RGBColor(0xF5, 0x9E, 0x0B)   # amber
BG_BOX    = RGBColor(0x17, 0x35, 0x58)
HDR_BLUE  = RGBColor(0x1E, 0x40, 0x66)

TITLE_FONT = "Calibri"
BODY_FONT  = "Calibri"

# ------------- Presentation skeleton -------------
prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
SLIDE_W = prs.slide_width
SLIDE_H = prs.slide_height

BLANK = prs.slide_layouts[6]

# ------------- Helpers -------------
def set_bg(slide, color=NAVY):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.line.fill.background()
    bg.shadow.inherit = False
    slide.shapes._spTree.remove(bg._element)
    slide.shapes._spTree.insert(2, bg._element)
    return bg

def add_rect(slide, x, y, w, h, fill=BG_BOX, line=None, corner=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if corner else MSO_SHAPE.RECTANGLE, x, y, w, h)
    if fill is None:
        shape.fill.background()
    else:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(1)
    shape.shadow.inherit = False
    return shape

def add_text(slide, x, y, w, h, text, *, size=18, bold=False, italic=False,
             color=WHITE, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
             font=BODY_FONT):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    if isinstance(text, str):
        lines = [text]
    else:
        lines = text
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = ln
        r.font.name = font
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
    return tb

def add_rich(slide, x, y, w, h, runs, *, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    """runs: list of paragraphs; each paragraph is list of (text, opts) tuples."""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for i, para in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        for text, opts in para:
            r = p.add_run()
            r.text = text
            r.font.name = opts.get("font", BODY_FONT)
            r.font.size = Pt(opts.get("size", 16))
            r.font.bold = opts.get("bold", False)
            r.font.italic = opts.get("italic", False)
            r.font.color.rgb = opts.get("color", WHITE)
    return tb

def add_bullets(slide, x, y, w, h, items, *, size=16, color=WHITE, bullet="•  ", space_after=4):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.margin_left = Inches(0.05)
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(space_after)
        if isinstance(item, str):
            r = p.add_run()
            r.text = bullet + item
            r.font.name = BODY_FONT
            r.font.size = Pt(size)
            r.font.color.rgb = color
        else:
            # item is list of (text, opts)
            first = True
            for text, opts in item:
                r = p.add_run()
                r.text = (bullet + text) if first else text
                first = False
                r.font.name = opts.get("font", BODY_FONT)
                r.font.size = Pt(opts.get("size", size))
                r.font.bold = opts.get("bold", False)
                r.font.italic = opts.get("italic", False)
                r.font.color.rgb = opts.get("color", color)
    return tb

def add_title_bar(slide, text, *, kicker=None):
    # slim accent bar on left
    add_rect(slide, Inches(0.4), Inches(0.35), Inches(0.08), Inches(0.55), fill=ACCENT)
    add_text(slide, Inches(0.6), Inches(0.28), Inches(12.3), Inches(0.7),
             text, size=30, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE, font=TITLE_FONT)
    if kicker:
        add_text(slide, Inches(0.6), Inches(0.78), Inches(12.3), Inches(0.3),
                 kicker, size=14, bold=False, color=GRAY_DIM, font=TITLE_FONT)

def add_footer(slide, slide_num, total=13):
    add_rect(slide, 0, Inches(7.15), SLIDE_W, Inches(0.35), fill=NAVY_2)
    add_text(slide, Inches(0.4), Inches(7.17), Inches(8), Inches(0.3),
             "Group 1  |  CSE638 GRS Winter 2026  |  Benchmarking Kubernetes CNI Plugins",
             size=10, color=GRAY_DIM, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, Inches(12.0), Inches(7.17), Inches(1.1), Inches(0.3),
             f"Slide {slide_num} / {total}",
             size=10, color=GRAY_DIM, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)

def cell_format(cell, *, fill=None, color=WHITE, size=13, bold=False, italic=False, align=PP_ALIGN.LEFT):
    if fill is not None:
        cell.fill.solid()
        cell.fill.fore_color.rgb = fill
    else:
        cell.fill.solid()
        cell.fill.fore_color.rgb = BG_BOX
    tf = cell.text_frame
    tf.margin_left = Inches(0.08)
    tf.margin_right = Inches(0.08)
    tf.margin_top = Inches(0.04)
    tf.margin_bottom = Inches(0.04)
    tf.word_wrap = True
    for p in tf.paragraphs:
        p.alignment = align
        for r in p.runs:
            r.font.name = BODY_FONT
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.italic = italic
            r.font.color.rgb = color

def build_table(slide, x, y, w, h, rows):
    """rows: list of lists; each entry is (text, opts_dict or None).
    First row assumed header. Returns the table shape."""
    nrows = len(rows)
    ncols = len(rows[0])
    tbl_shape = slide.shapes.add_table(nrows, ncols, x, y, w, h)
    tbl = tbl_shape.table
    for i, row in enumerate(rows):
        for j, entry in enumerate(row):
            if isinstance(entry, tuple):
                text, opts = entry
            else:
                text, opts = entry, {}
            opts = opts or {}
            cell = tbl.cell(i, j)
            cell.text = text
            is_header = (i == 0)
            fill = opts.get("fill",
                            HDR_BLUE if is_header else (BG_BOX if i % 2 else NAVY_2))
            color = opts.get("color", WHITE)
            bold = opts.get("bold", is_header)
            italic = opts.get("italic", False)
            size = opts.get("size", 13 if not is_header else 14)
            align = opts.get("align", PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER)
            cell_format(cell, fill=fill, color=color, size=size,
                        bold=bold, italic=italic, align=align)
    return tbl_shape

# ------------- Path helpers -------------
def P(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.isfile(p):
        print(f"WARNING: missing file {p}")
    return p

# ==================================================================
# SLIDE 1 — Title
# ==================================================================
s = prs.slides.add_slide(BLANK)
set_bg(s)
# Decorative diagonal accent
add_rect(s, 0, 0, SLIDE_W, Inches(0.12), fill=ACCENT)
add_rect(s, 0, Inches(7.38), SLIDE_W, Inches(0.12), fill=ACCENT)

# Top course info strip
add_text(s, Inches(0.4), Inches(0.4), Inches(12.5), Inches(0.35),
         "CSE638 — Graduate Systems (GRS)  •  Winter 2026  •  Instructor: Dr. Rinku Shah  •  IIIT-Delhi",
         size=14, color=GRAY_DIM, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# Main title
add_text(s, Inches(0.4), Inches(1.6), Inches(12.5), Inches(1.1),
         "Benchmarking Kubernetes CNI Plugins",
         size=48, bold=True, color=WHITE, align=PP_ALIGN.CENTER, font=TITLE_FONT)
add_text(s, Inches(0.4), Inches(2.55), Inches(12.5), Inches(0.7),
         "A Cross-Environment Performance Study",
         size=28, bold=False, color=ACCENT, align=PP_ALIGN.CENTER, font=TITLE_FONT)
add_text(s, Inches(0.4), Inches(3.25), Inches(12.5), Inches(0.5),
         "Kind-Cluster (Intra-Node)  vs.  Bare-Metal (Multi-Node WiFi)",
         size=20, italic=True, color=GRAY, align=PP_ALIGN.CENTER, font=TITLE_FONT)

# Separator
add_rect(s, Inches(4.5), Inches(4.0), Inches(4.3), Inches(0.04), fill=ACCENT)

# Team block
add_text(s, Inches(0.4), Inches(4.2), Inches(12.5), Inches(0.4),
         "Team — Group 1",
         size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
team_left = [
    "Yash Kumar Vaibhav        MT25091",
    "Nishit Jain                      MT25004",
    "Prakhar Agarwal             MT25005",
]
team_right = [
    "Reehan Sarmah              MT25036",
    "Samyak Kr. Sharma        MT25039",
]
add_bullets(s, Inches(2.5), Inches(4.75), Inches(4.3), Inches(1.4),
            team_left, size=15, color=GRAY, bullet="")
add_bullets(s, Inches(7.2), Inches(4.75), Inches(4.3), Inches(1.4),
            team_right, size=15, color=GRAY, bullet="")

# Repo link
add_rect(s, Inches(3.0), Inches(6.55), Inches(7.3), Inches(0.5), fill=NAVY_2, corner=True)
add_text(s, Inches(3.0), Inches(6.55), Inches(7.3), Inches(0.5),
         "github.com/yashkumarvaibhav/GrS-CSE638_Project",
         size=14, color=ACCENT, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

add_footer(s, 1)

# ==================================================================
# SLIDE 2 — Problem & Motivation
# ==================================================================
s = prs.slides.add_slide(BLANK)
set_bg(s)
add_title_bar(s, "Why Benchmark CNI Plugins?", kicker="Problem & motivation")

bullets = [
    "Kubernetes relies on CNI plugins for all pod networking — the choice directly shapes performance.",
    "Existing benchmarks test either simulated (kind) environments OR production-wired clusters.",
    [("No study compares the same CNIs across fundamentally different environments.",
      {"bold": True, "color": WHITE, "size": 18})],
    "Edge / WiFi deployments are growing rapidly — performance implications are largely unknown.",
    [("We bridge this gap: ", {"color": GRAY, "size": 18}),
     ("same 3 CNIs × same tools × 2 contrasting environments.", {"bold": True, "color": ACCENT, "size": 18})],
]
add_bullets(s, Inches(0.7), Inches(1.5), Inches(12.0), Inches(4.0),
            bullets, size=18, color=GRAY, space_after=12)

# Key message box
add_rect(s, Inches(1.2), Inches(5.8), Inches(10.9), Inches(1.1),
         fill=NAVY_3, line=ACCENT, corner=True)
add_text(s, Inches(1.2), Inches(5.8), Inches(10.9), Inches(1.1),
         "\u201CCNI rankings are NOT universal — they depend heavily on the deployment environment.\u201D",
         size=20, bold=True, italic=True, color=ACCENT,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

add_footer(s, 2)

# ==================================================================
# SLIDE 3 — Scope & Methodology
# ==================================================================
s = prs.slides.add_slide(BLANK)
set_bg(s)
add_title_bar(s, "What We Did", kicker="Scope & methodology")

# Two-column comparison
scope_rows = [
    ["", "Part A — Kind-Cluster", "Part B — Bare-Metal"],
    ["Hardware",   "Single 128-core AMD EPYC VM", "3 physical laptops (WiFi)"],
    ["Network",    "Docker bridge (intra-node)",  "802.11ac/ax shared LAN"],
    ["Bandwidth",  "~60 Gbps bandwidth headroom", "~100\u2013200 Mbps usable"],
    ["Measures",   "CNI software efficiency",     "Real physical-network constraints"],
]
build_table(s, Inches(0.7), Inches(1.4), Inches(12.0), Inches(2.2), scope_rows)

# CNIs strip
add_rect(s, Inches(0.7), Inches(3.85), Inches(12.0), Inches(1.25), fill=NAVY_2, corner=True)
add_text(s, Inches(0.7), Inches(3.9), Inches(12.0), Inches(0.35),
         "CNIs Tested",
         size=14, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
cni_runs = [[
    ("Flannel ", {"bold": True, "size": 16, "color": WHITE}),
    ("(VXLAN + Host-GW)  —  lightweight, simple", {"size": 15, "color": GRAY}),
]]
add_bullets(s, Inches(1.0), Inches(4.25), Inches(11.5), Inches(0.3),
            cni_runs, size=15, color=GRAY, bullet="\u25CF  ", space_after=2)
cni_runs = [[
    ("Calico ", {"bold": True, "size": 16, "color": WHITE}),
    ("(VXLAN + BGP)  —  iptables-based, policy-rich", {"size": 15, "color": GRAY}),
]]
add_bullets(s, Inches(1.0), Inches(4.55), Inches(11.5), Inches(0.3),
            cni_runs, size=15, color=GRAY, bullet="\u25CF  ", space_after=2)
cni_runs = [[
    ("Cilium ", {"bold": True, "size": 16, "color": WHITE}),
    ("(VXLAN + Native Routing / Underlay)  —  eBPF-based, advanced", {"size": 15, "color": GRAY}),
]]
add_bullets(s, Inches(1.0), Inches(4.85), Inches(11.5), Inches(0.3),
            cni_runs, size=15, color=GRAY, bullet="\u25CF  ", space_after=2)

# Tools strip
add_rect(s, Inches(0.7), Inches(5.35), Inches(5.9), Inches(1.55), fill=BG_BOX, corner=True)
add_text(s, Inches(0.7), Inches(5.4), Inches(5.9), Inches(0.35),
         "Tools",
         size=14, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
tools_bul = [
    "iperf3 — TCP & UDP throughput",
    "netperf — TCP_RR request / response latency",
    "fortio — HTTP load testing, P50 / P99",
    "kubectl top / docker stats — CPU & memory",
]
add_bullets(s, Inches(0.95), Inches(5.75), Inches(5.5), Inches(1.2),
            tools_bul, size=12, color=GRAY, bullet="\u25B8  ", space_after=2)

# Topologies strip
add_rect(s, Inches(6.8), Inches(5.35), Inches(5.9), Inches(1.55), fill=BG_BOX, corner=True)
add_text(s, Inches(6.8), Inches(5.4), Inches(5.9), Inches(0.35),
         "Test Topologies",
         size=14, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
topo_bul = [
    [("Kind:", {"bold": True, "color": WHITE, "size": 12}),
     (" Same-node (T1), Cross-node (T2), ClusterIP (T3)", {"size": 12, "color": GRAY})],
    [("BM:", {"bold": True, "color": WHITE, "size": 12}),
     (" 6 configs = 3 CNIs × 2 modes (overlay + underlay)", {"size": 12, "color": GRAY})],
    [("Reps:", {"bold": True, "color": WHITE, "size": 12}),
     (" 5 repetitions each (Calico BGP: 4)", {"size": 12, "color": GRAY})],
    [("Extensions:", {"bold": True, "color": WHITE, "size": 12}),
     (" E1 NetPol, E2 WireGuard, E3 Cilium KPR", {"size": 12, "color": GRAY})],
]
add_bullets(s, Inches(7.05), Inches(5.75), Inches(5.5), Inches(1.2),
            topo_bul, size=12, color=GRAY, bullet="\u25B8  ", space_after=2)

add_footer(s, 3)

# ==================================================================
# SLIDE 4 — Kind: Throughput & Latency
# ==================================================================
s = prs.slides.add_slide(BLANK)
set_bg(s)
add_title_bar(s, "Part A Results — Throughput & Latency",
              kicker="Kind-Cluster (Intra-Node)")

# Left half table
add_text(s, Inches(0.5), Inches(1.45), Inches(6.0), Inches(0.35),
         "TCP Throughput (Gbps, iperf3, 1MB)",
         size=15, bold=True, color=ACCENT)
thr_rows = [
    ["Topology",          "Flannel", "Calico", "Cilium"],
    ["Same-Node (T1)",    "60.93", "49.61", ("63.98", {"fill": WIN_GREEN, "color": NAVY, "bold": True})],
    ["Cross-Node (T2)",   ("30.96", {"fill": WIN_GREEN, "color": NAVY, "bold": True}), "23.83", "27.40"],
    ["ClusterIP (T3)",    ("34.13", {"fill": WIN_GREEN, "color": NAVY, "bold": True}), "24.11", "32.42"],
]
build_table(s, Inches(0.5), Inches(1.85), Inches(6.2), Inches(2.0), thr_rows)

add_text(s, Inches(0.5), Inches(4.0), Inches(6.2), Inches(0.5),
         "Cilium leads same-node  •  Flannel leads cross-node",
         size=14, italic=True, color=GRAY, align=PP_ALIGN.CENTER)

# Concurrency footnote
add_text(s, Inches(0.5), Inches(4.4), Inches(6.2), Inches(0.4),
         "\u2020 Values shown at the concurrency level where each topology peaks.",
         size=11, italic=True, color=GRAY_DIM, align=PP_ALIGN.CENTER)

# Latency callout
add_rect(s, Inches(0.5), Inches(5.0), Inches(6.2), Inches(1.85), fill=NAVY_3, line=ACCENT, corner=True)
add_text(s, Inches(0.6), Inches(5.1), Inches(6.0), Inches(0.4),
         "TCP_RR Latency (T2, 64B, netperf)",
         size=14, bold=True, color=ACCENT)
lat_runs = [
    [("Flannel", {"bold": True, "size": 15, "color": WIN_GREEN}),
     ("    24.18 \u00B5s    ", {"size": 15, "color": WHITE}),
     ("\u2248", {"size": 15, "color": GRAY_DIM}),
     ("    Cilium", {"bold": True, "size": 15, "color": ACCENT}),
     ("    24.63 \u00B5s", {"size": 15, "color": WHITE})],
    [("Calico", {"bold": True, "size": 15, "color": LOSE_RED}),
     ("    32.91 \u00B5s  ", {"size": 15, "color": WHITE}),
     ("(\u2191 36% vs. Flannel)", {"italic": True, "size": 13, "color": GRAY_DIM})],
]
add_rich(s, Inches(0.7), Inches(5.5), Inches(5.9), Inches(1.3), lat_runs,
         anchor=MSO_ANCHOR.MIDDLE)

# Right half — latency plot
s.shapes.add_picture(P("kind-cluster/plots/1_latency_comparison.png"),
                     Inches(7.0), Inches(1.45), width=Inches(6.0), height=Inches(5.4))

add_footer(s, 4)

# ==================================================================
# SLIDE 5 — Kind: HTTP & Extensions
# ==================================================================
s = prs.slides.add_slide(BLANK)
set_bg(s)
add_title_bar(s, "Part A — HTTP Performance & Security Extensions",
              kicker="Kind-Cluster (Intra-Node)")

# Top row: HTTP QPS boxes (fortio, 64B, c=16, T2)
add_text(s, Inches(0.5), Inches(1.35), Inches(12.3), Inches(0.35),
         "HTTP QPS  —  fortio, 64 B payload, concurrency = 16, topology T2",
         size=14, bold=True, color=ACCENT)

def qps_box(x, label, value, sub, color=WHITE, fill=BG_BOX):
    add_rect(s, x, Inches(1.75), Inches(3.9), Inches(1.6), fill=fill, corner=True)
    add_text(s, x, Inches(1.82), Inches(3.9), Inches(0.35),
             label, size=16, bold=True, color=color, align=PP_ALIGN.CENTER)
    add_text(s, x, Inches(2.2), Inches(3.9), Inches(0.7),
             value, size=30, bold=True, color=color, align=PP_ALIGN.CENTER)
    add_text(s, x, Inches(2.95), Inches(3.9), Inches(0.35),
             sub, size=11, italic=True, color=GRAY_DIM, align=PP_ALIGN.CENTER)

qps_box(Inches(0.5),  "Cilium",  "132,836 QPS", "eBPF fast-path", color=WIN_GREEN)
qps_box(Inches(4.7),  "Flannel", "81,749 QPS",  "baseline",       color=WHITE)
qps_box(Inches(8.9),  "Calico",  "74,792 QPS",  "lowest of three", color=LOSE_RED)

# WireGuard table
add_text(s, Inches(0.5), Inches(3.6), Inches(12.3), Inches(0.35),
         "Extension E2 — WireGuard Encryption Cost",
         size=14, bold=True, color=ACCENT)
wg_rows = [
    ["Metric",              "Calico",                                                      "Cilium"],
    ["Throughput loss",     ("\u221276%", {"fill": LOSE_RED, "color": WHITE, "bold": True}),  ("\u221247%", {"fill": WARN, "color": NAVY, "bold": True})],
    ["Latency increase",    ("+537%", {"fill": LOSE_RED, "color": WHITE, "bold": True}),  ("+365%", {"fill": WARN, "color": NAVY, "bold": True})],
]
build_table(s, Inches(0.5), Inches(3.95), Inches(7.5), Inches(1.4), wg_rows)

add_text(s, Inches(0.5), Inches(5.4), Inches(7.5), Inches(0.4),
         "Cilium's eBPF mitigates encryption overhead better.",
         size=13, italic=True, color=GRAY)

# Right side: NetworkPolicy insight + plot
add_rect(s, Inches(8.3), Inches(3.95), Inches(4.7), Inches(2.5),
         fill=NAVY_3, line=ACCENT, corner=True)
add_text(s, Inches(8.4), Inches(4.05), Inches(4.5), Inches(0.35),
         "Extension E1 — NetworkPolicy",
         size=13, bold=True, color=ACCENT)
np_runs = [
    [("Calico:", {"bold": True, "size": 14, "color": LOSE_RED}),
     (" throughput \u221245%", {"size": 14, "color": WHITE})],
    [("Cilium:", {"bold": True, "size": 14, "color": WIN_GREEN}),
     (" throughput +118%\u2020", {"size": 14, "color": WHITE})],
    [("eBPF handles policy in-kernel, avoiding iptables overhead.",
      {"italic": True, "size": 11, "color": GRAY_DIM})],
    [("\u2020 High CV on Cilium (\u223C57%) — directional only.",
      {"italic": True, "size": 10, "color": GRAY_DIM})],
]
add_rich(s, Inches(8.45), Inches(4.4), Inches(4.5), Inches(2.0), np_runs)

# Source bullet
add_text(s, Inches(0.5), Inches(5.85), Inches(12.3), Inches(0.4),
         "Plot reference: kind-cluster/plots/1_network_policy_overhead.png",
         size=10, italic=True, color=GRAY_DIM)

add_footer(s, 5)

# ==================================================================
# SLIDE 6 — Kind: Resource Overhead
# ==================================================================
s = prs.slides.add_slide(BLANK)
set_bg(s)
add_title_bar(s, "Part A — CPU & Memory Overhead",
              kicker="Kind-Cluster (Intra-Node)")

# Two plots side by side
add_text(s, Inches(0.5), Inches(1.3), Inches(6.0), Inches(0.3),
         "Memory Overhead (MiB)", size=13, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
s.shapes.add_picture(P("kind-cluster/plots/1_memory_overhead.png"),
                     Inches(0.5), Inches(1.65), width=Inches(6.0), height=Inches(3.8))

add_text(s, Inches(6.8), Inches(1.3), Inches(6.0), Inches(0.3),
         "CPU Overhead (%)", size=13, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
s.shapes.add_picture(P("kind-cluster/plots/1_cpu_overhead.png"),
                     Inches(6.8), Inches(1.65), width=Inches(6.0), height=Inches(3.8))

# Callouts below
add_rect(s, Inches(0.5), Inches(5.65), Inches(12.3), Inches(1.4),
         fill=NAVY_2, corner=True)
callouts = [
    [("Memory:", {"bold": True, "size": 14, "color": ACCENT}),
     ("  Flannel 389\u2013430 MiB  |  Calico & Cilium 969\u20131,049 MiB  ",
      {"size": 14, "color": WHITE}),
     ("(2.4\u20132.6\u00D7 more)", {"italic": True, "size": 13, "color": GRAY_DIM})],
    [("CPU baseline:", {"bold": True, "size": 14, "color": ACCENT}),
     ("  Similar across CNIs (~101\u2013117%)", {"size": 14, "color": WHITE})],
    [("WireGuard CPU:", {"bold": True, "size": 14, "color": ACCENT}),
     ("  Drops to 46\u201363%  ", {"size": 14, "color": WHITE}),
     ("(encryption throttles; network is the bottleneck, not CPU)",
      {"italic": True, "size": 12, "color": GRAY_DIM})],
]
add_rich(s, Inches(0.7), Inches(5.75), Inches(11.9), Inches(1.25), callouts,
         anchor=MSO_ANCHOR.MIDDLE)

add_footer(s, 6)

# ==================================================================
# SLIDE 7 — Bare-Metal: Throughput
# ==================================================================
s = prs.slides.add_slide(BLANK)
set_bg(s)
add_title_bar(s, "Part B Results — Throughput on WiFi",
              kicker="Bare-Metal Cluster")

# Large throughput plot on left
s.shapes.add_picture(P("bare-metal-cluster/plots/1_throughput_comparison.png"),
                     Inches(0.5), Inches(1.35), width=Inches(8.0), height=Inches(4.7))

# Callout numbers on right
callouts_x = Inches(8.8)
add_text(s, callouts_x, Inches(1.35), Inches(4.3), Inches(0.35),
         "Key Numbers (Gbps)", size=14, bold=True, color=ACCENT)

def num_row(y, cni, val, note, color=WHITE, fill=BG_BOX):
    add_rect(s, callouts_x, y, Inches(4.3), Inches(0.7), fill=fill, corner=True)
    add_text(s, callouts_x + Inches(0.2), y, Inches(2.2), Inches(0.7),
             cni, size=13, bold=True, color=color, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, callouts_x + Inches(2.3), y, Inches(1.0), Inches(0.7),
             val, size=16, bold=True, color=color, align=PP_ALIGN.RIGHT,
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, callouts_x + Inches(0.2), y + Inches(0.72), Inches(4.0), Inches(0.2),
             note, size=10, italic=True, color=GRAY_DIM)

num_row(Inches(1.75), "Flannel VXLAN",  "0.118", "")
num_row(Inches(2.65), "Calico VXLAN",   "0.119", "virtual tie")
num_row(Inches(3.55), "Cilium VXLAN",   "0.058", "half the others!", color=LOSE_RED)
num_row(Inches(4.45), "Cilium Underlay","0.102", "+77% over its own VXLAN", color=WIN_GREEN)

# Headline quote box
add_rect(s, Inches(0.5), Inches(6.25), Inches(12.3), Inches(0.85),
         fill=NAVY_3, line=ACCENT, corner=True)
add_text(s, Inches(0.5), Inches(6.25), Inches(12.3), Inches(0.85),
         "\u201CWiFi compresses all CNIs into a narrow 0.06\u20130.12 Gbps band — 262\u2013472\u00D7 slower than kind-cluster.\u201D",
         size=16, bold=True, italic=True, color=ACCENT,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

add_footer(s, 7)

# ==================================================================
# SLIDE 8 — Bare-Metal: Latency & The Surprise
# ==================================================================
s = prs.slides.add_slide(BLANK)
set_bg(s)
add_title_bar(s, "Part B — The Throughput\u2013Latency Inversion",
              kicker="Bare-Metal Cluster")

# Left: fortio comparison plot
s.shapes.add_picture(P("bare-metal-cluster/plots/1_fortio_comparison.png"),
                     Inches(0.5), Inches(1.4), width=Inches(6.3), height=Inches(4.3))

# Right: percentile table
add_text(s, Inches(7.0), Inches(1.4), Inches(6.0), Inches(0.3),
         "Fortio HTTP Latency — VXLAN mode",
         size=14, bold=True, color=ACCENT)
pct_rows = [
    ["Percentile", "Cilium VXLAN", "Flannel VXLAN", "Calico VXLAN"],
    ["P50",  ("6.56 ms", {"fill": WIN_GREEN, "color": NAVY, "bold": True}),  "9.26",  "9.23"],
    ["P99",  ("27.75 ms", {"fill": WIN_GREEN, "color": NAVY, "bold": True}), "38.77", "46.21"],
    ["Max",  ("38.72 ms", {"fill": WIN_GREEN, "color": NAVY, "bold": True}), "188.54", "248.93"],
]
build_table(s, Inches(7.0), Inches(1.75), Inches(6.0), Inches(2.2), pct_rows)

# Key insight box spanning bottom
add_rect(s, Inches(0.5), Inches(6.0), Inches(12.3), Inches(1.1),
         fill=NAVY_3, line=WARN, corner=True)
add_text(s, Inches(0.65), Inches(6.05), Inches(12.0), Inches(0.4),
         "\u26A1  Cilium VXLAN: WORST throughput (0.058 Gbps) but BEST HTTP latency (P50: 6.56 ms)",
         size=16, bold=True, color=WARN)
insight = [
    [("\u25B8  TCP throughput", {"bold": True, "size": 12, "color": WHITE}),
     (" = sustained bandwidth  \u2192  per-packet eBPF overhead accumulates.",
      {"size": 12, "color": GRAY})],
    [("\u25B8  HTTP latency", {"bold": True, "size": 12, "color": WHITE}),
     (" = individual request\u2013response  \u2192  eBPF's O(1) connection tracking wins per-request.",
      {"size": 12, "color": GRAY})],
]
add_rich(s, Inches(0.7), Inches(6.45), Inches(12.0), Inches(0.65), insight)

# Supporting notes on right under table
notes = [
    [("Max-latency gap:", {"bold": True, "size": 12, "color": ACCENT}),
     (" Cilium 38.72 ms vs. Calico 248.93 ms \u2192 Calico 6.4\u00D7 worse on tail.",
      {"size": 12, "color": GRAY})],
    [("Cilium Underlay P50:", {"bold": True, "size": 12, "color": ACCENT}),
     (" 11.54 ms (higher than Cilium VXLAN)  \u2192  underlay \u2260 lower latency on WiFi.",
      {"size": 12, "color": GRAY})],
]
add_rich(s, Inches(7.0), Inches(4.1), Inches(6.0), Inches(1.7), notes)

add_footer(s, 8)

# ==================================================================
# SLIDE 9 — Bare-Metal: Overlay vs Underlay + UDP
# ==================================================================
s = prs.slides.add_slide(BLANK)
set_bg(s)
add_title_bar(s, "Part B — Routing Modes & UDP Performance",
              kicker="Bare-Metal Cluster")

# Top half — plot + table side by side
s.shapes.add_picture(P("bare-metal-cluster/plots/1_encapsulation_comparison.png"),
                     Inches(0.5), Inches(1.3), width=Inches(6.8), height=Inches(3.7))

add_text(s, Inches(7.5), Inches(1.3), Inches(5.5), Inches(0.3),
         "VXLAN  \u2192  Native Routing / Underlay",
         size=13, bold=True, color=ACCENT)
ovl_rows = [
    ["CNI", "VXLAN", "Underlay", "Change"],
    ["Flannel", "0.118", "0.088\u2020", ("\u221225%",  {"fill": LOSE_RED, "color": WHITE, "bold": True})],
    ["Calico",  "0.119", "0.116",     ("\u22122%  (tie)", {"color": GRAY, "bold": True})],
    ["Cilium",  "0.058", "0.102",     ("+77%", {"fill": WIN_GREEN, "color": NAVY, "bold": True})],
]
build_table(s, Inches(7.5), Inches(1.65), Inches(5.5), Inches(2.0), ovl_rows)
add_text(s, Inches(7.5), Inches(3.75), Inches(5.5), Inches(0.5),
         "\u2020 Flannel Host-GW run includes cold-start (CV 55.7%).",
         size=10, italic=True, color=GRAY_DIM)
add_text(s, Inches(7.5), Inches(4.1), Inches(5.5), Inches(0.6),
         "Underlay advantage is CNI-specific — not universal.",
         size=13, italic=True, color=GRAY)

# Bottom half — UDP
add_rect(s, Inches(0.5), Inches(5.15), Inches(12.3), Inches(1.95),
         fill=NAVY_2, corner=True)
add_text(s, Inches(0.7), Inches(5.2), Inches(12.0), Inches(0.35),
         "UDP Highlights (iperf3 UDP, targets 10 / 25 / 50 Mbps)",
         size=14, bold=True, color=ACCENT)
udp_bul = [
    [("Calico BGP leads \u2014 ", {"bold": True, "size": 14, "color": WIN_GREEN}),
     ("11.88 Mbps mean, 38% mean loss across all targets.",
      {"size": 14, "color": WHITE})],
    [("At 10 Mbps target:", {"bold": True, "size": 14, "color": ACCENT}),
     (" Calico BGP reaches ", {"size": 14, "color": WHITE}),
     ("\u22640.15% loss  (mean ~0.11%, near-perfect).",
      {"bold": True, "size": 14, "color": WIN_GREEN})],
    [("At 50 Mbps:", {"bold": True, "size": 14, "color": WARN}),
     (" WiFi saturates \u2014 all CNIs hit ", {"size": 14, "color": WHITE}),
     ("54\u201382% packet loss.", {"bold": True, "size": 14, "color": LOSE_RED})],
]
add_rich(s, Inches(0.7), Inches(5.6), Inches(12.0), Inches(1.45), udp_bul)

add_footer(s, 9)

# ==================================================================
# SLIDE 10 — Cross-Environment
# ==================================================================
s = prs.slides.add_slide(BLANK)
set_bg(s)
add_title_bar(s, "Cross-Environment Analysis — Ranking Inversions",
              kicker="Does the winner change with the environment?")

# First table: ranking
rank_rows = [
    ["Metric",          "Kind-Cluster Winner", "Bare-Metal WiFi Winner", "Ranking Inverted?"],
    ["TCP Throughput",  ("Cilium",     {"fill": WIN_GREEN, "color": NAVY, "bold": True}),
                        ("Calico \u2248 Flannel", {"fill": WIN_GREEN, "color": NAVY, "bold": True}),
                        ("\u2705  YES", {"bold": True, "color": WIN_GREEN})],
    ["Latency (TCP_RR)",("Flannel \u2248 Cilium", {"fill": WIN_GREEN, "color": NAVY, "bold": True}),
                        ("Flannel", {"fill": WIN_GREEN, "color": NAVY, "bold": True}),
                        ("Partial", {"color": WARN, "bold": True})],
    ["HTTP Performance",("Cilium",     {"fill": WIN_GREEN, "color": NAVY, "bold": True}),
                        ("Cilium VXLAN", {"fill": WIN_GREEN, "color": NAVY, "bold": True}),
                        ("\u274C  NO  (intrinsic)", {"bold": True, "color": GRAY})],
    ["CPU Overhead",    ("~Equal", {"color": GRAY}),
                        ("Flannel  (3.9%)", {"fill": WIN_GREEN, "color": NAVY, "bold": True}),
                        ("\u2014", {"color": GRAY_DIM})],
]
build_table(s, Inches(0.5), Inches(1.35), Inches(12.3), Inches(2.4), rank_rows)

# Second table: throughput scaling ratio
add_text(s, Inches(0.5), Inches(3.95), Inches(12.3), Inches(0.35),
         "Throughput Scaling  —  Kind T2 vs. Bare-Metal WiFi",
         size=14, bold=True, color=ACCENT)
scale_rows = [
    ["CNI",     "Kind T2 (Gbps)", "BM WiFi (Gbps)", "Ratio"],
    ["Flannel", "30.96", "0.118", "262\u00D7"],
    ["Calico",  "23.83", "0.119", "200\u00D7"],
    ["Cilium",  "27.40", "0.058", ("472\u00D7  \u26A0", {"fill": WARN, "color": NAVY, "bold": True})],
]
build_table(s, Inches(0.5), Inches(4.35), Inches(12.3), Inches(2.0), scale_rows)

# Insight line
add_rect(s, Inches(0.5), Inches(6.5), Inches(12.3), Inches(0.55), fill=NAVY_3, corner=True)
add_text(s, Inches(0.5), Inches(6.5), Inches(12.3), Inches(0.55),
         "Cilium's 472\u00D7 ratio  \u2192  eBPF per-packet overhead amplifies on slow links.",
         size=14, italic=True, bold=True, color=ACCENT,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

add_footer(s, 10)

# ==================================================================
# SLIDE 11 — Edge Environment Paradox
# ==================================================================
s = prs.slides.add_slide(BLANK)
set_bg(s)
add_title_bar(s, "Key Insight — The Edge Environment Paradox",
              kicker="Why simplicity beats sophistication on constrained links")

# Central quote
add_rect(s, Inches(1.5), Inches(1.5), Inches(10.3), Inches(1.3),
         fill=NAVY_3, line=ACCENT, corner=True)
add_text(s, Inches(1.5), Inches(1.5), Inches(10.3), Inches(1.3),
         "\u201CIn resource-constrained environments,  simplicity outperforms sophistication.\u201D",
         size=22, bold=True, italic=True, color=ACCENT,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# Three supporting points with icons
def point_card(x, icon, title, body, color):
    add_rect(s, x, Inches(3.1), Inches(3.95), Inches(2.5), fill=BG_BOX, corner=True)
    add_text(s, x, Inches(3.2), Inches(3.95), Inches(0.55),
             icon, size=28, color=color, align=PP_ALIGN.CENTER)
    add_text(s, x, Inches(3.8), Inches(3.95), Inches(0.4),
             title, size=14, bold=True, color=color, align=PP_ALIGN.CENTER)
    add_text(s, x, Inches(4.25), Inches(3.95), Inches(1.3),
             body, size=12, color=GRAY, align=PP_ALIGN.CENTER)

point_card(Inches(0.6),
           "\U0001F527",
           "Flannel's Minimalism",
           "Consistent, reliable throughput on WiFi. Low CPU (3.9%). "
           "No control plane overhead, no eBPF taxes.",
           WIN_GREEN)
point_card(Inches(4.7),
           "\u26A1",
           "Cilium's eBPF",
           "Shines on fast links. On slow links, per-packet hooks dominate "
           "and negate the shortcut advantage.",
           WARN)
point_card(Inches(8.8),
           "\U0001F500",
           "Cilium Underlay Penalty",
           "111 trans/sec (Underlay) < 163 trans/sec (VXLAN). "
           "Security-identity checks fire on every packet.",
           LOSE_RED)

# Implication box
add_rect(s, Inches(0.5), Inches(5.85), Inches(12.3), Inches(1.15),
         fill=NAVY_3, line=WARN, corner=True)
add_text(s, Inches(0.5), Inches(5.85), Inches(12.3), Inches(1.15),
         "Implication  \u2192  CNI selection MUST be validated on representative hardware. "
         "Kind-cluster results do NOT predict edge / WiFi behavior.",
         size=15, bold=True, color=WARN,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

add_footer(s, 11)

# ==================================================================
# SLIDE 12 — Decision Matrix
# ==================================================================
s = prs.slides.add_slide(BLANK)
set_bg(s)
add_title_bar(s, "Practical Recommendations",
              kicker="CNI decision matrix by use-case")

dec_rows = [
    ["Use Case",                          "Recommended CNI",                                                      "Rationale"],
    ["Constrained / WiFi network",        ("Flannel VXLAN",    {"fill": WIN_GREEN, "color": NAVY, "bold": True}), "Lowest CPU (3.9%), consistent throughput"],
    ["Latency-critical microservices",    ("Cilium VXLAN",     {"fill": WIN_GREEN, "color": NAVY, "bold": True}), "Best P99 (27.75 ms), lowest Max (38.72 ms)"],
    ["High throughput (wired DC)\u2020",  ("Cilium Underlay",  {"fill": WIN_GREEN, "color": NAVY, "bold": True}), "+77% over VXLAN on bare-metal (extrapolated)"],
    ["UDP-heavy workloads",               ("Calico BGP",       {"fill": WIN_GREEN, "color": NAVY, "bold": True}), "Best UDP throughput; \u22640.15% loss at 10 Mbps"],
    ["Security-critical",                 ("Cilium",           {"fill": WIN_GREEN, "color": NAVY, "bold": True}), "Lower WireGuard overhead (\u221247% vs. \u221276%)"],
    ["Large-scale clusters",              ("Cilium KPR",       {"fill": WIN_GREEN, "color": NAVY, "bold": True}), "Bypasses iptables rule explosion"],
    ["Lowest complexity",                 ("Flannel VXLAN",    {"fill": WIN_GREEN, "color": NAVY, "bold": True}), "No BGP / eBPF, minimal control plane"],
]
build_table(s, Inches(0.5), Inches(1.4), Inches(12.3), Inches(5.3), dec_rows)

add_text(s, Inches(0.5), Inches(6.8), Inches(12.3), Inches(0.3),
         "\u2020 Wired bare-metal validation is Future Work; the +77% figure is measured on WiFi.",
         size=11, italic=True, color=GRAY_DIM)

add_footer(s, 12)

# ==================================================================
# SLIDE 13 — Conclusion & Future Work
# ==================================================================
s = prs.slides.add_slide(BLANK)
set_bg(s)
add_title_bar(s, "Conclusion", kicker="Takeaways, future work, Q&A")

# Takeaways
add_text(s, Inches(0.5), Inches(1.3), Inches(12.3), Inches(0.35),
         "Key Takeaways", size=15, bold=True, color=ACCENT)
takeaways = [
    [("1.  ", {"bold": True, "size": 14, "color": ACCENT}),
     ("CNI rankings are environment-dependent", {"bold": True, "size": 14, "color": WHITE}),
     (" \u2014 Cilium leads on fast links; Flannel leads on WiFi.",
      {"size": 14, "color": GRAY})],
    [("2.  ", {"bold": True, "size": 14, "color": ACCENT}),
     ("Throughput\u2013Latency Inversion", {"bold": True, "size": 14, "color": WHITE}),
     (" \u2014 Cilium has worst throughput but best HTTP latency on WiFi "
      "(eBPF per-request advantage).",
      {"size": 14, "color": GRAY})],
    [("3.  ", {"bold": True, "size": 14, "color": ACCENT}),
     ("Overlay vs. Underlay is CNI-specific", {"bold": True, "size": 14, "color": WHITE}),
     (" \u2014 no universal winner; Cilium gains +77%, others break even or regress.",
      {"size": 14, "color": GRAY})],
    [("4.  ", {"bold": True, "size": 14, "color": ACCENT}),
     ("WireGuard encryption", {"bold": True, "size": 14, "color": WHITE}),
     (" is expensive everywhere (\u221247% to \u221276% throughput).",
      {"size": 14, "color": GRAY})],
    [("5.  ", {"bold": True, "size": 14, "color": ACCENT}),
     ("WiFi is a valid, underexplored", {"bold": True, "size": 14, "color": WHITE}),
     (" deployment environment for Kubernetes research.",
      {"size": 14, "color": GRAY})],
]
add_rich(s, Inches(0.7), Inches(1.7), Inches(12.0), Inches(3.3), takeaways)

# Divider
add_rect(s, Inches(0.5), Inches(5.05), Inches(12.3), Inches(0.03), fill=GRAY_DIM)

# Future Work
add_text(s, Inches(0.5), Inches(5.15), Inches(12.3), Inches(0.35),
         "Future Work", size=14, bold=True, color=ACCENT)
future_items = [
    "Wired bare-metal (1\u201310 GbE) to complete the environment spectrum",
    "eBPF tracing for per-packet overhead profiling",
    "Production workloads (microservice meshes) beyond synthetic benchmarks",
]
add_bullets(s, Inches(0.7), Inches(5.5), Inches(12.0), Inches(1.2),
            future_items, size=13, color=GRAY, bullet="\u25B8  ", space_after=3)

# Thank You
add_rect(s, Inches(3.5), Inches(6.55), Inches(6.3), Inches(0.55),
         fill=NAVY_3, line=ACCENT, corner=True)
add_text(s, Inches(3.5), Inches(6.55), Inches(6.3), Inches(0.55),
         "Thank You  \u2014  Questions?",
         size=20, bold=True, color=ACCENT,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

add_footer(s, 13)

# ------------- Save -------------
out_path = os.path.join(HERE, "1_presentation.pptx")
prs.save(out_path)
print(f"Wrote {out_path}")
print(f"Slide count: {len(prs.slides)}")
