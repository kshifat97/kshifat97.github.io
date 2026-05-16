"""
Generate a polished scientific dashboard animation for a two-mass Hertzian
contact system with scrolling time response, distinct FFT spectra, and an
elastic-bit state inset.

How to run:
    python generate_hertzian_dashboard_animation.py

Outputs:
    outputs/hertzian_dashboard_animation.mp4
    outputs/hertzian_dashboard_animation.gif
    outputs/hertzian_dashboard_preview.png

Notes:
    MP4 export requires ffmpeg on PATH. On Windows, install it with:
        winget install --id Gyan.FFmpeg -e
    If system ffmpeg is not available, the script can also use imageio-ffmpeg:
        python -m pip install imageio-ffmpeg
"""

from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path


def require_package(import_name: str, install_name: str | None = None) -> None:
    """Fail early with an actionable dependency message."""
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
from matplotlib import patheffects
from matplotlib.patches import Circle, Ellipse, FancyBboxPatch, Rectangle


# ---------------------------------------------------------------------------
# Output and animation settings
# ---------------------------------------------------------------------------

OUT_DIR = Path("outputs")
MP4_PATH = OUT_DIR / "hertzian_dashboard_animation.mp4"
GIF_PATH = OUT_DIR / "hertzian_dashboard_animation.gif"
PNG_PATH = OUT_DIR / "hertzian_dashboard_preview.png"

FPS = 30
DURATION = 10.0
N_FRAMES = int(FPS * DURATION)
FIGSIZE = (19.2, 10.8)
DPI = 100

CYAN = "#36c5ff"
CYAN_SOFT = "#8ce6ff"
AMBER = "#ffb13b"
AMBER_SOFT = "#ffd38a"
TEXT = "#edf6ff"
MUTED = "#9db0c7"
PANEL_FACE = "#07182b"
GRID = "#24405f"


# ---------------------------------------------------------------------------
# Physics-inspired time response and contact signals
# ---------------------------------------------------------------------------


def mass_1_signal(t: np.ndarray | float) -> np.ndarray | float:
    """Prescribed displacement for Mass 1; frequencies tile the 10 s loop."""
    return (
        0.088 * np.sin(2.0 * np.pi * 0.4 * t + 0.35)
        + 0.048 * np.sin(2.0 * np.pi * 0.8 * t + 2.10)
        + 0.026 * np.sin(2.0 * np.pi * 1.3 * t + 1.15)
    )


def mass_2_signal(t: np.ndarray | float) -> np.ndarray | float:
    """Prescribed displacement for Mass 2 with distinct but coupled character."""
    return (
        0.078 * np.sin(2.0 * np.pi * 0.5 * t + 2.15)
        + 0.054 * np.sin(2.0 * np.pi * 0.9 * t + 0.58)
        + 0.022 * np.sin(2.0 * np.pi * 1.4 * t + 2.85)
    )


def smooth_contact_metrics(t: float) -> tuple[float, float]:
    """Return visual compression and unloading gap cues from relative motion."""
    relative = mass_1_signal(t) - mass_2_signal(t)
    compression = 0.028 * np.log1p(np.exp(34.0 * (relative + 0.018)))
    gap = 0.024 * np.log1p(np.exp(30.0 * (-relative - 0.012)))
    return float(min(compression, 0.095)), float(min(gap, 0.070))


# ---------------------------------------------------------------------------
# Smooth pseudo-random FFT spectra with separated peak families
# ---------------------------------------------------------------------------


def make_peak_params(
    base_centers: list[float],
    base_amplitudes: list[float],
    base_widths: list[float],
    seed: int,
) -> dict[str, np.ndarray]:
    """Create deterministic low-frequency modulation parameters per peak."""
    rng = np.random.default_rng(seed)
    n = len(base_centers)
    return {
        "base_centers": np.asarray(base_centers, dtype=float),
        "base_amplitudes": np.asarray(base_amplitudes, dtype=float),
        "base_widths": np.asarray(base_widths, dtype=float),
        "center_drift_1": rng.uniform(0.09, 0.20, n),
        "center_drift_2": rng.uniform(0.035, 0.095, n),
        "amp_mod_1": rng.uniform(0.12, 0.24, n),
        "amp_mod_2": rng.uniform(0.05, 0.12, n),
        "width_mod": rng.uniform(0.045, 0.11, n),
        "center_cycles_1": rng.integers(1, 4, n),
        "center_cycles_2": rng.integers(2, 6, n),
        "amp_cycles_1": rng.integers(1, 5, n),
        "amp_cycles_2": rng.integers(2, 6, n),
        "width_cycles": rng.integers(1, 4, n),
        "phase": rng.uniform(0.0, 2.0 * np.pi, (5, n)),
    }


MASS_1_FFT = make_peak_params(
    base_centers=[4.8, 10.9, 18.2, 26.5, 34.0],
    base_amplitudes=[0.72, 0.92, 0.62, 0.38, 0.48],
    base_widths=[0.62, 0.82, 0.92, 1.08, 1.34],
    seed=22,
)

MASS_2_FFT = make_peak_params(
    base_centers=[7.55, 14.6, 22.8, 30.7, 38.2],
    base_amplitudes=[0.48, 0.58, 0.50, 0.42, 0.34],
    base_widths=[0.70, 0.88, 0.96, 1.14, 1.38],
    seed=83,
)


def peak_properties(params: dict[str, np.ndarray], t: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Evaluate smoothly drifting peak centers, amplitudes, and widths."""
    tau = t / DURATION
    phase = params["phase"]
    centers = (
        params["base_centers"]
        + params["center_drift_1"] * np.sin(2.0 * np.pi * params["center_cycles_1"] * tau + phase[0])
        + params["center_drift_2"] * np.sin(2.0 * np.pi * params["center_cycles_2"] * tau + phase[1])
    )
    amplitudes = params["base_amplitudes"] * (
        1.0
        + params["amp_mod_1"] * np.sin(2.0 * np.pi * params["amp_cycles_1"] * tau + phase[2])
        + params["amp_mod_2"] * np.sin(2.0 * np.pi * params["amp_cycles_2"] * tau + phase[3])
    )
    widths = params["base_widths"] * (
        1.0 + params["width_mod"] * np.sin(2.0 * np.pi * params["width_cycles"] * tau + phase[4])
    )
    return centers, np.clip(amplitudes, 0.12, None), np.clip(widths, 0.35, None)


def enforce_peak_separation(c1: np.ndarray, c2: np.ndarray, min_sep: float = 2.0) -> tuple[np.ndarray, np.ndarray]:
    """Smooth-looking guard rail that prevents cross-family peak overlap."""
    adjusted_1 = c1.copy()
    adjusted_2 = c2.copy()
    for i in range(len(adjusted_1)):
        for j in range(len(adjusted_2)):
            diff = adjusted_2[j] - adjusted_1[i]
            if abs(diff) < min_sep:
                direction = 1.0 if diff >= 0.0 else -1.0
                push = 0.5 * (min_sep - abs(diff) + 0.02) * direction
                adjusted_1[i] -= push
                adjusted_2[j] += push
    return adjusted_1, adjusted_2


def spectrum(freq: np.ndarray, params: dict[str, np.ndarray], t: float, other: dict[str, np.ndarray] | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Build a Gaussian-peak FFT spectrum with independent drifting centers."""
    centers, amplitudes, widths = peak_properties(params, t)
    if other is not None:
        other_centers, _, _ = peak_properties(other, t)
        if params is MASS_1_FFT:
            centers, _ = enforce_peak_separation(centers, other_centers)
        else:
            _, centers = enforce_peak_separation(other_centers, centers)

    baseline = 0.018 + 0.010 * np.sin(2.0 * np.pi * (freq / 42.0 + t / DURATION)) ** 2
    y = baseline.copy()
    for center, amplitude, width in zip(centers, amplitudes, widths):
        y += amplitude * np.exp(-0.5 * ((freq - center) / width) ** 2)
    return y, centers


def validate_fft_separation() -> float:
    """Sample the full loop and report the closest cross-family peak spacing."""
    min_seen = float("inf")
    for frame in range(N_FRAMES + 1):
        t = frame / FPS
        c1, _, _ = peak_properties(MASS_1_FFT, t)
        c2, _, _ = peak_properties(MASS_2_FFT, t)
        c1, c2 = enforce_peak_separation(c1, c2)
        min_seen = min(min_seen, float(np.min(np.abs(c1[:, None] - c2[None, :]))))
    return min_seen


# ---------------------------------------------------------------------------
# Figure styling helpers
# ---------------------------------------------------------------------------


plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 12,
        "axes.edgecolor": "#4c6f96",
        "axes.labelcolor": "#bccbde",
        "xtick.color": "#aab9cc",
        "ytick.color": "#aab9cc",
        "text.color": TEXT,
        "figure.facecolor": "#020913",
        "savefig.facecolor": "#020913",
    }
)


def add_background(fig: plt.Figure) -> None:
    """Add a premium dark gradient with restrained cyan/amber glow fields."""
    ax_bg = fig.add_axes([0.0, 0.0, 1.0, 1.0], zorder=-30)
    ax_bg.set_axis_off()
    y, x = np.mgrid[0:1:540j, 0:1:960j]
    base = np.zeros((540, 960, 3), dtype=float)
    base[..., 0] = 0.010
    base[..., 1] = 0.035
    base[..., 2] = 0.075

    def glow(cx: float, cy: float, sx: float, sy: float, color: tuple[float, float, float], strength: float) -> None:
        field = np.exp(-(((x - cx) / sx) ** 2 + ((y - cy) / sy) ** 2))
        for channel, value in enumerate(color):
            base[..., channel] += strength * value * field

    glow(0.25, 0.32, 0.36, 0.28, (0.02, 0.34, 0.78), 0.26)
    glow(0.82, 0.28, 0.34, 0.26, (0.02, 0.18, 0.52), 0.22)
    glow(0.50, 0.82, 0.65, 0.34, (0.02, 0.15, 0.36), 0.20)
    glow(0.35, 0.14, 0.30, 0.16, (0.75, 0.28, 0.02), 0.08)
    ax_bg.imshow(np.clip(base, 0.0, 1.0), origin="lower", aspect="auto", extent=[0, 1, 0, 1])


def add_panel(fig: plt.Figure, bounds: tuple[float, float, float, float], radius: float = 0.012) -> None:
    """Draw a rounded glass panel behind an axes/card region."""
    x, y, w, h = bounds
    for pad, alpha, lw in [(0.006, 0.10, 1.8), (0.0025, 0.16, 1.1)]:
        glow = FancyBboxPatch(
            (x - pad, y - pad),
            w + 2.0 * pad,
            h + 2.0 * pad,
            boxstyle=f"round,pad=0.0,rounding_size={radius + pad}",
            transform=fig.transFigure,
            facecolor=(0.07, 0.35, 0.70, alpha * 0.25),
            edgecolor=(0.45, 0.78, 1.0, alpha),
            linewidth=lw,
            zorder=-4,
        )
        fig.patches.append(glow)
    panel = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.0,rounding_size={radius}",
        transform=fig.transFigure,
        facecolor=(0.018, 0.075, 0.135, 0.70),
        edgecolor=(0.48, 0.75, 1.0, 0.48),
        linewidth=0.9,
        zorder=-3,
    )
    fig.patches.append(panel)


def style_plot_axes(ax: plt.Axes) -> None:
    """Apply the shared dark dashboard plot styling."""
    ax.set_facecolor((0.01, 0.045, 0.085, 0.42))
    ax.grid(True, color=GRID, linewidth=0.8, alpha=0.58, linestyle=":")
    for spine in ax.spines.values():
        spine.set_color("#55789f")
        spine.set_alpha(0.62)
        spine.set_linewidth(0.9)
    ax.tick_params(length=4, colors="#aab9cc")


fig = plt.figure(figsize=FIGSIZE, dpi=DPI, facecolor="#020913")
add_background(fig)

CONTACT_CARD = (0.040, 0.505, 0.455, 0.365)
TIME_CARD = (0.040, 0.075, 0.455, 0.365)
BIT_CARD = (0.510, 0.505, 0.455, 0.365)
FFT_CARD = (0.510, 0.075, 0.455, 0.365)

for bounds in (TIME_CARD, CONTACT_CARD, FFT_CARD, BIT_CARD):
    add_panel(fig, bounds)

fig.text(
    0.040,
    0.935,
    "Direct Hertzian Contact: Two-Mass Oscillator",
    fontsize=29,
    fontweight="bold",
    color=TEXT,
    ha="left",
    va="center",
)
fig.text(
    0.040,
    0.895,
    "dynamic response | spectral evolution | elastic-bit representation",
    fontsize=11,
    color="#8ca0ba",
    ha="left",
    va="center",
)

fig.text(0.064, 0.835, "DIRECT HERTZIAN CONTACT", fontsize=13, fontweight="bold", color="#d8ecff", ha="left")
fig.text(0.064, 0.405, "TIME RESPONSE", fontsize=13, fontweight="bold", color="#d8ecff", ha="left")
fig.text(0.534, 0.835, "ELASTIC BIT STATE", fontsize=13, fontweight="bold", color="#d8ecff", ha="left")
fig.text(0.534, 0.405, "FFT AMPLITUDE SPECTRA", fontsize=13, fontweight="bold", color="#d8ecff", ha="left")


# ---------------------------------------------------------------------------
# Time-response panel
# ---------------------------------------------------------------------------

ax_time = fig.add_axes([0.078, 0.145, 0.390, 0.225], zorder=2)
style_plot_axes(ax_time)
WINDOW = 4.0
HISTORY = 520
t_window = np.linspace(-WINDOW, 0.0, HISTORY)
line1_glow, = ax_time.plot([], [], color=CYAN, lw=7.5, alpha=0.12)
line2_glow, = ax_time.plot([], [], color=AMBER, lw=7.5, alpha=0.12)
line1, = ax_time.plot([], [], color=CYAN, lw=2.6, label="Mass 1")
line2, = ax_time.plot([], [], color=AMBER, lw=2.6, label="Mass 2")
time_cursor = ax_time.axvline(0.0, color="#e3f5ff", lw=1.2, alpha=0.25)
ax_time.set_xlim(-WINDOW, 0.0)
ax_time.set_ylim(-0.18, 0.18)
ax_time.set_xlabel("Time window (s)", labelpad=8)
ax_time.set_ylabel("Displacement", labelpad=8)
time_legend = ax_time.legend(
    loc="upper right",
    frameon=True,
    framealpha=0.48,
    facecolor="#061526",
    edgecolor="#355f88",
)
for legend_line in time_legend.get_lines():
    legend_line.set_linewidth(3.0)


# ---------------------------------------------------------------------------
# Hertzian contact panel
# ---------------------------------------------------------------------------

ax_contact = fig.add_axes([0.058, 0.535, 0.410, 0.295], zorder=2)
ax_contact.set_facecolor((0.0, 0.0, 0.0, 0.0))
ax_contact.set_aspect("equal", adjustable="box")
ax_contact.set_xlim(-2.55, 2.55)
ax_contact.set_ylim(-1.35, 1.30)
ax_contact.axis("off")

ring_theta = np.linspace(-0.08 * np.pi, 1.08 * np.pi, 180)
for scale, alpha in [(1.0, 0.22), (1.22, 0.12), (1.44, 0.08)]:
    ax_contact.plot(
        1.98 * scale * np.cos(ring_theta),
        0.82 * scale * np.sin(ring_theta) - 0.05,
        color="#4da7ff",
        lw=0.8,
        alpha=alpha,
        linestyle="-",
    )

for x_line in np.linspace(-1.95, 1.95, 9):
    ax_contact.plot([x_line - 0.10, x_line + 0.10], [-1.06, -0.92], color="#244c73", lw=1.2, alpha=0.45)
ax_contact.plot([-2.05, 2.05], [-1.00, -1.00], color="#7092ad", lw=2.1, alpha=0.58, solid_capstyle="round")

RADIUS = 0.66
LEFT_REST = -0.66
RIGHT_REST = 0.66
VISUAL_GAIN = 0.92

shadow1 = Ellipse((LEFT_REST, -0.79), 1.18, 0.18, facecolor="#000000", edgecolor="none", alpha=0.34, zorder=3)
shadow2 = Ellipse((RIGHT_REST, -0.79), 1.18, 0.18, facecolor="#000000", edgecolor="none", alpha=0.34, zorder=3)
glow1 = Ellipse((LEFT_REST, 0.0), 1.55, 1.55, facecolor=CYAN, edgecolor="none", alpha=0.08, zorder=4)
glow2 = Ellipse((RIGHT_REST, 0.0), 1.55, 1.55, facecolor=AMBER, edgecolor="none", alpha=0.08, zorder=4)
mass1 = Ellipse((LEFT_REST, 0.0), 2 * RADIUS, 2 * RADIUS, facecolor="#129ce4", edgecolor=CYAN_SOFT, lw=1.6, zorder=6)
mass2 = Ellipse((RIGHT_REST, 0.0), 2 * RADIUS, 2 * RADIUS, facecolor="#d98b26", edgecolor=AMBER_SOFT, lw=1.6, zorder=6)
for patch in (shadow1, shadow2, glow1, glow2, mass1, mass2):
    ax_contact.add_patch(patch)

mass1.set_path_effects([patheffects.withStroke(linewidth=5, foreground="#0e3d5f", alpha=0.75)])
mass2.set_path_effects([patheffects.withStroke(linewidth=5, foreground="#5b3510", alpha=0.70)])


def sphere_layers(cx: float, color: str) -> list[Circle]:
    """Create translucent highlight layers for a dimensional sphere look."""
    layers: list[Circle] = []
    for dx, dy, radius, alpha, z in [
        (-0.16, 0.18, 0.54, 0.12, 7),
        (-0.29, 0.30, 0.23, 0.24, 8),
        (-0.36, 0.38, 0.10, 0.36, 9),
    ]:
        layer = Circle((cx + dx, dy), radius, facecolor=color, edgecolor="none", alpha=alpha, zorder=z)
        ax_contact.add_patch(layer)
        layers.append(layer)
    return layers


layers1 = sphere_layers(LEFT_REST, "#d9f7ff")
layers2 = sphere_layers(RIGHT_REST, "#fff0c8")

contact_glow = Ellipse((0.0, 0.0), 0.08, 0.92, facecolor="#ffffff", edgecolor="#d9fbff", lw=0.8, alpha=0.24, zorder=10)
contact_core = Ellipse((0.0, 0.0), 0.022, 0.62, facecolor="#faffff", edgecolor="none", alpha=0.42, zorder=11)
gap_slit = Rectangle((-0.006, -0.47), 0.012, 0.94, facecolor="#020913", edgecolor="#79d8ff", lw=0.8, alpha=0.0, zorder=12)
for patch in (contact_glow, contact_core, gap_slit):
    ax_contact.add_patch(patch)

mass1_label = ax_contact.text(LEFT_REST, 0.98, "Mass 1", ha="center", va="center", fontsize=14, fontweight="bold", color="#e3f8ff")
mass2_label = ax_contact.text(RIGHT_REST, 0.98, "Mass 2", ha="center", va="center", fontsize=14, fontweight="bold", color="#ffe7bd")
compression_label = ax_contact.text(0.0, -1.20, "Compression", ha="center", va="center", fontsize=11, color="#bceeff")
bracket_line, = ax_contact.plot([], [], color="#bceeff", lw=1.2, alpha=0.76)
bracket_left, = ax_contact.plot([], [], color="#bceeff", lw=1.2, alpha=0.76)
bracket_right, = ax_contact.plot([], [], color="#bceeff", lw=1.2, alpha=0.76)


# ---------------------------------------------------------------------------
# FFT amplitude spectra panel
# ---------------------------------------------------------------------------

ax_fft = fig.add_axes([0.555, 0.145, 0.390, 0.225], zorder=2)
style_plot_axes(ax_fft)
freq = np.linspace(0.0, 41.0, 650)
fft1_glow, = ax_fft.plot([], [], color=CYAN, lw=7.0, alpha=0.12)
fft2_glow, = ax_fft.plot([], [], color=AMBER, lw=7.0, alpha=0.13)
fft1_line, = ax_fft.plot([], [], color=CYAN, lw=2.35, label="Mass 1")
fft2_line, = ax_fft.plot([], [], color=AMBER, lw=2.35, label="Mass 2")
fft1_fill = ax_fft.fill_between(freq, np.zeros_like(freq), np.zeros_like(freq), color=CYAN, alpha=0.12)
fft2_fill = ax_fft.fill_between(freq, np.zeros_like(freq), np.zeros_like(freq), color=AMBER, alpha=0.12)
ax_fft.set_xlim(0.0, 41.0)
ax_fft.set_ylim(0.0, 1.05)
ax_fft.set_xlabel("Frequency (Hz)", labelpad=8)
ax_fft.set_ylabel("Amplitude", labelpad=8)
fft_legend = ax_fft.legend(
    loc="upper right",
    frameon=True,
    framealpha=0.48,
    facecolor="#061526",
    edgecolor="#355f88",
)
for legend_line in fft_legend.get_lines():
    legend_line.set_linewidth(3.0)


# ---------------------------------------------------------------------------
# Elastic-bit state panel
# ---------------------------------------------------------------------------

ax_bit_state = fig.add_axes([0.555, 0.555, 0.155, 0.275], zorder=3)
ax_bit_state.set_facecolor((0.0, 0.0, 0.0, 0.0))
ax_bit_state.set_xlim(-1.05, 1.05)
ax_bit_state.set_ylim(-1.05, 1.05)
ax_bit_state.set_aspect("equal", adjustable="box")
ax_bit_state.axis("off")

ax_bit_text = fig.add_axes([0.730, 0.575, 0.205, 0.230], zorder=3)
ax_bit_text.set_facecolor((0.0, 0.0, 0.0, 0.0))
ax_bit_text.set_xlim(0, 1)
ax_bit_text.set_ylim(0, 1)
ax_bit_text.axis("off")

bit_center = np.array([0.0, 0.0])
bit_radius = 0.82
bit_sphere = Circle(bit_center, bit_radius, facecolor=(0.05, 0.20, 0.34, 0.36), edgecolor="#3e8ed0", lw=1.0, alpha=0.78)
ax_bit_state.add_patch(bit_sphere)
ax_bit_state.add_patch(Ellipse(bit_center, 2 * bit_radius, 0.42, facecolor="none", edgecolor="#5f88b2", lw=0.8, alpha=0.42))
ax_bit_state.add_patch(Ellipse(bit_center, 0.42, 2 * bit_radius, facecolor="none", edgecolor="#5f88b2", lw=0.8, alpha=0.34))
ax_bit_state.plot([0.0, 0.0], [-bit_radius, bit_radius], color="#70a7db", lw=0.8, alpha=0.55)
ax_bit_state.plot([-bit_radius, bit_radius], [0.0, 0.0], color="#70a7db", lw=0.8, alpha=0.50)
state_zero = Circle((0.0, bit_radius), 0.082, facecolor=CYAN, edgecolor="#dff8ff", lw=0.8, alpha=0.92)
state_one = Circle((0.0, -bit_radius), 0.082, facecolor=AMBER, edgecolor="#fff1cb", lw=0.8, alpha=0.92)
state_point = Circle(bit_center, 0.080, facecolor="#f2fbff", edgecolor=CYAN, lw=1.2, alpha=0.96)
state_trace, = ax_bit_state.plot([], [], color="#c6f4ff", lw=1.2, alpha=0.56)
for patch in (state_zero, state_one, state_point):
    ax_bit_state.add_patch(patch)
state_point.set_path_effects([patheffects.withStroke(linewidth=6, foreground=CYAN, alpha=0.24)])
ax_bit_text.text(0.52, 0.78, r"$|\psi\rangle = \alpha\ |0\rangle + \beta\ |1\rangle$", ha="center", va="center", fontsize=13.0, color="#d8e9ff")
alpha_text = ax_bit_text.text(0.20, 0.45, "", ha="left", va="center", fontsize=12.0, color="#cfe6ff")
beta_text = ax_bit_text.text(0.20, 0.23, "", ha="left", va="center", fontsize=12.0, color="#ffe4b8")
ax_bit_text.scatter([0.12], [0.45], s=36, color=CYAN, alpha=0.95)
ax_bit_text.scatter([0.12], [0.23], s=36, color=AMBER, alpha=0.95)


# ---------------------------------------------------------------------------
# Animation callbacks
# ---------------------------------------------------------------------------


def update_time_panel(t: float) -> None:
    samples = t + t_window
    y1 = mass_1_signal(samples)
    y2 = mass_2_signal(samples)
    for line in (line1, line1_glow):
        line.set_data(t_window, y1)
    for line in (line2, line2_glow):
        line.set_data(t_window, y2)


def update_contact_panel(t: float) -> None:
    y1 = float(mass_1_signal(t))
    y2 = float(mass_2_signal(t))
    compression, gap = smooth_contact_metrics(t)
    x1 = LEFT_REST + VISUAL_GAIN * y1
    x2 = RIGHT_REST + VISUAL_GAIN * y2
    center = 0.5 * (x1 + x2)
    flatten = min(0.085, 0.80 * compression)

    mass1.center = (x1, 0.0)
    mass2.center = (x2, 0.0)
    mass1.width = 2 * RADIUS - flatten
    mass2.width = 2 * RADIUS - flatten
    mass1.height = 2 * RADIUS + 0.22 * flatten
    mass2.height = 2 * RADIUS + 0.22 * flatten

    glow1.center = (x1, 0.0)
    glow2.center = (x2, 0.0)
    glow1.width = glow1.height = 1.42 + 1.4 * compression
    glow2.width = glow2.height = 1.42 + 1.4 * compression
    glow1.set_alpha(0.070 + 0.45 * compression)
    glow2.set_alpha(0.070 + 0.42 * compression)

    shadow1.center = (x1, -0.79)
    shadow2.center = (x2, -0.79)
    shadow1.width = 1.10 + 0.8 * abs(y1)
    shadow2.width = 1.10 + 0.8 * abs(y2)

    for layer, (dx, dy) in zip(layers1, [(-0.16, 0.18), (-0.29, 0.30), (-0.36, 0.38)]):
        layer.center = (x1 + dx, dy)
    for layer, (dx, dy) in zip(layers2, [(-0.16, 0.18), (-0.29, 0.30), (-0.36, 0.38)]):
        layer.center = (x2 + dx, dy)

    contact_glow.center = (center, 0.0)
    contact_glow.width = 0.055 + 0.75 * compression
    contact_glow.height = 0.70 + 2.8 * compression
    contact_glow.set_alpha(0.12 + min(0.52, 4.7 * compression))
    contact_core.center = (center, 0.0)
    contact_core.width = 0.018 + 0.30 * compression
    contact_core.height = 0.50 + 2.2 * compression
    contact_core.set_alpha(0.16 + min(0.46, 4.5 * compression))
    gap_slit.set_x(center - max(0.010, 0.28 * gap) / 2.0)
    gap_slit.set_width(max(0.010, 0.28 * gap))
    gap_slit.set_alpha(min(0.34, 5.4 * gap))

    mass1_label.set_position((x1, 0.98))
    mass2_label.set_position((x2, 0.98))
    compression_label.set_text("Compression" if compression >= gap else "Unloading")
    compression_label.set_color("#bceeff" if compression >= gap else "#8da2b8")
    bracket_w = 0.26 + 1.2 * compression
    bracket_y = -1.075
    bracket_line.set_data([center - bracket_w, center + bracket_w], [bracket_y, bracket_y])
    bracket_left.set_data([center - bracket_w, center - bracket_w], [bracket_y, bracket_y + 0.095])
    bracket_right.set_data([center + bracket_w, center + bracket_w], [bracket_y, bracket_y + 0.095])


def update_fft_panel(t: float) -> None:
    global fft1_fill, fft2_fill
    s1, _ = spectrum(freq, MASS_1_FFT, t, other=MASS_2_FFT)
    s2, _ = spectrum(freq, MASS_2_FFT, t, other=MASS_1_FFT)
    fft1_line.set_data(freq, s1)
    fft2_line.set_data(freq, s2)
    fft1_glow.set_data(freq, s1)
    fft2_glow.set_data(freq, s2)
    fft1_fill.remove()
    fft2_fill.remove()
    fft1_fill = ax_fft.fill_between(freq, 0.0, s1, color=CYAN, alpha=0.115)
    fft2_fill = ax_fft.fill_between(freq, 0.0, s2, color=AMBER, alpha=0.115)


def update_elastic_bit_panel(t: float) -> None:
    relative = float(mass_1_signal(t) - mass_2_signal(t))
    tau = t / DURATION
    theta = 0.50 * np.pi + 0.52 * np.tanh(7.5 * relative)
    phi = 2.0 * np.pi * tau + 0.55 * np.sin(2.0 * np.pi * 2.0 * tau + 0.8)
    px = bit_center[0] + bit_radius * 0.63 * np.sin(theta) * np.cos(phi)
    py = bit_center[1] + bit_radius * 0.92 * np.cos(theta)
    state_point.center = (px, py)

    trail_tau = np.linspace(max(0.0, tau - 0.18), tau, 42)
    trail_x: list[float] = []
    trail_y: list[float] = []
    for trail in trail_tau:
        trail_t = trail * DURATION
        trail_rel = float(mass_1_signal(trail_t) - mass_2_signal(trail_t))
        trail_theta = 0.50 * np.pi + 0.52 * np.tanh(7.5 * trail_rel)
        trail_phi = 2.0 * np.pi * trail + 0.55 * np.sin(2.0 * np.pi * 2.0 * trail + 0.8)
        trail_x.append(bit_center[0] + bit_radius * 0.63 * np.sin(trail_theta) * np.cos(trail_phi))
        trail_y.append(bit_center[1] + bit_radius * 0.92 * np.cos(trail_theta))
    state_trace.set_data(trail_x, trail_y)

    alpha_mag = 0.72 + 0.025 * np.sin(2.0 * np.pi * tau + 0.35)
    beta_mag = np.sqrt(max(0.0, 1.0 - alpha_mag**2))
    alpha_phase = 0.15 + 0.025 * np.sin(2.0 * np.pi * 2.0 * tau + 1.2)
    beta_phase = -0.32 + 0.030 * np.sin(2.0 * np.pi * 3.0 * tau + 2.1)
    alpha_text.set_text(rf"$\alpha$ = {alpha_mag:.2f} $\angle$ {alpha_phase:.2f}$\pi$")
    beta_text.set_text(rf"$\beta$ = {beta_mag:.2f} $\angle$ {beta_phase:.2f}$\pi$")


def update(frame: int) -> list:
    """Synchronized animation update for every dashboard panel."""
    t = frame / FPS
    update_time_panel(t)
    update_contact_panel(t)
    update_fft_panel(t)
    update_elastic_bit_panel(t)
    return []


def save_preview() -> None:
    """Save a polished still frame for quick embedding checks."""
    update(int(0.37 * N_FRAMES))
    fig.savefig(PNG_PATH, dpi=DPI)


def resolve_ffmpeg() -> str | None:
    """Find system ffmpeg or fall back to imageio-ffmpeg if installed."""
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


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    min_sep = validate_fft_separation()
    print(f"Minimum Mass 1 / Mass 2 FFT peak separation over loop: {min_sep:.2f} Hz")
    if min_sep < 2.0:
        raise SystemExit("FFT peak separation validation failed; expected at least 2.0 Hz.")

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
        bitrate=10000,
        extra_args=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
    )
    anim.save(MP4_PATH, writer=mp4_writer, dpi=DPI)

    print(f"Saving GIF to {GIF_PATH} ...")
    gif_writer = animation.PillowWriter(fps=FPS)
    anim.save(GIF_PATH, writer=gif_writer, dpi=DPI)

    print("Created:")
    print(f"  {MP4_PATH}")
    print(f"  {GIF_PATH}")
    print(f"  {PNG_PATH}")


if __name__ == "__main__":
    main()
