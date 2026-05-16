"""
Generate a compact scientific animation of a two-mass Hertzian contact system.

How to run:
    python generate_hertzian_two_mass_animation.py

Outputs are written to:
    outputs/hertzian_two_mass_animation.mp4
    outputs/hertzian_two_mass_animation.gif
    outputs/hertzian_two_mass_preview.png
    outputs/hertzian_two_mass_preview.html

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
    """Give a clear setup message before importing optional runtime packages."""
    if importlib.util.find_spec(import_name) is None:
        package = install_name or import_name
        raise SystemExit(
            f"Missing Python package '{package}'. Install dependencies with:\n"
            f"    python -m pip install numpy matplotlib pillow\n"
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
from matplotlib.patches import Circle, Ellipse, Rectangle


# ---------------------------------------------------------------------------
# Output and animation settings
# ---------------------------------------------------------------------------

OUT_DIR = Path("outputs")
MP4_PATH = OUT_DIR / "hertzian_two_mass_animation.mp4"
GIF_PATH = OUT_DIR / "hertzian_two_mass_animation.gif"
PNG_PATH = OUT_DIR / "hertzian_two_mass_preview.png"
HTML_PATH = OUT_DIR / "hertzian_two_mass_preview.html"

FPS = 30
DURATION = 10.0
N_FRAMES = int(FPS * DURATION)
FIGSIZE = (19.2, 10.8)
DPI = 100


# ---------------------------------------------------------------------------
# Physics-inspired prescribed motion
# ---------------------------------------------------------------------------

RADIUS = 0.72
REST_CENTER_GAP = 2.0 * RADIUS
LEFT_REST_X = -0.72
RIGHT_REST_X = LEFT_REST_X + REST_CENTER_GAP
MOTION_SCALE = 0.55
CONTACT_SCALE = 2.25


def displacement_mass_1(t: np.ndarray | float) -> np.ndarray | float:
    """Smooth looped displacement for mass 1."""
    return MOTION_SCALE * (
        0.180 * np.sin(2.0 * np.pi * 0.6 * t)
        + 0.052 * np.sin(2.0 * np.pi * 1.2 * t + 0.70)
        + 0.026 * np.sin(2.0 * np.pi * 1.8 * t + 1.80)
    )


def displacement_mass_2(t: np.ndarray | float) -> np.ndarray | float:
    """Smooth looped displacement for mass 2 with coupled relative motion."""
    return MOTION_SCALE * (
        -0.155 * np.sin(2.0 * np.pi * 0.6 * t + 0.32)
        + 0.070 * np.sin(2.0 * np.pi * 1.2 * t + 2.38)
        - 0.018 * np.sin(2.0 * np.pi * 1.8 * t + 0.42)
    )


def contact_compression(t: np.ndarray | float) -> np.ndarray | float:
    """Positive visual compression based on relative center approach."""
    x1 = displacement_mass_1(t)
    x2 = displacement_mass_2(t)
    # x1 - x2 closes the center distance; softplus avoids hard visual switching.
    approach = CONTACT_SCALE * (x1 - x2)
    return 0.13 * np.log1p(np.exp(16.0 * (approach + 0.012))) / 16.0


def contact_gap(t: np.ndarray | float) -> np.ndarray | float:
    """Small air-gap cue when the visualized contact is unloading."""
    x1 = displacement_mass_1(t)
    x2 = displacement_mass_2(t)
    separation = CONTACT_SCALE * (x2 - x1)
    return 0.11 * np.log1p(np.exp(13.0 * (separation - 0.022))) / 13.0


def fft_profile(freq: np.ndarray, t: float) -> np.ndarray:
    """Live-looking FFT amplitude with smooth, looped peak modulation."""
    baseline = 0.028 + 0.012 * np.sin(2.0 * np.pi * (freq / 42.0 + 0.2 * t)) ** 2
    peaks = [
        (5.5, 0.62, 0.72, 0.00, 1.0),
        (12.0, 0.82, 0.52, 1.35, 2.0),
        (19.5, 1.10, 0.46, 2.10, 1.0),
        (27.0, 1.38, 0.34, 3.00, 3.0),
        (35.0, 1.72, 0.26, 4.25, 2.0),
    ]
    amp = baseline.copy()
    for center, width, strength, phase, mod_rate in peaks:
        modulation = 0.56 + 0.44 * np.sin(2.0 * np.pi * mod_rate * t / DURATION + phase) ** 2
        drift = 0.22 * np.sin(2.0 * np.pi * t / DURATION + phase)
        amp += strength * modulation * np.exp(-0.5 * ((freq - center - drift) / width) ** 2)
    return amp


# ---------------------------------------------------------------------------
# Figure construction
# ---------------------------------------------------------------------------

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 12,
        "axes.edgecolor": "#3a4656",
        "axes.labelcolor": "#b9c6d8",
        "xtick.color": "#8f9bad",
        "ytick.color": "#8f9bad",
        "text.color": "#e9f0fb",
        "figure.facecolor": "#091019",
        "savefig.facecolor": "#091019",
    }
)

fig = plt.figure(figsize=FIGSIZE, dpi=DPI, facecolor="#091019")
gs = fig.add_gridspec(
    2,
    2,
    width_ratios=[1.55, 1.0],
    height_ratios=[0.92, 1.18],
    left=0.055,
    right=0.965,
    top=0.875,
    bottom=0.075,
    hspace=0.28,
    wspace=0.17,
)

ax_time = fig.add_subplot(gs[0, :])
ax_system = fig.add_subplot(gs[1, 0])
ax_fft = fig.add_subplot(gs[1, 1])

for ax in (ax_time, ax_system, ax_fft):
    ax.set_facecolor("#0d1723")
    ax.grid(True, color="#253244", linewidth=0.8, alpha=0.55)
    for spine in ax.spines.values():
        spine.set_color("#334154")
        spine.set_linewidth(1.0)

fig.text(
    0.055,
    0.965,
    "Direct Hertzian Contact: Two-Mass Oscillator",
    fontsize=20,
    fontweight="bold",
    color="#f3f8ff",
    ha="left",
    va="top",
)
fig.text(
    0.965,
    0.965,
    "smooth prescribed response | live spectral view",
    fontsize=11,
    color="#7f8ea3",
    ha="right",
    va="top",
)


# Time-response panel
WINDOW = 4.0
N_HISTORY = 430
t_window = np.linspace(-WINDOW, 0.0, N_HISTORY)
line_m1, = ax_time.plot([], [], color="#39c5ff", lw=2.5, label="Mass 1")
line_m2, = ax_time.plot([], [], color="#ffb84d", lw=2.5, label="Mass 2")
time_cursor = ax_time.axvline(0.0, color="#dce7f5", lw=1.1, alpha=0.42)
ax_time.set_xlim(-WINDOW, 0.0)
ax_time.set_ylim(-0.18, 0.18)
ax_time.set_title("Time response", loc="left", pad=12, fontsize=15, fontweight="bold")
ax_time.set_xlabel("time window (s)")
ax_time.set_ylabel("displacement")
ax_time.legend(
    loc="upper right",
    frameon=True,
    framealpha=0.18,
    facecolor="#121f2f",
    edgecolor="#45556c",
)


# Mechanical-system panel
ax_system.set_title("", pad=0)
ax_system.set_aspect("equal", adjustable="box")
ax_system.set_xlim(-2.15, 2.15)
ax_system.set_ylim(-1.28, 1.30)
ax_system.set_xticks([])
ax_system.set_yticks([])
ax_system.grid(False)
ax_system.set_xlabel("")
ax_system.set_ylabel("")

rail_y = -0.93
ax_system.plot(
    [-1.75, 1.75],
    [rail_y, rail_y],
    color="#5a6a7c",
    lw=3.0,
    alpha=0.75,
    solid_capstyle="round",
)
for x_tick in np.linspace(-1.55, 1.55, 9):
    ax_system.plot(
        [x_tick - 0.07, x_tick + 0.07],
        [rail_y - 0.06, rail_y + 0.06],
        color="#344457",
        lw=1.8,
        alpha=0.7,
    )

shadow1 = Ellipse((LEFT_REST_X, -0.78), 1.13, 0.17, color="#000000", alpha=0.32)
shadow2 = Ellipse((RIGHT_REST_X, -0.78), 1.13, 0.17, color="#000000", alpha=0.32)
mass1 = Ellipse(
    (LEFT_REST_X, 0.0),
    2.0 * RADIUS,
    2.0 * RADIUS,
    facecolor="#2f9ed8",
    edgecolor="#a9e7ff",
    lw=1.8,
)
mass2 = Ellipse(
    (RIGHT_REST_X, 0.0),
    2.0 * RADIUS,
    2.0 * RADIUS,
    facecolor="#d89a32",
    edgecolor="#ffe3a5",
    lw=1.8,
)

for patch in (shadow1, shadow2, mass1, mass2):
    ax_system.add_patch(patch)

mass1.set_path_effects([patheffects.withStroke(linewidth=5, foreground="#112635", alpha=0.75)])
mass2.set_path_effects([patheffects.withStroke(linewidth=5, foreground="#332411", alpha=0.75)])

contact_patch = Ellipse(
    (0.0, 0.0),
    0.09,
    0.98,
    facecolor="#ffffff",
    edgecolor="#d8fbff",
    lw=1.0,
    alpha=0.28,
    zorder=8,
)
contact_core = Ellipse(
    (0.0, 0.0),
    0.028,
    0.72,
    facecolor="#f5ffff",
    edgecolor="none",
    alpha=0.45,
    zorder=9,
)
gap_patch = Rectangle(
    (-0.01, -0.50),
    0.02,
    1.0,
    facecolor="#091019",
    edgecolor="#8fc8e2",
    linewidth=0.8,
    alpha=0.0,
    zorder=10,
)
ax_system.add_patch(contact_patch)
ax_system.add_patch(contact_core)
ax_system.add_patch(gap_patch)

highlight1 = Circle(
    (LEFT_REST_X - 0.22, 0.28),
    0.18,
    facecolor="#ffffff",
    edgecolor="none",
    alpha=0.18,
    zorder=7,
)
highlight2 = Circle(
    (RIGHT_REST_X - 0.22, 0.28),
    0.18,
    facecolor="#ffffff",
    edgecolor="none",
    alpha=0.16,
    zorder=7,
)
ax_system.add_patch(highlight1)
ax_system.add_patch(highlight2)

label_m1 = ax_system.text(
    LEFT_REST_X,
    0.95,
    "Mass 1",
    ha="center",
    va="center",
    fontsize=13,
    fontweight="bold",
    color="#d8f4ff",
)
label_m2 = ax_system.text(
    RIGHT_REST_X,
    0.95,
    "Mass 2",
    ha="center",
    va="center",
    fontsize=13,
    fontweight="bold",
    color="#ffe9ba",
)
compression_text = ax_system.text(
    0.0,
    -1.12,
    "direct contact",
    ha="center",
    va="center",
    fontsize=11,
    color="#8192a8",
)


# FFT panel
freq = np.linspace(0.0, 42.0, 520)
fft_line, = ax_fft.plot([], [], color="#b8f06a", lw=2.7)
fft_fill = ax_fft.fill_between(freq, np.zeros_like(freq), np.zeros_like(freq), color="#8ee55d", alpha=0.16)
ax_fft.set_xlim(0.0, 42.0)
ax_fft.set_ylim(0.0, 0.92)
ax_fft.set_title("FFT amplitude", loc="left", pad=12, fontsize=15, fontweight="bold")
ax_fft.set_xlabel("frequency")
ax_fft.set_ylabel("amplitude")


def shade_sphere(circle: Ellipse, center_x: float) -> list[Circle]:
    """Layer translucent circles for dimensional sphere shading."""
    layers: list[Circle] = []
    specs = [(0.56, "#ffffff", 0.065, 6), (0.40, "#ffffff", 0.055, 7), (0.22, "#ffffff", 0.080, 8)]
    offsets = [(0.0, 0.0), (-0.14, 0.15), (-0.23, 0.25), (-0.31, 0.34)]
    for (rad, face, alpha, z), (dx, dy) in zip(specs, offsets[1:]):
        layer = Circle((center_x + dx, dy), rad, facecolor=face, edgecolor="none", alpha=alpha, zorder=z)
        ax_system.add_patch(layer)
        layers.append(layer)
    circle.set_zorder(4)
    return layers


shade_layers_1 = shade_sphere(mass1, LEFT_REST_X)
shade_layers_2 = shade_sphere(mass2, RIGHT_REST_X)


def update_fft_fill(y: np.ndarray) -> None:
    """Refresh the filled area below the FFT curve."""
    global fft_fill
    fft_fill.remove()
    fft_fill = ax_fft.fill_between(freq, 0.0, y, color="#8ee55d", alpha=0.16)


def artists() -> list:
    """All animated artists for blitting."""
    return [
        line_m1,
        line_m2,
        time_cursor,
        shadow1,
        shadow2,
        mass1,
        mass2,
        contact_patch,
        contact_core,
        gap_patch,
        highlight1,
        highlight2,
        label_m1,
        label_m2,
        compression_text,
        fft_line,
        fft_fill,
        *shade_layers_1,
        *shade_layers_2,
    ]


def update(frame: int) -> list:
    """Animation callback for synchronized motion, time response, and FFT."""
    t = frame / FPS

    # Rolling time response, with all frequencies chosen to tile the loop.
    t_samples = t + t_window
    y1 = displacement_mass_1(t_samples)
    y2 = displacement_mass_2(t_samples)
    line_m1.set_data(t_window, y1)
    line_m2.set_data(t_window, y2)

    # Contact geometry uses a magnified relative displacement for legibility.
    x1 = LEFT_REST_X + displacement_mass_1(t)
    x2 = RIGHT_REST_X + displacement_mass_2(t)
    comp = float(contact_compression(t))
    gap = float(contact_gap(t))
    apparent_x1 = x1 + comp * 0.34 - gap * 0.18
    apparent_x2 = x2 - comp * 0.34 + gap * 0.18
    center_contact = 0.5 * (apparent_x1 + apparent_x2)

    flatten = min(0.075, comp * 0.58)
    mass1.width = 2.0 * RADIUS - flatten
    mass2.width = 2.0 * RADIUS - flatten
    mass1.height = 2.0 * RADIUS + 0.26 * flatten
    mass2.height = 2.0 * RADIUS + 0.26 * flatten
    mass1.center = (apparent_x1, 0.0)
    mass2.center = (apparent_x2, 0.0)

    shadow1.center = (apparent_x1, -0.78)
    shadow2.center = (apparent_x2, -0.78)
    shadow1.width = 1.07 + 0.12 * abs(y1[-1]) / 0.16
    shadow2.width = 1.07 + 0.12 * abs(y2[-1]) / 0.16

    for layer, dx, dy in zip(shade_layers_1, [-0.14, -0.23, -0.31], [0.15, 0.25, 0.34]):
        layer.center = (apparent_x1 + dx, dy)
    for layer, dx, dy in zip(shade_layers_2, [-0.14, -0.23, -0.31], [0.15, 0.25, 0.34]):
        layer.center = (apparent_x2 + dx, dy)

    highlight1.center = (apparent_x1 - 0.22, 0.28)
    highlight2.center = (apparent_x2 - 0.22, 0.28)
    label_m1.set_position((apparent_x1, 0.95))
    label_m2.set_position((apparent_x2, 0.95))

    contact_alpha = 0.14 + min(0.46, 3.8 * comp)
    contact_patch.center = (center_contact, 0.0)
    contact_patch.width = 0.05 + 0.62 * comp
    contact_patch.height = 0.74 + 1.8 * comp
    contact_patch.set_alpha(contact_alpha)
    contact_core.center = (center_contact, 0.0)
    contact_core.width = 0.014 + 0.24 * comp
    contact_core.height = 0.52 + 1.55 * comp
    contact_core.set_alpha(0.18 + min(0.46, 4.2 * comp))

    gap_patch.set_x(center_contact - max(0.008, 0.22 * gap) / 2.0)
    gap_patch.set_y(-0.48)
    gap_patch.set_width(max(0.008, 0.22 * gap))
    gap_patch.set_height(0.96)
    gap_patch.set_alpha(min(0.36, 4.8 * gap))

    compression_text.set_text("compression" if comp > gap else "unloading")
    compression_text.set_color("#aeeeff" if comp > gap else "#7d8da2")

    fft_y = fft_profile(freq, t)
    fft_line.set_data(freq, fft_y)
    update_fft_fill(fft_y)

    return artists()


def save_preview() -> None:
    """Save a single polished still from the animation."""
    update(int(0.38 * N_FRAMES))
    fig.savefig(PNG_PATH, dpi=DPI)


def save_html_preview() -> None:
    """Write a tiny local browser preview for quick website-section testing."""
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Hertzian Two-Mass Animation Preview</title>
  <style>
    html, body {{
      margin: 0;
      min-height: 100%;
      background: #091019;
      display: grid;
      place-items: center;
    }}
    .module {{
      width: min(96vw, 1200px);
      background: #091019;
    }}
    video {{
      width: 100%;
      height: auto;
      display: block;
      border-radius: 8px;
      box-shadow: 0 22px 70px rgba(0, 0, 0, 0.35);
    }}
  </style>
</head>
<body>
  <main class="module">
    <video src="{MP4_PATH.name}" autoplay muted loop playsinline controls></video>
  </main>
</body>
</html>
"""
    HTML_PATH.write_text(html, encoding="utf-8")


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

    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is None:
        try:
            import imageio_ffmpeg

            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            plt.rcParams["animation.ffmpeg_path"] = ffmpeg_path
            print(f"Using ffmpeg from imageio-ffmpeg: {ffmpeg_path}")
        except ImportError as exc:
            raise SystemExit(
                "ffmpeg was not found, so MP4 export cannot run.\n"
                "Install ffmpeg and re-run this script. On Windows:\n"
                "    winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements\n"
                "Or install the Python helper package:\n"
                "    python -m pip install imageio-ffmpeg\n"
            ) from exc

    print(f"Saving MP4 to {MP4_PATH} ...")
    mp4_writer = animation.FFMpegWriter(
        fps=FPS,
        codec="libx264",
        bitrate=9000,
        extra_args=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
    )
    anim.save(MP4_PATH, writer=mp4_writer, dpi=DPI)

    print(f"Saving GIF to {GIF_PATH} ...")
    gif_writer = animation.PillowWriter(fps=FPS)
    anim.save(GIF_PATH, writer=gif_writer, dpi=DPI)

    save_html_preview()
    print("Created:")
    print(f"  {MP4_PATH}")
    print(f"  {GIF_PATH}")
    print(f"  {PNG_PATH}")
    print(f"  {HTML_PATH}")


if __name__ == "__main__":
    main()
