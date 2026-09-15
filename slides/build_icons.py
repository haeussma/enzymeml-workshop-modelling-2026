"""Line icons for the deck, drawn with matplotlib: black strokes on a transparent background.
Run: uv run python slides/build_icons.py  → slides/figures/icon_*.png"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch, Polygon

OUT = Path(__file__).resolve().parent / "figures"
LW, INK = 5, "#0A0A0A"


def canvas():
    fig, ax = plt.subplots(figsize=(3, 3), dpi=200)
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.set_aspect("equal"); ax.axis("off")
    return fig, ax


def save(fig, name):
    fig.savefig(OUT / f"icon_{name}.png", transparent=True, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


def card():
    fig, ax = canvas()
    ax.add_patch(FancyBboxPatch((2, 1), 6, 8, boxstyle="round,pad=0,rounding_size=0.5", fill=False, lw=LW, ec=INK))
    for y, x1 in ((7, 6.5), (5.5, 7), (4, 6), (2.5, 5)):
        ax.plot([3.3, x1], [y, y], lw=LW, color=INK, solid_capstyle="round")
    save(fig, "card")


def peak():
    fig, ax = canvas()
    x = np.linspace(0.5, 9.5, 300)
    y = 1.5 + 4.5 * np.exp(-((x - 4.2) / 0.7) ** 2) + 1.5 * np.exp(-((x - 7.2) / 0.5) ** 2)
    ax.plot(x, y, lw=LW, color=INK, solid_capstyle="round")
    ax.text(6.9, 7.3, "?", fontsize=52, fontweight="bold", color=INK, ha="center", va="center", family="Arial")
    save(fig, "peak")


def person_check():
    fig, ax = canvas()
    ax.add_patch(Circle((3.5, 7), 1.6, fill=False, lw=LW, ec=INK))
    ax.add_patch(FancyBboxPatch((0.8, 1), 5.4, 3.6, boxstyle="round,pad=0,rounding_size=1.8", fill=False, lw=LW, ec=INK))
    ax.plot([6.6, 7.6, 9.6], [4.0, 2.6, 6.6], lw=LW + 1, color=INK, solid_capstyle="round", solid_joinstyle="round")
    save(fig, "person_check")


def document_arrows():
    """An EnzymeML document: the logo in the upper part of the page, text lines below, arrows in and out."""
    fig, ax = canvas()
    ax.add_patch(FancyBboxPatch((3.2, 1.5), 3.6, 7, boxstyle="round,pad=0,rounding_size=0.4", fill=False, lw=LW, ec=INK))
    logo = plt.imread(OUT.parent / "assets/logos/enzymeml-logo.png")
    w = 2.2; h = w * logo.shape[0] / logo.shape[1]
    ax.imshow(logo, extent=(5 - w / 2, 5 + w / 2, 7.6 - h, 7.6), zorder=3)
    for y in (4.4, 3.2):
        ax.plot([4.2, 5.8], [y, y], lw=LW - 1, color=INK, solid_capstyle="round")
    for x0, x1 in ((0.4, 2.6), (7.4, 9.6)):
        ax.annotate("", xy=(x1, 5), xytext=(x0, 5), arrowprops=dict(arrowstyle="-|>", lw=LW, color=INK, mutation_scale=28))
    save(fig, "document_arrows")


if __name__ == "__main__":
    for make in (card, peak, person_check, document_arrows):
        make()
    print("icons written to", OUT)
