# -*- coding: utf-8 -*-
"""
Generate a light-theme research animation for phase-geometric vibration analysis.

How to run:
    python generate_phase_geometric_vibration_animation.py

Outputs:
    outputs/phase_geometric_vibration_animation.mp4
    outputs/phase_geometric_vibration_animation.gif
    outputs/phase_geometric_vibration_preview.png

Notes:
    MP4/GIF export requires ffmpeg. On Windows, install it with:
        winget install --id Gyan.FFmpeg -e
    If system ffmpeg is unavailable, this script can use imageio-ffmpeg:
        python -m pip install imageio-ffmpeg
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
from pathlib import Path


def require_package(import_name: str, install_name: str | None = None) -> None:
    """Provide a clear setup message if a dependency is missing."""
    if importlib.util.find_spec(import_name) is None:
        package = install_name or import_name
        raise SystemExit(
            f"Missing Python package '{package}'. Install dependencies with:\n"
            "    python -m pip install numpy matplotlib pillow imageio-ffmpeg\n"
        )


require_package("numpy")
require_package("matplotlib")
require_package("PIL", "pillow")

import numpy as np

import matplotlib

matplotlib.use("Agg")

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle, Wedge


# ---------------------------------------------------------------------------
# Export settings
# ---------------------------------------------------------------------------

OUT_DIR = Path("outputs")
MP4_PATH = OUT_DIR / "phase_geometric_vibration_animation.mp4"
GIF_PATH = OUT_DIR / "phase_geometric_vibration_animation.gif"
PNG_PATH = OUT_DIR / "phase_geometric_vibration_preview.png"
PALETTE_PATH = OUT_DIR / "phase_geometric_vibration_palette.png"

FPS = 30
DURATION = 10.0
N_FRAMES = int(FPS * DURATION)
FIGSIZE = (19.2, 10.8)
DPI = 100


# ---------------------------------------------------------------------------
# Visual system
# ---------------------------------------------------------------------------

BG_TOP = np.array([0.985, 0.989, 0.992])
BG_BOTTOM = np.array([0.920, 0.940, 0.952])
INK = "#20303c"
SLATE = "#5d6d78"
MUTED = "#87959e"
GRID = "#d7e1e7"
PANEL_EDGE = "#d9e4ea"
PANEL_FACE = (1.0, 1.0, 1.0, 0.76)
TEAL = "#20aaa1"
TEAL_DARK = "#137f79"
AMBER = "#d98b42"
AMBER_DARK = "#a35e2a"
CORAL = "#d66e63"
NAVY = "#2d4354"
METAL = "#cfd8df"
METAL_DARK = "#84939d"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "figure.facecolor": "#eef4f7",
        "savefig.facecolor": "#eef4f7",
        "axes.facecolor": (1, 1, 1, 0),
        "axes.labelcolor": SLATE,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "text.color": INK,
    }
)


def smooth_array(x: np.ndarray, edge0: float, edge1: float) -> np.ndarray:
    """Vector cubic smooth-step."""
    u = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def style_plot_axis(ax: plt.Axes) -> None:
    """Clean, light scientific chart styling."""
    ax.grid(True, color=GRID, linewidth=0.8, alpha=0.72)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#b8c8d1")
        ax.spines[side].set_linewidth(0.9)
    ax.tick_params(length=3, width=0.8, colors=MUTED, labelsize=9)


def add_panel(bounds: tuple[float, float, float, float], radius: float = 0.018) -> None:
    """Subtle surface for one content region."""
    x, y, w, h = bounds
    shadow = FancyBboxPatch(
        (x + 0.004, y - 0.006),
        w,
        h,
        transform=fig.transFigure,
        boxstyle=f"round,pad=0.004,rounding_size={radius}",
        facecolor=(0.28, 0.36, 0.42, 0.045),
        edgecolor="none",
        zorder=-8,
    )
    panel = FancyBboxPatch(
        (x, y),
        w,
        h,
        transform=fig.transFigure,
        boxstyle=f"round,pad=0.004,rounding_size={radius}",
        facecolor=PANEL_FACE,
        edgecolor=PANEL_EDGE,
        linewidth=1.0,
        zorder=-7,
    )
    fig.patches.extend([shadow, panel])


# ---------------------------------------------------------------------------
# Synthetic response data with closed reduced-state loops
# ---------------------------------------------------------------------------

freq = np.linspace(0.0, 40.0, 900)
s = 2.0 * np.pi * freq / freq[-1]

E1 = np.array([0.34, 0.60, 0.80, 0.60, 0.34], dtype=float)
E1 = E1 / np.linalg.norm(E1)
E2 = np.array([-0.61, -0.34, 0.00, 0.34, 0.61], dtype=float)
E2 = E2 / np.linalg.norm(E2)


def lorentzian(f: np.ndarray, center: float, width: float, amp: float) -> np.ndarray:
    return amp / (1.0 + ((f - center) / width) ** 2)


def amplitude_response(f: np.ndarray, defect: bool = False) -> np.ndarray:
    """Amplitude curves remain close so the defect signature is modest."""
    if defect:
        amp = 0.12 + lorentzian(f, 12.22, 1.46, 0.89) + lorentzian(f, 26.02, 2.16, 0.56)
    else:
        amp = 0.12 + lorentzian(f, 12.00, 1.42, 0.91) + lorentzian(f, 26.26, 2.08, 0.55)
    return amp / amp.max()


amp_base = amplitude_response(freq, defect=False)
amp_def = amplitude_response(freq, defect=True)

# Periodic angular coordinates: both reduced-state trajectories close exactly.
theta_base_model = 0.95 + 0.25 * np.sin(s - 0.55) + 0.055 * np.sin(2.0 * s + 0.40)
theta_def_model = theta_base_model + 0.050 * np.sin(s) ** 2 - 0.035 * np.sin(2.0 * s - 0.15)
phi_base_model = s + 0.25 * np.sin(s + 0.30)
phi_def_model = s + 0.25 * np.sin(s + 0.30) + 0.58 * (1.0 - np.cos(s)) + 0.08 * np.sin(2.0 * s)

common_phase = -0.22 * np.sin(s - 0.2)
alpha_base_model = amp_base * np.cos(theta_base_model / 2.0) * np.exp(1j * common_phase)
beta_base_model = amp_base * np.sin(theta_base_model / 2.0) * np.exp(1j * (common_phase + phi_base_model))
alpha_def_model = amp_def * np.cos(theta_def_model / 2.0) * np.exp(1j * common_phase)
beta_def_model = amp_def * np.sin(theta_def_model / 2.0) * np.exp(1j * (common_phase + phi_def_model))

u_base = E1[:, None] * alpha_base_model[None, :] + E2[:, None] * beta_base_model[None, :]
u_def = E1[:, None] * alpha_def_model[None, :] + E2[:, None] * beta_def_model[None, :]

# Modal projection recovers alpha and beta from measured five-component response.
alpha_base = E1 @ u_base
beta_base = E2 @ u_base
alpha_def = E1 @ u_def
beta_def = E2 @ u_def


def normalize_state(alpha: np.ndarray, beta: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    norm = np.sqrt(np.abs(alpha) ** 2 + np.abs(beta) ** 2)
    return alpha / norm, beta / norm


alpha_base_n, beta_base_n = normalize_state(alpha_base, beta_base)
alpha_def_n, beta_def_n = normalize_state(alpha_def, beta_def)
theta_base = 2.0 * np.arctan2(np.abs(beta_base_n), np.abs(alpha_base_n))
theta_def = 2.0 * np.arctan2(np.abs(beta_def_n), np.abs(alpha_def_n))
phi_base = np.unwrap(np.angle(beta_base_n) - np.angle(alpha_base_n))
phi_def = np.unwrap(np.angle(beta_def_n) - np.angle(alpha_def_n))


def sphere_xyz(theta: np.ndarray, phi: np.ndarray) -> np.ndarray:
    return np.column_stack([np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)])


def project_sphere(points: np.ndarray) -> np.ndarray:
    """Project 3D sphere coordinates to a clean editorial 2D view."""
    az = np.deg2rad(-36.0)
    x, y, z = points[:, 0], points[:, 1], points[:, 2]
    xr = x * np.cos(az) - y * np.sin(az)
    yr = x * np.sin(az) + y * np.cos(az)
    return np.column_stack([0.98 * xr, 0.70 * z + 0.23 * yr])


traj_base = project_sphere(sphere_xyz(theta_base, phi_base))
traj_def = project_sphere(sphere_xyz(theta_def, phi_def))
response_scale = 0.058 / np.max(np.abs(u_base))


# ---------------------------------------------------------------------------
# Figure and panels
# ---------------------------------------------------------------------------

fig = plt.figure(figsize=FIGSIZE, dpi=DPI, facecolor="#eef4f7")

ax_bg = fig.add_axes([0, 0, 1, 1], zorder=-100)
ax_bg.set_axis_off()
yy, xx = np.mgrid[0:1:540j, 0:1:960j]
bg = BG_BOTTOM * (1.0 - yy[..., None]) + BG_TOP * yy[..., None]
bg += 0.018 * np.exp(-(((xx - 0.20) / 0.45) ** 2 + ((yy - 0.68) / 0.42) ** 2))[..., None] * np.array(
    [0.72, 0.93, 0.90]
)
bg += 0.018 * np.exp(-(((xx - 0.82) / 0.35) ** 2 + ((yy - 0.43) / 0.55) ** 2))[..., None] * np.array(
    [0.94, 0.87, 0.78]
)
ax_bg.imshow(np.clip(bg, 0, 1), origin="lower", aspect="auto", extent=[0, 1, 0, 1])

fig.text(0.055, 0.938, "Phase–Geometric Vibration Analysis", fontsize=27, fontweight="bold", color=INK, ha="left")
fig.text(0.057, 0.902, "from measured vibration response to modal-state trajectories", fontsize=12.5, color=SLATE, ha="left")

AMP_PANEL = (0.055, 0.620, 0.345, 0.255)
PHASE_PANEL = (0.055, 0.350, 0.345, 0.235)
MECH_PANEL = (0.055, 0.070, 0.580, 0.240)
PROJ_PANEL = (0.425, 0.350, 0.260, 0.525)
STATE_PANEL = (0.710, 0.070, 0.245, 0.805)

for panel in (AMP_PANEL, PHASE_PANEL, MECH_PANEL, PROJ_PANEL, STATE_PANEL):
    add_panel(panel)


# ---------------------------------------------------------------------------
# Panel B: amplitude response
# ---------------------------------------------------------------------------

fig.text(0.075, 0.842, "Amplitude response", fontsize=13.8, fontweight="bold", color=INK, ha="left")
fig.text(0.075, 0.815, "Only a modest visible change", fontsize=9.8, color=SLATE, ha="left")

ax_amp = fig.add_axes([0.083, 0.660, 0.292, 0.120])
style_plot_axis(ax_amp)
ax_amp.plot(freq, amp_base, color=TEAL, lw=2.25)
ax_amp.plot(freq, amp_def, color=AMBER, lw=2.15)
ax_amp.fill_between(freq, amp_base, amp_def, color=AMBER, alpha=0.10, linewidth=0)
amp_scan = ax_amp.axvline(freq[0], color=NAVY, lw=0.9, alpha=0.23)
amp_dot_base, = ax_amp.plot([], [], "o", ms=4.0, color=TEAL)
amp_dot_def, = ax_amp.plot([], [], "o", ms=4.0, color=AMBER)
ax_amp.set_xlim(0, 40)
ax_amp.set_ylim(0.02, 1.08)
ax_amp.set_xlabel("Frequency", labelpad=2)
ax_amp.set_ylabel("Amplitude", labelpad=2)
ax_amp.text(0.72, 0.80, "baseline", transform=ax_amp.transAxes, fontsize=8.2, color=TEAL_DARK)
ax_amp.text(0.72, 0.67, "perturbed", transform=ax_amp.transAxes, fontsize=8.2, color=AMBER_DARK)


# ---------------------------------------------------------------------------
# Panel C: relative phase
# ---------------------------------------------------------------------------

fig.text(0.075, 0.553, "Relative phase", fontsize=13.8, fontweight="bold", color=INK, ha="left")
fig.text(0.075, 0.526, "Phase reveals a stronger change", fontsize=9.8, color=SLATE, ha="left")
fig.text(0.285, 0.553, r"$\phi=\arg(\beta)-\arg(\alpha)$", fontsize=10.0, color=SLATE, ha="left")

ax_phase = fig.add_axes([0.083, 0.392, 0.292, 0.105])
style_plot_axis(ax_phase)
ax_phase.plot(freq, phi_base, color=TEAL, lw=2.25)
ax_phase.plot(freq, phi_def, color=AMBER, lw=2.15)
ax_phase.fill_between(freq, phi_base, phi_def, color=AMBER, alpha=0.11, linewidth=0)
phase_scan = ax_phase.axvline(freq[0], color=NAVY, lw=0.9, alpha=0.23)
phase_dot_base, = ax_phase.plot([], [], "o", ms=4.0, color=TEAL)
phase_dot_def, = ax_phase.plot([], [], "o", ms=4.0, color=AMBER)
ax_phase.set_xlim(0, 40)
ax_phase.set_ylim(phi_base.min() - 0.35, phi_def.max() + 0.35)
ax_phase.set_xlabel("Frequency", labelpad=2)
ax_phase.set_ylabel("Relative phase", labelpad=2)


# ---------------------------------------------------------------------------
# Panel A: measured vibration system
# ---------------------------------------------------------------------------

fig.text(0.075, 0.277, "Measured vibration system", fontsize=13.8, fontweight="bold", color=INK, ha="left")
fig.text(0.075, 0.250, r"$u(\omega)=[U_1,U_2,U_3,U_4,U_5]^T$", fontsize=11.2, color=SLATE, ha="left")

ax_mech = fig.add_axes([0.075, 0.098, 0.535, 0.128])
ax_mech.set_xlim(0, 1)
ax_mech.set_ylim(0, 1)
ax_mech.axis("off")

mass_x0 = np.linspace(0.135, 0.865, 5)
mass_y = 0.50
body_w = 0.078
body_h = 0.300
cap_w = 0.035
spring_anchor = body_w / 2.0 + cap_w / 2.0

wall_left = Rectangle((0.030, 0.29), 0.018, 0.43, facecolor="#d8e2e8", edgecolor="#aab9c2", lw=0.8)
wall_right = Rectangle((0.952, 0.29), 0.018, 0.43, facecolor="#d8e2e8", edgecolor="#aab9c2", lw=0.8)
ax_mech.add_patch(wall_left)
ax_mech.add_patch(wall_right)
ax_mech.plot([0.065, 0.935], [0.15, 0.15], color="#c0ccd4", lw=1.1)

spring_lines = [ax_mech.plot([], [], color="#758895", lw=1.55, solid_capstyle="round", zorder=2)[0] for _ in range(6)]
mass_parts: list[tuple[Rectangle, Ellipse, Ellipse, Rectangle, Ellipse, str]] = []
mass_colors = [TEAL, TEAL, "#b9c4cc", AMBER, AMBER]

for i, x in enumerate(mass_x0):
    color = mass_colors[i]
    body = Rectangle(
        (x - body_w / 2.0, mass_y - body_h / 2.0),
        body_w,
        body_h,
        facecolor=color,
        edgecolor="white",
        linewidth=0.9,
        zorder=4,
    )
    left_cap = Ellipse((x - body_w / 2.0, mass_y), cap_w, body_h, facecolor=color, edgecolor="white", lw=0.9, zorder=5)
    right_cap = Ellipse((x + body_w / 2.0, mass_y), cap_w, body_h, facecolor=color, edgecolor="white", lw=0.9, zorder=5)
    shade = Rectangle((x - body_w / 2.0, mass_y - body_h / 2.0), body_w, body_h * 0.33, facecolor=(0, 0, 0, 0.10), edgecolor="none", zorder=6)
    shine = Ellipse((x - body_w * 0.18, mass_y + body_h * 0.23), body_w * 0.48, body_h * 0.15, facecolor="white", edgecolor="none", alpha=0.42, zorder=7)
    for patch in (body, left_cap, right_cap, shade, shine):
        ax_mech.add_patch(patch)
    ax_mech.text(x, 0.91, f"m{i + 1}", ha="center", va="center", fontsize=8.8, color=SLATE)
    ax_mech.text(x, 0.03, f"$u_{i + 1}$", ha="center", va="center", fontsize=8.6, color=MUTED)
    mass_parts.append((body, left_cap, right_cap, shade, shine, color))

defect_halo = Ellipse((mass_x0[2], mass_y), 0.170, 0.365, facecolor=CORAL, edgecolor="none", alpha=0.09, zorder=1)
ax_mech.add_patch(defect_halo)


def spring_path(x0: float, y0: float, x1: float, y1: float, turns: int = 6) -> tuple[np.ndarray, np.ndarray]:
    n = 120
    xs = np.linspace(x0, x1, n)
    center = np.linspace(y0, y1, n)
    return xs, center + 0.032 * np.sin(np.linspace(0.0, 2.0 * np.pi * turns, n))


def update_cylinder(parts: tuple[Rectangle, Ellipse, Ellipse, Rectangle, Ellipse, str], x: float, y: float) -> None:
    body, left_cap, right_cap, shade, shine, _ = parts
    body.set_xy((x - body_w / 2.0, y - body_h / 2.0))
    left_cap.center = (x - body_w / 2.0, y)
    right_cap.center = (x + body_w / 2.0, y)
    shade.set_xy((x - body_w / 2.0, y - body_h / 2.0))
    shine.center = (x - body_w * 0.18, y + body_h * 0.23)


# ---------------------------------------------------------------------------
# Panel D: modal projection
# ---------------------------------------------------------------------------

fig.text(0.448, 0.842, "Modal projection", fontsize=13.8, fontweight="bold", color=INK, ha="left")
fig.text(0.448, 0.815, "Measured response projected onto two modal coordinates", fontsize=9.4, color=SLATE, ha="left")

ax_proj = fig.add_axes([0.445, 0.395, 0.220, 0.375])
ax_proj.set_xlim(0, 1)
ax_proj.set_ylim(0, 1)
ax_proj.axis("off")

ax_proj.text(0.02, 0.92, r"$u(\omega)=[U_1,\ldots,U_5]^T$", fontsize=11.2, color=INK, ha="left")

vector_x = 0.10
vector_y = np.linspace(0.70, 0.42, 5)
ax_proj.plot([vector_x, vector_x], [vector_y.min() - 0.045, vector_y.max() + 0.045], color="#aebbc3", lw=1.0)
for i, yy_i in enumerate(vector_y):
    ax_proj.add_patch(Circle((vector_x, yy_i), 0.015, facecolor="#ffffff", edgecolor=NAVY, lw=0.8))
    ax_proj.text(vector_x - 0.040, yy_i, f"$U_{i + 1}$", ha="right", va="center", fontsize=8.2, color=SLATE)

ax_proj.add_patch(FancyArrowPatch((0.17, 0.56), (0.28, 0.56), arrowstyle="-|>", mutation_scale=13, lw=1.0, color="#9daeb8"))
ax_proj.text(0.23, 0.60, "project", fontsize=8.0, color=MUTED, ha="center")

mode_x = np.linspace(0.32, 0.55, 5)
mode_scale = 0.070
mode1_y = 0.68 + mode_scale * E1 / np.max(np.abs(E1))
mode2_y = 0.45 + mode_scale * E2 / np.max(np.abs(E2))
ax_proj.text(0.29, 0.71, r"$|E_1\rangle$", fontsize=11.3, color=TEAL_DARK, ha="right", va="center")
ax_proj.text(0.29, 0.45, r"$|E_2\rangle$", fontsize=11.3, color=AMBER_DARK, ha="right", va="center")
ax_proj.plot(mode_x, mode1_y, color=TEAL, lw=1.5)
ax_proj.plot(mode_x, mode2_y, color=AMBER, lw=1.5)
ax_proj.scatter(mode_x, mode1_y, s=18, color=TEAL, edgecolors="white", linewidths=0.5, zorder=4)
ax_proj.scatter(mode_x, mode2_y, s=18, color=AMBER, edgecolors="white", linewidths=0.5, zorder=4)

for y0 in (0.68, 0.45):
    ax_proj.add_patch(FancyArrowPatch((0.58, y0), (0.66, y0), arrowstyle="-|>", mutation_scale=13, lw=1.0, color="#9daeb8"))

ax_proj.text(0.68, 0.70, r"$\alpha(\omega)=\langle E_1|u(\omega)\rangle$", fontsize=10.1, color=TEAL_DARK, ha="left", va="center")
ax_proj.text(0.68, 0.47, r"$\beta(\omega)=\langle E_2|u(\omega)\rangle$", fontsize=10.1, color=AMBER_DARK, ha="left", va="center")
alpha_bar = Rectangle((0.68, 0.625), 0.001, 0.025, facecolor=TEAL, edgecolor="none", alpha=0.42)
beta_bar = Rectangle((0.68, 0.395), 0.001, 0.025, facecolor=AMBER, edgecolor="none", alpha=0.42)
ax_proj.add_patch(alpha_bar)
ax_proj.add_patch(beta_bar)

ax_proj.plot([0.05, 0.94], [0.285, 0.285], color="#d6e0e6", lw=0.9)
ax_proj.text(
    0.02,
    0.185,
    r"$|\psi(\omega)\rangle=\alpha(\omega)|E_1\rangle+\beta(\omega)|E_2\rangle$",
    fontsize=10.5,
    color=INK,
    ha="left",
)


# ---------------------------------------------------------------------------
# Panel E: reduced-state sphere and geometric phase
# ---------------------------------------------------------------------------

fig.text(0.730, 0.842, "Reduced-state trajectory", fontsize=13.8, fontweight="bold", color=INK, ha="left")
fig.text(0.730, 0.814, "classical reduced-state representation", fontsize=9.3, color=SLATE, ha="left")
fig.text(0.730, 0.788, r"$\theta=2\tan^{-1}(|\beta|/|\alpha|)$    $\phi=\arg(\beta)-\arg(\alpha)$", fontsize=9.5, color=SLATE)

ax_sphere = fig.add_axes([0.727, 0.405, 0.210, 0.330])
ax_sphere.set_xlim(-1.25, 1.25)
ax_sphere.set_ylim(-1.22, 1.22)
ax_sphere.set_aspect("equal", adjustable="box")
ax_sphere.axis("off")

angle = np.linspace(0.0, 2.0 * np.pi, 260)
sphere_shadow = Ellipse((0.0, -1.06), 1.25, 0.13, facecolor="#bfccd5", edgecolor="none", alpha=0.34)
sphere_shell = Circle((0.0, 0.0), 1.0, facecolor=(0.83, 0.90, 0.93, 0.42), edgecolor="#aec0ca", lw=1.0)
ax_sphere.add_patch(sphere_shadow)
ax_sphere.add_patch(sphere_shell)

for ph in np.linspace(0.0, np.pi, 6, endpoint=False):
    pts = np.column_stack([np.sin(angle) * np.cos(ph), np.sin(angle) * np.sin(ph), np.cos(angle)])
    pp = project_sphere(pts)
    ax_sphere.plot(pp[:, 0], pp[:, 1], color="#aebcc6", lw=0.65, alpha=0.55)
for z in (-0.45, 0.0, 0.45):
    r = np.sqrt(1.0 - z * z)
    pts = np.column_stack([r * np.cos(angle), r * np.sin(angle), np.full_like(angle, z)])
    pp = project_sphere(pts)
    ax_sphere.plot(pp[:, 0], pp[:, 1], color="#b9c6ce", lw=0.65, alpha=0.48)

loop_fill = Polygon(traj_def, closed=True, facecolor=AMBER, edgecolor="none", alpha=0.105)
ax_sphere.add_patch(loop_fill)
ax_sphere.plot(traj_base[:, 0], traj_base[:, 1], color=TEAL, lw=2.05)
ax_sphere.plot(traj_def[:, 0], traj_def[:, 1], color=AMBER, lw=2.05)
trail_line, = ax_sphere.plot([], [], color=NAVY, lw=1.0, alpha=0.43)
state_base_dot = Circle((0, 0), 0.030, facecolor=TEAL, edgecolor="white", lw=0.8, zorder=8)
state_def_glow = Circle((0, 0), 0.090, facecolor=AMBER, edgecolor="none", alpha=0.15, zorder=7)
state_def_dot = Circle((0, 0), 0.039, facecolor="white", edgecolor=AMBER, lw=1.25, zorder=9)
ax_sphere.add_patch(state_base_dot)
ax_sphere.add_patch(state_def_glow)
ax_sphere.add_patch(state_def_dot)
ax_sphere.text(0.0, 1.13, r"$|E_1\rangle$", ha="center", va="center", fontsize=10.6, color=TEAL_DARK)
ax_sphere.text(0.0, -1.15, r"$|E_2\rangle$", ha="center", va="center", fontsize=10.6, color=AMBER_DARK)
fig.text(0.730, 0.385, "baseline", color=TEAL_DARK, fontsize=9.2, ha="left")
fig.text(0.805, 0.385, "perturbed", color=AMBER_DARK, fontsize=9.2, ha="left")

fig.text(0.730, 0.306, "Geometric phase", fontsize=13.0, fontweight="bold", color=INK, ha="left")
fig.text(
    0.730,
    0.268,
    "Geometric phase: phase accumulated because the\n"
    "normalized reduced state traces a closed path in state space.",
    fontsize=8.3,
    color=SLATE,
    ha="left",
    linespacing=1.22,
)
fig.text(0.730, 0.205, r"$\gamma_g=\oint i\langle\psi|d\psi\rangle$", fontsize=12.4, color=NAVY, ha="left")
fig.text(0.730, 0.170, "Depends on the loop geometry, not only on amplitude.", fontsize=8.3, color=SLATE, ha="left")

ax_gamma = fig.add_axes([0.875, 0.185, 0.060, 0.120])
ax_gamma.set_xlim(-1, 1)
ax_gamma.set_ylim(-1, 1)
ax_gamma.set_aspect("equal")
ax_gamma.axis("off")
loop_t = np.linspace(0.0, 2.0 * np.pi, 180)
loop_x = 0.60 * np.cos(loop_t) + 0.08 * np.cos(2 * loop_t)
loop_y = 0.43 * np.sin(loop_t)
ax_gamma.add_patch(Polygon(np.column_stack([loop_x, loop_y]), closed=True, facecolor=AMBER, edgecolor="none", alpha=0.16))
ax_gamma.plot(loop_x, loop_y, color="#c49a70", lw=1.2)
gamma_arc = Wedge((0, 0), 0.77, 25, 30, width=0.12, facecolor=AMBER, edgecolor="none", alpha=0.60)
ax_gamma.add_patch(gamma_arc)


# Minimal connectors: mechanical response -> modal projection -> reduced state.
for start, end in [((0.635, 0.190), (0.425, 0.475)), ((0.685, 0.620), (0.710, 0.600))]:
    fig.patches.append(
        FancyArrowPatch(
            start,
            end,
            transform=fig.transFigure,
            arrowstyle="-|>",
            mutation_scale=14,
            lw=1.05,
            color="#aebbc3",
            alpha=0.72,
            zorder=-1,
        )
    )


# ---------------------------------------------------------------------------
# Animation update
# ---------------------------------------------------------------------------


def update(frame: int) -> list:
    q = frame / N_FRAMES
    idx = min(int(q * (len(freq) - 1)), len(freq) - 1)
    f_now = float(freq[idx])
    t = frame / FPS

    amp_scan.set_xdata([f_now, f_now])
    phase_scan.set_xdata([f_now, f_now])
    amp_dot_base.set_data([f_now], [amp_base[idx]])
    amp_dot_def.set_data([f_now], [amp_def[idx]])
    phase_dot_base.set_data([f_now], [phi_base[idx]])
    phase_dot_def.set_data([f_now], [phi_def[idx]])

    # Gentle horizontal vibration of the five cylindrical masses.
    carrier = np.exp(1j * 2.0 * np.pi * 1.20 * t)
    dx = response_scale * np.real(u_base[:, idx] * carrier)
    y_positions = mass_y + 0.006 * np.sin(2.0 * np.pi * 1.20 * t + np.arange(5) * 0.30)
    x_positions = mass_x0 + dx
    for i, x in enumerate(x_positions):
        update_cylinder(mass_parts[i], float(x), float(y_positions[i]))

    endpoints = [(0.048, mass_y), *[(float(x), float(y)) for x, y in zip(x_positions, y_positions)], (0.952, mass_y)]
    for i, spring in enumerate(spring_lines):
        x0, y0 = endpoints[i]
        x1, y1 = endpoints[i + 1]
        offset0 = spring_anchor if i > 0 else 0.0
        offset1 = spring_anchor if i < 5 else 0.0
        xs, ys = spring_path(x0 + offset0, y0, x1 - offset1, y1, turns=5 if i in (0, 5) else 6)
        spring.set_data(xs, ys)
    defect_halo.center = (float(x_positions[2]), float(y_positions[2]))
    defect_halo.set_alpha(0.075 + 0.040 * np.sin(2.0 * np.pi * q) ** 2)

    # Modal coefficient bars.
    alpha_bar.set_width(0.24 * float(np.abs(alpha_def_n[idx])))
    beta_bar.set_width(0.24 * float(np.abs(beta_def_n[idx])))

    # Closed-loop state trajectory point.
    point_base = traj_base[idx]
    point_def = traj_def[idx]
    state_base_dot.center = (float(point_base[0]), float(point_base[1]))
    state_def_glow.center = (float(point_def[0]), float(point_def[1]))
    state_def_dot.center = (float(point_def[0]), float(point_def[1]))
    trail_line.set_data(traj_def[: idx + 1, 0], traj_def[: idx + 1, 1])
    loop_fill.set_alpha(0.085 + 0.045 * np.sin(np.pi * q) ** 2)

    gamma_arc.theta2 = 25 + 330 * q
    return []


def save_preview() -> None:
    """Save a representative still frame."""
    update(int(0.64 * N_FRAMES))
    fig.savefig(PNG_PATH, dpi=DPI)


# ---------------------------------------------------------------------------
# Export helpers
# ---------------------------------------------------------------------------


def resolve_ffmpeg() -> str | None:
    """Find system ffmpeg or imageio-ffmpeg fallback."""
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is not None:
        return ffmpeg_path
    try:
        import imageio_ffmpeg

        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        plt.rcParams["animation.ffmpeg_path"] = ffmpeg_path
        print(f"Using ffmpeg from imageio-ffmpeg: {ffmpeg_path}")
        return ffmpeg_path
    except ImportError:
        return None


def save_gif_from_mp4(ffmpeg_path: str) -> None:
    """Create a compact full-resolution GIF from the rendered MP4."""
    palette_filter = "fps=30,scale=1920:1080:flags=lanczos,palettegen=max_colors=168:stats_mode=diff"
    gif_filter = "fps=30,scale=1920:1080:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5"
    try:
        subprocess.run(
            [ffmpeg_path, "-y", "-i", str(MP4_PATH), "-vf", palette_filter, str(PALETTE_PATH)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            [
                ffmpeg_path,
                "-y",
                "-i",
                str(MP4_PATH),
                "-i",
                str(PALETTE_PATH),
                "-filter_complex",
                gif_filter,
                "-loop",
                "0",
                str(GIF_PATH),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    finally:
        PALETTE_PATH.unlink(missing_ok=True)


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    save_preview()

    anim = animation.FuncAnimation(
        fig,
        update,
        frames=N_FRAMES,
        interval=1000 / FPS,
        blit=False,
        repeat=True,
    )

    ffmpeg_path = resolve_ffmpeg()
    if ffmpeg_path is None:
        raise SystemExit(
            "ffmpeg was not found, so MP4 export cannot run.\n"
            "Install ffmpeg and re-run this script. On Windows:\n"
            "    winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements\n"
            "Or install the Python helper package:\n"
            "    python -m pip install imageio-ffmpeg\n"
        )

    print(f"Saving MP4 to {MP4_PATH} ...")
    writer = animation.FFMpegWriter(
        fps=FPS,
        codec="libx264",
        bitrate=9500,
        extra_args=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
    )
    anim.save(MP4_PATH, writer=writer, dpi=DPI)

    print(f"Saving GIF to {GIF_PATH} ...")
    save_gif_from_mp4(ffmpeg_path)

    print("Created:")
    print(f"  {MP4_PATH}")
    print(f"  {GIF_PATH}")
    print(f"  {PNG_PATH}")


if __name__ == "__main__":
    main()
