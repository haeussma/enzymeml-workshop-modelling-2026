"""Public Anthropic/OpenAI flagships, last workshop to today: Artificial Analysis Intelligence Index.

Values: Artificial Analysis Intelligence Index v4.3 (0-100, composite of many benchmarks), each
model at its highest public effort setting, read from artificialanalysis.ai on 2026-09-13.
Only generally available flagship models; previews, coding-only and small variants excluded.
Earlier METR time-horizon version of this figure: metr/.

Run with: uv run --with matplotlib --with pandas python plot_llm_timeline.py
"""
import matplotlib.dates as mdates
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

plt.rcParams.update({"font.family": "sans-serif", "font.size": 7, "axes.linewidth": 0.6,
                     "xtick.major.width": 0.6, "ytick.major.width": 0.6,
                     "xtick.major.size": 3, "ytick.major.size": 3})

COLORS = {"Anthropic": "#CC6677", "OpenAI": "#4477AA"}
LAST_WORKSHOP = pd.Timestamp("2025-09-30")  # 6th EnzymeML Workshop, 29 Sep – 2 Oct 2025
YMIN, YMAX = 15, 60
# (dx, dy) label offset in points
LABEL_OFFSET = {
    "Opus 4.1": (16, -6),
    "GPT-5": (0, 5),
    "GPT-5.1": (0, -6),
    "Opus 4.5": (-14, 4),
    "GPT-5.2": (14, -5),
    "Opus 4.6": (4, -6),
    "GPT-5.4": (-14, 4),
    "Opus 4.7": (-4, 5),
    "GPT-5.5": (6, -6),
    "Opus 4.8": (16, -3),
    "Fable 5": (-14, 4),
    "GPT-5.6 Sol": (20, -5),
    "Opus 5": (-4, 5),
    "Fable 5.1": (-10, 5),
    "GPT-6 Astra": (10, -6),
}

df = pd.read_csv("data.csv", parse_dates=["release_date"]).sort_values("release_date")
df["short"] = df.model.str.replace("Claude ", "")

fig, ax = plt.subplots(figsize=(4.6, 2.8))
ax.axvline(LAST_WORKSHOP, color="0.6", ls="--", lw=0.6, zorder=0)
ax.text(LAST_WORKSHOP, YMAX, " last workshop", fontsize=6, color="0.45", ha="left", va="top")

for company, g in df.groupby("company"):
    c = COLORS[company]
    ax.plot(g.release_date, g.value, "-", color=c, lw=0.9)
    ax.scatter(g.release_date, g.value, facecolors="white", edgecolors=c, linewidths=1.1,
               s=18, zorder=3)
    for _, r in g.iterrows():
        dx, dy = LABEL_OFFSET.get(r.short, (0, 5))
        ax.annotate(r.short, (r.release_date, r.value), textcoords="offset points",
                    xytext=(dx, dy), fontsize=6, color=c, ha="center",
                    va="bottom" if dy > 0 else "top",
                    path_effects=[pe.withStroke(linewidth=2, foreground="white")], zorder=4)

ax.set_ylim(YMIN, YMAX)
ax.set_yticks(range(20, YMAX + 1, 10))
ax.set_ylabel("Intelligence Index")
ax.set_xlim(pd.Timestamp("2025-07-15"), pd.Timestamp("2026-10-01"))
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[8, 11, 2, 5]))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
ax.spines[["top", "right"]].set_visible(False)

marker = dict(marker="o", markersize=4, markerfacecolor="white", markeredgewidth=1.1)
handles = [Line2D([], [], color=COLORS[k], lw=0.9, **marker, label=k) for k in COLORS]
ax.legend(handles=handles, loc="lower right", fontsize=6, frameon=False, handlelength=2.2)

fig.tight_layout()
fig.savefig("llm_timeline.png", dpi=300)
fig.savefig("llm_timeline.pdf")
print("wrote llm_timeline.png and llm_timeline.pdf")
