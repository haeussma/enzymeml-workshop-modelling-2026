"""METR 50% time horizon of public Anthropic/OpenAI flagships, last workshop to today.

Time horizon = length of tasks (in human-expert time) a model completes with 50% success.
Values: METR TH1.1 (metr.org/assets/benchmark_results_1_1.yaml) and METR's GPT-5.6 Sol report,
checked 2026-09-13. The y-axis ends at 16 h, above which METR calls its measurements unreliable.
GPT-5.6 Sol (lighter, dotted) is flagged by METR as not robust; later flagships have no value.
CIs are in data.csv and deliberately not drawn.

Run with: uv run --with matplotlib --with pandas python plot_llm_timeline.py
"""
import matplotlib.dates as mdates
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd

plt.rcParams.update({"font.family": "sans-serif", "font.size": 7, "axes.linewidth": 0.6,
                     "xtick.major.width": 0.6, "ytick.major.width": 0.6,
                     "xtick.major.size": 3, "ytick.major.size": 3})

COLORS = {"Anthropic": "#CC6677", "OpenAI": "#4477AA"}
LAST_WORKSHOP = pd.Timestamp("2025-09-15")  # placeholder until the exact date is confirmed
# (dx, dy) label offset in points
LABEL_OFFSET = {
    "Opus 4.1": (20, -3),
    "GPT-5": (0, 6),
    "Opus 4.5": (-18, 4),
    "GPT-5.2": (12, -8),
    "Opus 4.6": (-18, 3),
    "GPT-5.4": (0, -8),
    "GPT-5.6 Sol": (0, 6),
}

df = pd.read_csv("data.csv", parse_dates=["release_date"]).sort_values("release_date")
df["short"] = df.model.str.replace("Claude ", "")

fig, ax = plt.subplots(figsize=(3.5, 2.4))
ax.axvline(LAST_WORKSHOP, color="0.6", ls="--", lw=0.6, zorder=0)
ax.text(LAST_WORKSHOP, 16, " last workshop", fontsize=6, color="0.45", ha="left", va="top")
for company, g in df.groupby("company"):
    c = COLORS[company]
    ok, flagged = g[g.reliable == "yes"], g[g.reliable != "yes"]
    ax.plot(ok.release_date, ok.p50_h, "-", color=c, lw=0.9)
    ax.scatter(ok.release_date, ok.p50_h, facecolors="white", edgecolors=c, linewidths=1.1,
               s=18, zorder=3)
    for _, r in flagged.iterrows():
        ax.plot([ok.release_date.iloc[-1], r.release_date], [ok.p50_h.iloc[-1], r.p50_h], ":",
                color=c, lw=0.9, alpha=0.5)
        ax.scatter(r.release_date, r.p50_h, facecolors="white", edgecolors=c, linewidths=1.1,
                   s=18, alpha=0.5, zorder=3)
    for _, r in g.iterrows():
        dx, dy = LABEL_OFFSET.get(r.short, (0, 6))
        ax.annotate(r.short, (r.release_date, r.p50_h), textcoords="offset points",
                    xytext=(dx, dy), fontsize=6, color=c, ha="center",
                    va="bottom" if dy > 0 else "top", alpha=1 if r.reliable == "yes" else 0.6,
                    path_effects=[pe.withStroke(linewidth=2, foreground="white")], zorder=4)

ax.set_ylim(0, 16)
ax.set_yticks([0, 4, 8, 12, 16])
ax.set_ylabel("Time horizon (h)")
ax.set_xlim(pd.Timestamp("2025-07-15"), pd.Timestamp("2026-09-15"))
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[8, 11, 2, 5]))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
ax.spines[["top", "right"]].set_visible(False)

marker = dict(marker="o", markersize=4, markerfacecolor="white", markeredgewidth=1.1)
handles = [Line2D([], [], color=COLORS["Anthropic"], lw=0.9, **marker, label="Anthropic"),
           Line2D([], [], color=COLORS["OpenAI"], lw=0.9, **marker, label="OpenAI"),
           Line2D([], [], color="0.6", lw=0.9, ls=":", **marker, label="Not robust (METR)")]
ax.legend(handles=handles, loc="lower right", fontsize=6, frameon=False, handlelength=2.2)

fig.tight_layout()
fig.savefig("llm_timeline.png", dpi=300)
fig.savefig("llm_timeline.pdf")
print("wrote llm_timeline.png and llm_timeline.pdf")
