"""
Generate an editorial scientific motion-graphics animation explaining reduced
geometric-state interpretation of classical mechanical response.

How to run:
    python generate_geometric_mechanics_animation.py

Outputs:
    outputs/geometric_mechanics_animation.mp4
    outputs/geometric_mechanics_animation.gif
    outputs/geometric_mechanics_preview.png

Notes:
    MP4 export requires ffmpeg on PATH. On Windows, install it with:
        winget install --id Gyan.FFmpeg -e
    If system ffmpeg is unavailable, this script can also use imageio-ffmpeg:
        python -m pip install imageio-ffmpeg
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
from pathlib import Path


def require_package(import_name: str, install_name: str | None = None) -> None:
    """Give a clear dependency message before importing plotting packages."""
    if importlib.util.find_spec(import_name) is None:
        package = install_name or import_name
        raise SystemExit(
            f"Missing Python package '{package}'. Install dependencies with:\n"
            f"    python -m pip install numpy matplotlib pillow imageio-ffmpeg\n"
        )


require_package("numpy")
require_package("matplotlib")
require_package("PIL", "pillow")

import numpy as np

import matplotlib

matplotlib.use("Agg")

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, Polygon


# ---------------------------------------------------------------------------
# Export settings
# ---------------------------------------------------------------------------

OUT_DIR = Path("outputs")
MP4_PATH = OUT_DIR / "geometric_mechanics_animation.mp4"
GIF_PATH = OUT_DIR / "geometric_mechanics_animation.gif"
PNG_PATH = OUT_DIR / "geometric_mechanics_preview.png"
PALETTE_PATH = OUT_DIR / "geometric_mechanics_palette.png"

FPS = 30
DURATION = 10.0
N_FRAMES = int(FPS * DURATION)
FIGSIZE = (19.2, 10.8)
DPI = 100


# ---------------------------------------------------------------------------
# Editorial visual language
# ---------------------------------------------------------------------------

BG_DARK = "#10161c"
INK = "#f0eee8"
MUTED = "#a7adb4"
FAINT = "#6e7782"
TEAL = "#66d2c4"
TEAL_DEEP = "#2b9a96"
ROSE = "#dba083"
ROSE_DEEP = "#a96961"
LAVENDER = "#b8b6d9"
SILVER = "#d9dde0"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 12,
        "figure.facecolor": BG_DARK,
        "savefig.facecolor": BG_DARK,
        "axes.facecolor": (0, 0, 0, 0),
        "text.color": INK,
        "axes.labelcolor": MUTED,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
    }
)


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    """Smooth cubic step from 0 to 1."""
    if edge0 == edge1:
        return 1.0 if x >= edge1 else 0.0
    u = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return float(u * u * (3.0 - 2.0 * u))


def fade_window(t: float, start: float, fade_in: float, fade_out: float, end: float) -> float:
    """Fade in, hold, then fade out."""
    return smoothstep(start, fade_in, t) * (1.0 - smoothstep(fade_out, end, t))


def set_alpha(artists: list, alpha: float) -> None:
    """Apply alpha to a mixed list of matplotlib artists."""
    for artist in artists:
        if artist is not None:
            artist.set_alpha(alpha)


def style_minimal_axis(ax: plt.Axes) -> None:
    """Use sparse editorial chart styling, not a dashboard frame."""
    ax.grid(True, color="#d8dde2", alpha=0.075, linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#c7ccd0")
        ax.spines[side].set_alpha(0.30)
        ax.spines[side].set_linewidth(0.9)
    ax.tick_params(length=3, width=0.8, colors=MUTED)


# ---------------------------------------------------------------------------
# Synthetic but meaningful response data
# ---------------------------------------------------------------------------

freq = np.linspace(0.0, 40.0, 720)


def lorentzian(f: np.ndarray, center: float, width: float, amp: float) -> np.ndarray:
    return amp / (1.0 + ((f - center) / width) ** 2)


amp_baseline = (
    0.10
    + lorentzian(freq, 11.8, 1.45, 0.82)
    + lorentzian(freq, 26.3, 2.10, 0.54)
    + 0.030 * np.exp(-((freq - 33.0) / 4.2) ** 2)
)
amp_perturbed = (
    0.10
    + lorentzian(freq, 12.15, 1.50, 0.80)
    + lorentzian(freq, 25.95, 2.16, 0.56)
    + 0.026 * np.exp(-((freq - 32.7) / 4.3) ** 2)
)
amp_baseline /= amp_baseline.max()
amp_perturbed /= amp_perturbed.max()

phase_baseline = (
    -0.18 * np.pi
    - 0.86 * np.arctan((freq - 11.8) / 1.45)
    - 0.58 * np.arctan((freq - 26.3) / 2.10)
)
phase_perturbed = (
    -0.18 * np.pi
    - 0.98 * np.arctan((freq - 12.25) / 1.25)
    - 0.46 * np.arctan((freq - 24.6) / 1.45)
    + 0.64 * np.exp(-((freq - 21.8) / 5.7) ** 2)
)
phase_baseline = np.unwrap(phase_baseline)
phase_perturbed = np.unwrap(phase_perturbed)


def modal_coefficients(f: np.ndarray, defect: bool) -> tuple[np.ndarray, np.ndarray]:
    """Create complex modal coefficients alpha(f), beta(f)."""
    tau = f / 40.0
    a1 = 0.82 + 0.12 * np.cos(2.0 * np.pi * tau) + 0.07 * np.exp(-((f - 10.5) / 6.0) ** 2)
    a2 = 0.46 + 0.35 * smooth_array(tau, 0.36, 0.74) + 0.08 * np.sin(2.0 * np.pi * 1.5 * tau + 0.4)
    p1 = 0.25 * np.sin(2.0 * np.pi * tau + 0.35)
    p2 = 1.05 * np.pi * tau + 0.40 * np.sin(2.0 * np.pi * 1.4 * tau + 1.1)

    if defect:
        a1 = a1 * (1.0 - 0.08 * np.exp(-((f - 23.0) / 5.0) ** 2))
        a2 = a2 + 0.18 * np.exp(-((f - 23.0) / 4.6) ** 2)
        p2 = p2 + 0.95 * smooth_array(f, 17.5, 26.0) - 0.26 * np.exp(-((f - 32.0) / 4.6) ** 2)
        p1 = p1 - 0.20 * np.exp(-((f - 18.0) / 7.0) ** 2)

    alpha = a1 * np.exp(1j * p1)
    beta = a2 * np.exp(1j * p2)
    norm = np.sqrt(np.abs(alpha) ** 2 + np.abs(beta) ** 2)
    return alpha / norm, beta / norm


def smooth_array(x: np.ndarray, edge0: float, edge1: float) -> np.ndarray:
    u = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


alpha_base, beta_base = modal_coefficients(freq, defect=False)
alpha_defect, beta_defect = modal_coefficients(freq, defect=True)


def reduced_angles(alpha: np.ndarray, beta: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    theta = 2.0 * np.arctan2(np.abs(beta), np.abs(alpha))
    phi = np.unwrap(np.angle(beta) - np.angle(alpha))
    return theta, phi


theta_base, phi_base = reduced_angles(alpha_base, beta_base)
theta_defect, phi_defect = reduced_angles(alpha_defect, beta_defect)


def sphere_xyz(theta: np.ndarray, phi: np.ndarray) -> np.ndarray:
    return np.column_stack(
        [
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta),
        ]
    )


traj_base_3d = sphere_xyz(theta_base, phi_base)
traj_defect_3d = sphere_xyz(theta_defect, phi_defect)


def project(points: np.ndarray) -> np.ndarray:
    """Project 3D sphere coordinates into a quiet 2D cinematic view."""
    az = np.deg2rad(-36.0)
    x, y, z = points[:, 0], points[:, 1], points[:, 2]
    xr = x * np.cos(az) - y * np.sin(az)
    yr = x * np.sin(az) + y * np.cos(az)
    return np.column_stack([0.98 * xr, 0.68 * z + 0.24 * yr])


traj_base = project(traj_base_3d)
traj_defect = project(traj_defect_3d)


# ---------------------------------------------------------------------------
# Figure construction
# ---------------------------------------------------------------------------

fig = plt.figure(figsize=FIGSIZE, dpi=DPI, facecolor=BG_DARK)

ax_bg = fig.add_axes([0, 0, 1, 1], zorder=-50)
ax_bg.set_axis_off()
yy, xx = np.mgrid[0:1:540j, 0:1:960j]
rng = np.random.default_rng(11)
texture = rng.normal(0.0, 0.010, size=(540, 960))
base = np.zeros((540, 960, 3), dtype=float)
base[..., 0] = 0.060 + 0.030 * (1.0 - yy)
base[..., 1] = 0.080 + 0.038 * (1.0 - yy)
base[..., 2] = 0.100 + 0.050 * (1.0 - yy)

def add_bg_glow(cx: float, cy: float, sx: float, sy: float, color: tuple[float, float, float], strength: float) -> None:
    field = np.exp(-(((xx - cx) / sx) ** 2 + ((yy - cy) / sy) ** 2))
    for channel, value in enumerate(color):
        base[..., channel] += strength * value * field


add_bg_glow(0.22, 0.70, 0.44, 0.42, (0.10, 0.32, 0.30), 0.16)
add_bg_glow(0.76, 0.33, 0.40, 0.36, (0.34, 0.22, 0.30), 0.12)
add_bg_glow(0.52, 0.12, 0.55, 0.25, (0.22, 0.24, 0.32), 0.11)
base += texture[..., None]
ax_bg.imshow(np.clip(base, 0.0, 1.0), origin="lower", aspect="auto", extent=[0, 1, 0, 1])

fig.text(0.070, 0.915, "Reduced Geometric Mechanics", fontsize=25, fontweight="normal", color=INK, ha="left")
fig.text(0.072, 0.875, "phase, modal projection, and state geometry in classical vibration response", fontsize=12, color=MUTED, ha="left")


# Amplitude response view
ax_amp = fig.add_axes([0.150, 0.245, 0.700, 0.465])
style_minimal_axis(ax_amp)
amp_base_line, = ax_amp.plot([], [], color=TEAL, lw=2.7, solid_capstyle="round")
amp_defect_line, = ax_amp.plot([], [], color=ROSE, lw=2.5, solid_capstyle="round")
amp_base_shadow, = ax_amp.plot([], [], color=TEAL_DEEP, lw=8.5, alpha=0.06, solid_capstyle="round")
amp_defect_shadow, = ax_amp.plot([], [], color=ROSE_DEEP, lw=8.5, alpha=0.05, solid_capstyle="round")
ax_amp.set_xlim(0, 40)
ax_amp.set_ylim(0.02, 1.12)
ax_amp.set_xlabel("Frequency")
ax_amp.set_ylabel("Amplitude")
amp_label_base = ax_amp.text(11.7, 1.03, "baseline", color=TEAL, fontsize=11, ha="center")
amp_label_defect = ax_amp.text(25.9, 0.75, "perturbed", color=ROSE, fontsize=11, ha="center")
amp_caption = fig.text(0.150, 0.760, "Amplitude alone may show only a small change", fontsize=21, color=INK, ha="left")


# Phase response view
ax_phase = fig.add_axes([0.150, 0.245, 0.700, 0.465])
style_minimal_axis(ax_phase)
phase_region = ax_phase.axvspan(18.0, 25.5, color=ROSE, alpha=0.0, linewidth=0)
phase_base_line, = ax_phase.plot([], [], color=TEAL, lw=2.6, solid_capstyle="round")
phase_defect_line, = ax_phase.plot([], [], color=ROSE, lw=2.6, solid_capstyle="round")
phase_base_shadow, = ax_phase.plot([], [], color=TEAL_DEEP, lw=8.0, alpha=0.05, solid_capstyle="round")
phase_defect_shadow, = ax_phase.plot([], [], color=ROSE_DEEP, lw=8.0, alpha=0.05, solid_capstyle="round")
ax_phase.set_xlim(0, 40)
phase_min = min(phase_baseline.min(), phase_perturbed.min()) - 0.20
phase_max = max(phase_baseline.max(), phase_perturbed.max()) + 0.20
ax_phase.set_ylim(phase_min, phase_max)
ax_phase.set_xlabel("Frequency")
ax_phase.set_ylabel("Relative phase")
phase_caption = fig.text(0.150, 0.760, "Phase evolution reveals a stronger signature", fontsize=21, color=INK, ha="left")
phase_micro = fig.text(0.650, 0.725, "phi = arg(beta) - arg(alpha)", fontsize=12, color=MUTED, ha="left")


# Modal projection view
ax_modal = fig.add_axes([0.075, 0.170, 0.850, 0.620])
ax_modal.set_xlim(0, 1)
ax_modal.set_ylim(0, 1)
ax_modal.axis("off")
modal_caption = fig.text(0.110, 0.780, "Modal amplitudes and relative phase define a reduced state", fontsize=20, color=INK, ha="left")

chain_x = np.linspace(0.08, 0.42, 9)
chain_y = 0.48 + 0.035 * np.sin(np.linspace(0, 2.2 * np.pi, 9))
chain_line, = ax_modal.plot(chain_x, chain_y, color=SILVER, lw=1.2, alpha=0.0)
chain_nodes = [
    Circle((x, y), 0.014 + 0.006 * np.exp(-((i - 5.8) / 1.2) ** 2), facecolor=SILVER, edgecolor="none", alpha=0.0)
    for i, (x, y) in enumerate(zip(chain_x, chain_y))
]
for node in chain_nodes:
    ax_modal.add_patch(node)
defect_glow = Circle((chain_x[6], chain_y[6]), 0.044, facecolor=ROSE, edgecolor="none", alpha=0.0)
ax_modal.add_patch(defect_glow)

mode_x = np.linspace(0.10, 0.40, 160)
mode_s = 0.60 + 0.050 * np.sin(np.linspace(0, 2.0 * np.pi, 160))
mode_a = 0.33 + 0.050 * np.sin(np.linspace(0, 2.0 * np.pi, 160) + np.pi)
mode_s_line, = ax_modal.plot(mode_x, mode_s, color=TEAL, lw=1.8, alpha=0.0)
mode_a_line, = ax_modal.plot(mode_x, mode_a, color=ROSE, lw=1.8, alpha=0.0)
modal_arrow, = ax_modal.plot([0.49, 0.58], [0.48, 0.48], color=MUTED, lw=1.3, alpha=0.0)
modal_arrow_head = Polygon([[0.58, 0.48], [0.555, 0.495], [0.555, 0.465]], closed=True, facecolor=MUTED, edgecolor="none", alpha=0.0)
ax_modal.add_patch(modal_arrow_head)
modal_eq = ax_modal.text(0.62, 0.52, r"$u(\omega)\ \rightarrow\ \alpha |S\rangle + \beta |A\rangle$", fontsize=22, color=INK, ha="left", va="center", alpha=0.0)
modal_inner_1 = ax_modal.text(0.62, 0.42, r"$\alpha = \langle S|u\rangle$", fontsize=13, color=TEAL, ha="left", va="center", alpha=0.0)
modal_inner_2 = ax_modal.text(0.62, 0.36, r"$\beta = \langle A|u\rangle$", fontsize=13, color=ROSE, ha="left", va="center", alpha=0.0)
modal_label_1 = ax_modal.text(0.10, 0.68, "symmetric basis", fontsize=10.5, color=TEAL, ha="left", alpha=0.0)
modal_label_2 = ax_modal.text(0.10, 0.24, "antisymmetric basis", fontsize=10.5, color=ROSE, ha="left", alpha=0.0)


# Reduced geometric state view
ax_sphere = fig.add_axes([0.355, 0.155, 0.375, 0.665])
ax_sphere.set_xlim(-1.25, 1.25)
ax_sphere.set_ylim(-1.25, 1.25)
ax_sphere.set_aspect("equal", adjustable="box")
ax_sphere.axis("off")

sphere_shadow = Ellipse((0.0, -1.04), 1.28, 0.13, facecolor="#060809", edgecolor="none", alpha=0.0)
sphere_shell = Circle((0.0, 0.0), 1.0, facecolor=(0.78, 0.82, 0.86, 0.035), edgecolor=SILVER, lw=0.9, alpha=0.0)
ax_sphere.add_patch(sphere_shadow)
ax_sphere.add_patch(sphere_shell)

meridian_lines: list = []
u = np.linspace(0, 2.0 * np.pi, 240)
for phi0 in np.linspace(0, np.pi, 5, endpoint=False):
    circle_3d = np.column_stack([np.sin(u) * np.cos(phi0), np.sin(u) * np.sin(phi0), np.cos(u)])
    projected = project(circle_3d)
    line, = ax_sphere.plot(projected[:, 0], projected[:, 1], color=SILVER, lw=0.65, alpha=0.0)
    meridian_lines.append(line)
equator_3d = np.column_stack([np.cos(u), np.sin(u), np.zeros_like(u)])
equator = project(equator_3d)
equator_line, = ax_sphere.plot(equator[:, 0], equator[:, 1], color=LAVENDER, lw=0.9, alpha=0.0)

trajectory_fill = Polygon(np.zeros((3, 2)), closed=True, facecolor=ROSE, edgecolor="none", alpha=0.0)
ax_sphere.add_patch(trajectory_fill)
traj_base_line, = ax_sphere.plot([], [], color=TEAL, lw=2.0, alpha=0.0, solid_capstyle="round")
traj_defect_line, = ax_sphere.plot([], [], color=ROSE, lw=2.0, alpha=0.0, solid_capstyle="round")
traj_base_soft, = ax_sphere.plot([], [], color=TEAL, lw=8.0, alpha=0.0, solid_capstyle="round")
traj_defect_soft, = ax_sphere.plot([], [], color=ROSE, lw=8.0, alpha=0.0, solid_capstyle="round")
state_dot_glow = Circle((0.0, 0.0), 0.090, facecolor=ROSE, edgecolor="none", alpha=0.0)
state_dot = Circle((0.0, 0.0), 0.035, facecolor=INK, edgecolor=ROSE, lw=1.0, alpha=0.0)
ax_sphere.add_patch(state_dot_glow)
ax_sphere.add_patch(state_dot)

sphere_caption = fig.text(0.115, 0.780, "The response becomes a trajectory in reduced geometric space", fontsize=20, color=INK, ha="left")
sphere_eq_1 = fig.text(0.075, 0.275, r"$|\psi\rangle = \alpha |S\rangle + \beta |A\rangle$", fontsize=18, color=INK, ha="left")
sphere_eq_2 = fig.text(0.075, 0.225, r"$\theta = 2\tan^{-1}(|\beta|/|\alpha|)$", fontsize=13, color=MUTED, ha="left")
sphere_eq_3 = fig.text(0.075, 0.185, r"$\phi = \arg(\beta) - \arg(\alpha)$", fontsize=13, color=MUTED, ha="left")
traj_label_b = fig.text(0.745, 0.355, "baseline path", fontsize=11, color=TEAL, ha="left")
traj_label_d = fig.text(0.745, 0.315, "perturbed path", fontsize=11, color=ROSE, ha="left")

topology_caption = fig.text(0.106, 0.780, "Trajectory shape and accumulated phase reveal hidden dynamic behavior", fontsize=20, color=INK, ha="left")
gamma_text = fig.text(0.760, 0.245, r"$\gamma_g = \oint i\langle\psi|d\psi\rangle$", fontsize=13, color=MUTED, ha="left")
localization_text = fig.text(0.760, 0.205, "defect sensitivity  |  localization  |  symmetry change", fontsize=10.5, color=FAINT, ha="left")

final_statement = fig.text(
    0.075,
    0.715,
    "Beyond resonance analysis:\nphase, geometry, and topology reveal\nthe evolving mechanical state",
    fontsize=27,
    color=INK,
    ha="left",
    va="top",
    linespacing=1.18,
)

final_sub = fig.text(
    0.078,
    0.485,
    "Classical modal response becomes\na trajectory through reduced state space.",
    fontsize=13,
    color=MUTED,
    ha="left",
    va="top",
    linespacing=1.35,
)


amp_artists = [
    ax_amp,
    amp_base_line,
    amp_defect_line,
    amp_base_shadow,
    amp_defect_shadow,
    amp_label_base,
    amp_label_defect,
    amp_caption,
]
phase_artists = [
    ax_phase,
    phase_region,
    phase_base_line,
    phase_defect_line,
    phase_base_shadow,
    phase_defect_shadow,
    phase_caption,
    phase_micro,
]
modal_artists = [
    ax_modal,
    modal_caption,
    chain_line,
    *chain_nodes,
    defect_glow,
    mode_s_line,
    mode_a_line,
    modal_arrow,
    modal_arrow_head,
    modal_eq,
    modal_inner_1,
    modal_inner_2,
    modal_label_1,
    modal_label_2,
]
sphere_artists = [
    ax_sphere,
    sphere_shadow,
    sphere_shell,
    *meridian_lines,
    equator_line,
    trajectory_fill,
    traj_base_line,
    traj_defect_line,
    traj_base_soft,
    traj_defect_soft,
    state_dot_glow,
    state_dot,
    sphere_caption,
    sphere_eq_1,
    sphere_eq_2,
    sphere_eq_3,
    traj_label_b,
    traj_label_d,
]
topology_artists = [topology_caption, gamma_text, localization_text]
final_artists = [final_statement, final_sub]


def set_axis_alpha(ax: plt.Axes, alpha: float) -> None:
    """Fade an axis, including labels, ticks, grid, and spines."""
    ax.xaxis.label.set_alpha(alpha)
    ax.yaxis.label.set_alpha(alpha)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_alpha(alpha)
    for tick in ax.xaxis.get_major_ticks() + ax.yaxis.get_major_ticks():
        tick.tick1line.set_alpha(alpha)
        tick.tick2line.set_alpha(alpha)
    for spine in ax.spines.values():
        spine.set_alpha(0.30 * alpha)
    for gridline in ax.get_xgridlines() + ax.get_ygridlines():
        gridline.set_alpha(0.075 * alpha)


def trace_data(x: np.ndarray, y: np.ndarray, progress: float) -> tuple[np.ndarray, np.ndarray]:
    """Return a prefix of a curve for trace-on animation."""
    n = max(2, int(np.clip(progress, 0.0, 1.0) * (len(x) - 1)))
    return x[:n], y[:n]


def update_amplitude_scene(t: float, alpha: float) -> None:
    set_axis_alpha(ax_amp, alpha)
    p_base = smoothstep(0.30, 1.15, t)
    p_defect = smoothstep(1.05, 1.95, t)
    xb, yb = trace_data(freq, amp_baseline, p_base)
    xd, yd = trace_data(freq, amp_perturbed, p_defect)
    for line in (amp_base_line, amp_base_shadow):
        line.set_data(xb, yb)
    for line in (amp_defect_line, amp_defect_shadow):
        line.set_data(xd, yd)
    amp_base_line.set_alpha(0.96 * alpha)
    amp_base_shadow.set_alpha(0.075 * alpha)
    amp_label_base.set_alpha(alpha)
    amp_defect_line.set_alpha(0.95 * alpha * p_defect)
    amp_defect_shadow.set_alpha(0.065 * alpha * p_defect)
    amp_label_defect.set_alpha(alpha * p_defect)
    amp_caption.set_alpha(alpha)


def update_phase_scene(t: float, alpha: float) -> None:
    set_axis_alpha(ax_phase, alpha)
    p_base = smoothstep(2.25, 3.05, t)
    p_defect = smoothstep(2.65, 3.55, t)
    xb, yb = trace_data(freq, phase_baseline, p_base)
    xd, yd = trace_data(freq, phase_perturbed, p_defect)
    for line in (phase_base_line, phase_base_shadow):
        line.set_data(xb, yb)
    for line in (phase_defect_line, phase_defect_shadow):
        line.set_data(xd, yd)
    phase_base_line.set_alpha(0.96 * alpha)
    phase_base_shadow.set_alpha(0.065 * alpha)
    phase_defect_line.set_alpha(0.96 * alpha * p_defect)
    phase_defect_shadow.set_alpha(0.065 * alpha * p_defect)
    phase_region.set_alpha(0.10 * alpha * smoothstep(3.25, 4.00, t))
    set_alpha([phase_caption, phase_micro], alpha)


def update_modal_scene(t: float, alpha: float) -> None:
    p = smoothstep(4.15, 5.10, t)
    chain_line.set_alpha(0.45 * alpha)
    for i, node in enumerate(chain_nodes):
        node.set_alpha(alpha * (0.45 + 0.45 * smoothstep(4.18 + 0.035 * i, 4.65 + 0.035 * i, t)))
    defect_glow.set_alpha(0.18 * alpha * (0.65 + 0.35 * np.sin(2.0 * np.pi * t / DURATION) ** 2))
    set_alpha([mode_s_line, mode_a_line, modal_label_1, modal_label_2], alpha * p)
    set_alpha([modal_arrow, modal_arrow_head], alpha * smoothstep(4.75, 5.35, t))
    set_alpha([modal_eq, modal_inner_1, modal_inner_2], alpha * smoothstep(5.05, 5.70, t))
    modal_caption.set_alpha(alpha)


def update_sphere_scene(t: float, alpha: float, topology_alpha: float, final_alpha: float) -> None:
    draw_p = smoothstep(5.95, 8.10, t)
    idx = max(3, int(draw_p * (len(traj_base) - 1)))
    current_base = traj_base[:idx]
    current_defect = traj_defect[:idx]
    traj_base_line.set_data(current_base[:, 0], current_base[:, 1])
    traj_defect_line.set_data(current_defect[:, 0], current_defect[:, 1])
    traj_base_soft.set_data(current_base[:, 0], current_base[:, 1])
    traj_defect_soft.set_data(current_defect[:, 0], current_defect[:, 1])

    point = current_defect[-1]
    state_dot_glow.center = (float(point[0]), float(point[1]))
    state_dot.center = (float(point[0]), float(point[1]))
    sphere_shadow.set_alpha(0.22 * alpha)
    sphere_shell.set_alpha(0.48 * alpha)
    for line in meridian_lines:
        line.set_alpha(0.18 * alpha)
    equator_line.set_alpha(0.28 * alpha)
    traj_base_line.set_alpha(0.80 * alpha * draw_p)
    traj_defect_line.set_alpha(0.86 * alpha * draw_p)
    traj_base_soft.set_alpha(0.065 * alpha * draw_p)
    traj_defect_soft.set_alpha(0.080 * alpha * draw_p)
    dot_alpha = alpha * smoothstep(6.25, 6.75, t)
    state_dot_glow.set_alpha(0.16 * dot_alpha)
    state_dot.set_alpha(dot_alpha)

    fill_path = np.vstack([traj_defect[:idx:7], [[0.0, 0.0]]])
    if len(fill_path) >= 4:
        trajectory_fill.set_xy(fill_path)
    trajectory_fill.set_alpha(0.10 * topology_alpha)
    set_alpha([sphere_caption, sphere_eq_1, sphere_eq_2, sphere_eq_3, traj_label_b, traj_label_d], alpha * (1.0 - final_alpha))
    set_alpha(topology_artists, topology_alpha * (1.0 - final_alpha))
    set_alpha(final_artists, final_alpha)


def update(frame: int) -> list:
    """Animate the full editorial story."""
    t = frame / FPS
    amp_alpha = fade_window(t, 0.05, 0.45, 2.05, 2.75)
    phase_alpha = fade_window(t, 2.05, 2.55, 4.15, 4.85)
    modal_alpha = fade_window(t, 4.10, 4.75, 6.10, 6.95)
    sphere_alpha = smoothstep(5.65, 6.45, t) * (1.0 - 0.24 * smoothstep(9.35, 9.90, t))
    topology_alpha = smoothstep(7.65, 8.35, t) * (1.0 - 0.30 * smoothstep(9.35, 9.90, t))
    final_alpha = smoothstep(8.55, 9.25, t)

    update_amplitude_scene(t, amp_alpha)
    update_phase_scene(t, phase_alpha)
    update_modal_scene(t, modal_alpha)
    update_sphere_scene(t, sphere_alpha, topology_alpha, final_alpha)
    return []


def save_preview() -> None:
    """Save a final-frame preview still."""
    update(int(9.35 * FPS))
    fig.savefig(PNG_PATH, dpi=DPI)


def resolve_ffmpeg() -> str | None:
    """Find system ffmpeg or use imageio-ffmpeg as a local fallback."""
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
    """Create a web-friendlier full-resolution GIF using an optimized palette."""
    palette_filter = "fps=30,scale=1920:1080:flags=lanczos,palettegen=max_colors=160:stats_mode=diff"
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
    mp4_writer = animation.FFMpegWriter(
        fps=FPS,
        codec="libx264",
        bitrate=9500,
        extra_args=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
    )
    anim.save(MP4_PATH, writer=mp4_writer, dpi=DPI)

    print(f"Saving GIF to {GIF_PATH} ...")
    save_gif_from_mp4(ffmpeg_path)

    print("Created:")
    print(f"  {MP4_PATH}")
    print(f"  {GIF_PATH}")
    print(f"  {PNG_PATH}")


if __name__ == "__main__":
    main()
