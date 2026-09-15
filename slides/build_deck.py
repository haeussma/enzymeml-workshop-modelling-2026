"""Deck for the NeuS hands-on session, 7th EnzymeML Workshop 2026 (Wednesday 16 September, 9:00–12:00).

Run (from the repository root), after build_template.py:
    uv run --with python-pptx --with pillow --with lxml python slides/build_deck.py
Reads slides/template.pptx, slides/figures/* and slides/llm_timeline/llm_timeline.png; writes slides/workshop.pptx
and prints a per-slide check (layout, pictures, title; asserts no placeholder prompt is left).
Speaker notes carry the timing. Parameter names (k_cat, Km_ManNAc, Km_PEP, Km) are typeset with sub/superscripts.
"""
import re
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE, MSO_SHAPE_TYPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls, qn
from pptx.util import Pt

from build_template import CITATION, CW, DIM, E, INK, KICKER, SUBTITLE, TABLE_STYLE, X

HERE = Path(__file__).resolve().parent
FIGS = HERE / "figures"
LLM = HERE / "llm_timeline/llm_timeline.png"
OUT = HERE / "workshop.pptx"
TOP, BOTTOM = 1.8, 6.3                                   # content band under a title without subtitle
PARAM = re.compile(r"Km_(ManNAc|PEP)|Km\b|k_cat")
PROMPTS = ("Kicker", "Subtitle", "Citation", "Click to add")


# ---- text -----------------------------------------------------------------------------------
def runs(p, s, bold=None, size=None, color=None):
    """Append `s` to paragraph p; Km_PEP, Km and k_cat become K_M^PEP, K_M and k_cat (italic, sub/superscript)."""
    def run(t, italic=None, baseline=None):
        if not t:
            return
        r = p.add_run()
        r.text, r.font.bold, r.font.italic = t, bold, italic
        if size:
            r.font.size = Pt(size)
        if color:
            r.font.color.rgb = RGBColor.from_string(color)
        if baseline:
            r.font._rPr.set("baseline", baseline)
    i = 0
    for m in PARAM.finditer(s):
        run(s[i:m.start()])
        if m.group(0) == "k_cat":
            run("k", True); run("cat", None, "-25000")
        else:
            run("K", True); run("M", True, "-25000"); run(m.group(1), None, "30000")
        i = m.end()
    run(s[i:])


def text(ph, items, size=None):
    """Bullets into a placeholder; (lead, rest) gets a bold lead; (heading, None) is a bold line without bullet."""
    tf = ph.text_frame
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        lead, rest = item if isinstance(item, tuple) else ("", item)
        if rest is None:
            pPr = p._p.get_or_add_pPr()
            pPr.set("marL", "0"), pPr.set("indent", "0")
            pPr.append(parse_xml(f'<a:buNone {nsdecls("a")}/>'))
            rest = ""
        for s, bold in ((lead, True), (rest, None)):
            runs(p, s, bold, size)


def drop(ph):
    ph._element.getparent().remove(ph._element)


def label(s, x, y, w, h, t, size=12, color=DIM, bold=None):
    tf = s.shapes.add_textbox(E(x), E(y), E(w), E(h)).text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    runs(p, t, bold, size, color)


def place(shape, x, y, w, h):
    shape.left, shape.top, shape.width, shape.height = E(x), E(y), E(w), E(h)


# ---- figures and tables ---------------------------------------------------------------------
def picture(s, path, x, y, w, h, center=True):
    """Picture fitted into the box (x, y, w, h) inches, top-aligned; returns its width and height."""
    iw, ih = Image.open(path).size
    k = min(w / iw, h / ih)
    pw, ph = iw * k, ih * k
    s.shapes.add_picture(str(path), E(x + (w - pw) / 2 if center else x), E(y), E(pw), E(ph))
    return pw, ph


def figure_slide(s, path, bullets, top=TOP):
    """Figure with its bullets below or, when that leaves the figure more room, beside it."""
    drop(s.placeholders[1])
    cap = s.placeholders[2]
    iw, ih = Image.open(path).size
    lines = sum(-(-len("".join(b)) // 115) for b in bullets)      # ~115 characters per 14 pt line
    cap_h = 0.24 * lines + 0.06 * len(bullets)
    k_below = min(CW / iw, (BOTTOM - top - cap_h - 0.15) / ih)
    k_beside = min(7.4 / iw, (BOTTOM - top) / ih)
    if k_below >= k_beside:
        w, h = picture(s, path, X, top, CW, ih * k_below)
        place(cap, X, top + h + 0.15, CW, cap_h)
        text(cap, bullets)
    else:
        w, h = picture(s, path, X, top, 7.4, BOTTOM - top, center=False)
        place(cap, X + w + 0.35, top + 0.1, CW - w - 0.35, BOTTOM - top - 0.1)
        text(cap, bullets, size=16)


def table(s, rows, x, y, widths, size=14, row_h=0.42):
    t = s.shapes.add_table(len(rows), len(rows[0]), E(x), E(y), E(sum(widths)), E(row_h * len(rows))).table
    t._tbl.tblPr.find(qn("a:tableStyleId")).text = TABLE_STYLE     # python-pptx writes its own default id
    t.horz_banding = False
    for j, w in enumerate(widths):
        t.columns[j].width = E(w)
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            runs(t.cell(i, j).text_frame.paragraphs[0], v, bold=i == 0 or j == 0, size=size)


# ---- diagram shapes -------------------------------------------------------------------------
def box(s, x, y, w, h, title, sub):
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, E(x), E(y), E(w), E(h))
    sh.adjustments[0] = 0.12
    sh.fill.background()
    sh.line.color.rgb, sh.line.width = RGBColor.from_string(INK), Pt(1)
    sh.shadow.inherit = False
    tf = sh.text_frame
    tf.word_wrap, tf.vertical_anchor = True, MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = E(0.08)
    for t, size, color, bold in ((title, 14, INK, True), (sub, 11, DIM, None)):
        if not t:
            continue
        p = tf.paragraphs[0] if t is title else tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        runs(p, t, bold, size, color)                    # the shape style would draw the text white


def line(s, x1, y1, x2, y2, head=False):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, E(x1), E(y1), E(x2), E(y2))
    c.line.color.rgb, c.line.width = RGBColor.from_string(INK), Pt(1.25)
    if head:
        c.line._get_or_add_ln().append(parse_xml(f'<a:tailEnd {nsdecls("a")} type="triangle" w="med" len="med"/>'))


def bracket(s, x1, x2, y, t):
    """A rule with end ticks under a group of boxes, labelled below."""
    line(s, x1, y, x2, y)
    for x in (x1, x2):
        line(s, x, y - 0.12, x, y)
    label(s, x1, y + 0.08, x2 - x1, 0.3, t, size=12, color=INK)


def workflow(s):
    bw, gap, y, h = 1.85, 0.57, 2.7, 1.25
    xs = [X + i * (bw + gap) for i in range(5)]
    steps = [("Raw HPLC chromatograms", "one peak table per injection"),
             ("Chromhandler", "peaks, calibration"),
             ("EnzymeML document", "Neu5Ac time courses"),
             ("Catalax", "ODE model, Bayesian inference"),
             ("k_cat, Km_ManNAc, Km_PEP", "posterior distributions")]
    for x, (title, sub) in zip(xs, steps):
        box(s, x, y, bw, h, title, sub)
    for x in xs[:-1]:
        line(s, x + bw + 0.06, y + h / 2, x + bw + gap - 0.06, y + h / 2, head=True)
    bracket(s, xs[0], xs[2] + bw, y + h + 0.45, "Task 1 · chromatograms to EnzymeML")
    bracket(s, xs[2], xs[4] + bw, y + h + 1.2, "Task 2 · infer the kinetic parameters")


def concept(s):
    """The language model in the centre, tools left, skills right, the scientist above; the caption is the slide's."""
    xm, ym, wm, hm = 5.0, 3.55, 3.0, 1.1                 # model box
    box(s, xm, ym, wm, hm, "Language model", "ChatGPT, Claude, Gemini, …")
    box(s, 4.467, 1.85, 4.4, 0.8, "You", "the task, the decisions, the checks")
    line(s, 6.167, 2.71, 6.167, ym - 0.06, head=True); label(s, 5.35, 2.95, 0.75, 0.25, "task")
    line(s, 7.167, ym - 0.06, 7.167, 2.71, head=True); label(s, 7.25, 2.95, 0.9, 0.25, "results")
    # tools: three boxes on a spine, one arrow each way
    label(s, X, 2.55, 2.3, 0.3, "Tools")
    ys = [2.9, 3.75, 4.6]
    for y, t in zip(ys, ("read files", "run Python", "make plots")):
        box(s, X, y, 2.3, 0.7, t, None)
        line(s, X + 2.3, y + 0.35, 3.6, y + 0.35)
    line(s, 3.6, ys[0] + 0.35, 3.6, ys[-1] + 0.35)
    line(s, xm - 0.06, 3.9, 3.66, 3.9, head=True); label(s, 3.7, 3.6, 1.2, 0.25, "actions")
    line(s, 3.66, 4.3, xm - 0.06, 4.3, head=True); label(s, 3.7, 4.36, 1.2, 0.25, "results")
    # skills: two boxes on a spine, one arrow in
    xs, ws = 9.633, 2.8
    label(s, xs, 2.65, ws, 0.3, "Skills")
    ys = [3.0, 4.2]
    for y, (t, sub) in zip(ys, (("chromhandler.md", "peak tables → EnzymeML"),
                                ("catalax.md", "EnzymeML → k_cat, Km by Bayesian inference"))):
        box(s, xs, y, ws, 1.0, t, sub)
        line(s, xs, y + 0.5, 9.2, y + 0.5)
    line(s, 9.2, ys[0] + 0.5, 9.2, ys[-1] + 0.5)
    line(s, 9.14, 4.1, xm + wm + 0.06, 4.1, head=True); label(s, xm + wm + 0.05, 3.8, 1.1, 0.25, "instructions")


def tool_slide(s, inputs, steps, outputs):
    """One tool: inputs on the left, the steps in order in the middle (decisions marked in the sub line),
    outputs on the right; spines with arrows connect the columns. Under a title with subtitle."""
    cols = {"Input": (X, 3.0), "Steps": (X + 3.57, 4.4), "Output": (X + 8.53, 3.0)}
    for name, (x, w) in cols.items():
        label(s, x, 2.25, w, 0.3, name)
    top = 2.6
    # inputs, joined by a spine that feeds the first step
    x, w = cols["Input"]
    h, gap = 0.75, 0.25
    spine = x + w + 0.25
    for i, (t, sub) in enumerate(inputs):
        y = top + i * (h + gap)
        box(s, x, y, w, h, t, sub)
        line(s, x + w, y + h / 2, spine, y + h / 2)
    xs, ws = cols["Steps"]
    hs, gs = 0.58, 0.16
    ys = [top + i * (hs + gs) for i in range(len(steps))]
    line(s, spine, ys[0] + hs / 2, spine, top + (len(inputs) - 1) * (h + gap) + h / 2)
    line(s, spine, ys[0] + hs / 2, xs - 0.06, ys[0] + hs / 2, head=True)
    # steps, one arrow to the next
    for y, (t, sub) in zip(ys, steps):
        box(s, xs, y, ws, hs, t, sub)
    for y in ys[:-1]:
        line(s, xs + ws / 2, y + hs + 0.02, xs + ws / 2, y + gs + hs - 0.02, head=True)
    # outputs, fed by the last step through a spine
    xo, wo = cols["Output"]
    spine = xo - 0.25
    y_last = ys[-1] + hs / 2
    line(s, xs + ws, y_last, spine, y_last)
    line(s, spine, top + h / 2, spine, y_last)
    for i, (t, sub) in enumerate(outputs):
        y = top + i * (h + gap)
        box(s, xo, y, wo, h, t, sub)
        line(s, spine, y + h / 2, xo - 0.06, y + h / 2, head=True)

def hurdles(s):
    """Last year's path to an analysis: four hurdles in a row before the analysis itself."""
    bw, gap, y, h = 1.85, 0.57, 2.6, 1.15
    xs = [X + i * (bw + gap) for i in range(5)]
    steps = [("Install", "Python, packages, a working environment"),
             ("Read the docs", "how the tools are used"),
             ("Write the code", "Python, by hand, for your data"),
             ("Debug, repeat", "errors, versions, time"),
             ("Your analysis", "structured data, a kinetic model")]
    for x, (title, sub) in zip(xs, steps):
        box(s, x, y, bw, h, title, sub)
    for x in xs[:-1]:
        line(s, x + bw + 0.06, y + h / 2, x + bw + gap - 0.06, y + h / 2, head=True)

def pillars(s, items):
    """Columns of icon, bold headline and one grey line; no boxes."""
    n, gap = len(items), 0.5
    w = (CW - gap * (n - 1)) / n
    for i, (icon, head, sub) in enumerate(items):
        x = X + i * (w + gap)
        picture(s, FIGS / icon, x + (w - 1.5) / 2, 2.15, 1.5, 1.5)
        label(s, x, 3.95, w, 0.45, head, size=16, color=INK, bold=True)
        label(s, x, 4.55, w, 1.4, sub, size=13)


# ---- the deck -------------------------------------------------------------------------------
def main():
    prs = Presentation(HERE / "template.pptx")
    lay = {l.name: l for l in prs.slide_layouts}

    def slide(layout, kicker, title, subtitle=None, cite=None, notes=""):
        s = prs.slides.add_slide(lay[layout])
        for idx, t in ((0, title), (KICKER, kicker), (SUBTITLE, subtitle), (CITATION, cite)):
            if t:
                tf = s.placeholders[idx].text_frame
                tf.text = ""
                runs(tf.paragraphs[0], t)
        s.notes_slide.notes_text_frame.text = notes
        return s

    def two_lines(s, first, second):                    # cover and end: name, then a grey second line
        tf = s.placeholders[1].text_frame
        tf.text = first
        p = tf.add_paragraph()
        p.text, p.level = second, 1

    s = slide("Cover", "7th EnzymeML Workshop · Rüdesheim · Hands-on session 2 · 16 September 2026",
              "From measurement to kinetic modelling",
              notes="9:00 · 1 min. Welcome to hands-on session 2 (9:00–12:00). The session is shared with Sascha Gabriel "
                    "(Stuttgart); this deck is my part. Plan: 15 min of introduction, a live demo, two hands-on tasks with a "
                    "break in between, comparison of results at 11:25, wrap-up at 11:50.")
    two_lines(s, "Max Häußler", "University of Freiburg")

    s = slide("Figure", "Looking back", "Last year the code was the hurdle",
              "Previous hands-on sessions: we installed, read the docs and wrote the analysis code ourselves",
              notes="9:01 · 2 min. Recap of the earlier sessions: we, as humans, wrote the code. Before the first "
                    "plot everyone had to set up a computing environment, read the documentation of the tools for "
                    "extracting and modelling data, and write Python. Installations failed, the code was unfamiliar, "
                    "and for people who do not work with code every day this was a burden. That kept many from "
                    "structuring their data at all, and so from using contemporary data-science methods on it. "
                    "Bridge: since then a lot has happened with language models and AI agents; the models got better, "
                    "and the harnesses that let a model execute tools got much better. Next slide shows the models.")
    drop(s.placeholders[1])
    hurdles(s)
    place(s.placeholders[2], X, 4.5, CW, 1.3)
    text(s.placeholders[2], ["Failing installs and unfamiliar code: a hurdle for everyone who does not code daily",
                             "So the data stayed unstructured, and the contemporary methods out of reach",
                             ("Since then: ", "the models got better, and so did the harnesses that let them run tools")])

    s = slide("Figure", "Language models since the last workshop", "From 23 to 53 in one year",
              "The two labs traded the lead several times; the biggest single step was Fable 5 in June 2026",
              cite="Artificial Analysis Intelligence Index v4.3, artificialanalysis.ai; release dates from the vendors",
              notes="9:03 · 2 min. Dashed line: the 6th workshop, 29 Sep – 2 Oct 2025. Since then the flagship models went "
                    "from about 23 to 53 on the index. The index is an independent benchmark, every model tested the same way. "
                    "The point is that the tool changed a lot in one year, not which lab leads. Keep it short.")
    figure_slide(s, LLM, ["The Intelligence Index is an independent score from 0 to 100 that combines many tests of "
                          "knowledge, reasoning, coding and agentic work, with every model tested the same way.",
                          "Shown are the flagship models of Anthropic and OpenAI that anyone can use, each at its strongest "
                          "public setting."], top=2.2)

    s = slide("Content", "Motivation", "The assistant types, you decide",
              notes="9:05 · 2 min. What this enables for us: from a one-page description a model writes correct code "
                    "against Chromhandler and Catalax. What it does not do: know where the peak is, which model is right, "
                    "whether a result is wrong. So today the assistant executes, you decide and check. EnzymeML is the "
                    "document that travels between the steps and the tools.")
    drop(s.placeholders[1])
    pillars(s, [("icon_card.png", "One page is enough",
                 "From a one-page card, today's models write working code for our tools"),
                ("icon_peak.png", "Blind to your data",
                 "Where the peak is, which model is right, when a result is wrong"),
                ("icon_person_check.png", "You decide and check",
                 "The decisions and the checks stay with the scientist; the assistant executes"),
                ("icon_document_arrows.png", "EnzymeML in between",
                 "One document carries the data between the steps and the tools")])

    s = slide("Figure", "Concept", "Tools act, skills instruct, you decide",
              notes="9:07 · 2 min. A language model on its own only writes text. Tools are functions it can call and "
                    "whose output it sees: read a file, run Python, make a plot; that is how it reads the peak tables "
                    "and runs Chromhandler and Catalax. Skills are instructions in plain text: our two tool cards, "
                    "chromhandler.md and catalax.md, tell it how each library turns data into insight, peak tables into "
                    "an EnzymeML document, the document into kcat and Km by Bayesian inference. You give the task, take "
                    "the decisions and check the results; the model executes.")
    drop(s.placeholders[1])
    concept(s)
    place(s.placeholders[2], X, 5.65, CW, 0.4)
    text(s.placeholders[2], ["Tools let the model read the data and run code; skills tell it how our libraries turn "
                             "data into insight"])

    s = slide("Title only", "Workflow", "Two tasks, one document in between",
              "Task 1 ends with the EnzymeML document; task 2 starts from it",
              notes="9:09 · 1 min. Walk through the five boxes left to right. Task 1 covers the first three, task 2 the "
                    "last three; the EnzymeML document is the handover, which is why anyone stuck in task 1 can start "
                    "task 2 from the checkpoint. Timing: task 1 9:15–10:15, task 2 10:30–11:25.")
    workflow(s)

    s = slide("Title only", "Tool 1 · Chromhandler", "Chromhandler: from peak tables to concentrations",
              "Reads the instrument's exports, assigns and calibrates one peak per compound, writes EnzymeML",
              notes="9:10 · 1 min. Left: what goes in, the peak tables the instrument software exported (one per "
                    "injection, the reaction time in the file name), the standards with known concentrations, and the "
                    "initial concentrations. Middle: the steps in order; two of them are the scientist's decisions, the "
                    "retention window per session and accepting the calibration. Right: the EnzymeML document and the "
                    "checks the task card asks for.")
    tool_slide(s,
               inputs=[("Peak tables", None), ("Calibration standards", None), ("Initial concentrations", None)],
               steps=[("Read the exports", None), ("Set the retention window", None), ("Assign the peak", None),
                      ("Calibrate", None), ("Export", None)],
               outputs=[("EnzymeML document", None), ("Checks", None)])

    s = slide("Title only", "Tool 2 · Catalax", "Catalax: from time courses to kinetic parameters",
              "Builds the ODE model from a rate law and samples the posterior of its parameters",
              notes="9:11 · 1 min. Left: the EnzymeML document, the rate law, and the assumptions, priors and noise. "
                    "Middle: load, define the model, set the priors, sample with Hamiltonian Monte Carlo, then check "
                    "and plot. The model, the priors and the noise are the scientist's decisions; the checks say whether "
                    "the posterior can be trusted. Right: posterior distributions, not point estimates, and the plots.")
    tool_slide(s,
               inputs=[("EnzymeML document", None), ("Rate law", None), ("Priors and noise", None)],
               steps=[("Load the dataset", None), ("Define the model", None), ("Set the priors", None),
                      ("Sample", None), ("Check and plot", None)],
               outputs=[("Posterior", None), ("Plots", None)])

    s = slide("Figure", "The experiment", "ManNAc + PEP → Neu5Ac + Pi, followed by HPLC",
              cite="Data: Çakar et al. (2024) Kinetic characterization of two neuraminic acid synthases and evaluation of their application potential. Appl. Microbiol. Biotechnol. 108, 446 · doi:10.1007/s00253-024-13277-1",
              notes="9:12 · 2 min. Neu5Ac synthase condenses ManNAc and PEP to Neu5Ac and phosphate (metal cofactor, "
                    "water). HPLC-PDA at 215 nm; the instrument software exported one peak table per injection. Only the "
                    "product is quantified; the substrates enter the model as their known initial values. Do not "
                    "explain the design or the numbers: how many reactions there are, what was varied and what the "
                    "data look like is what the participants find out with their assistant in task 1.")
    figure_slide(s, FIGS / "reaction_scheme.png",
                 ["Reactions sampled over time and followed by HPLC-PDA at 215 nm",
                  "What you get is the instrument's peak table per injection, not the raw trace",
                  "Only the product Neu5Ac is quantified; calibration standards with known concentrations",
                  "How many reactions, which conditions, how they were varied: that is in the data"])

    s = slide("Content", "Today", "What we do today",
              notes="9:15 · 1 min. Task 1 with Chromhandler, task 2 with Catalax. Live demo first, then you work in "
                    "pairs; the checks in the task card decide when you are done. Timing: demo 9:15, hands-on 9:30, "
                    "break 10:15–10:30, demo 10:30, hands-on 10:40. At 11:25 we collect everybody's kcat and Km on one "
                    "slide or the whiteboard, wrap-up 11:50.")
    text(s.placeholders[1], [("Task 1: ", "from the peak tables to an EnzymeML document (Chromhandler)"),
                             ("Task 2: ", "from the EnzymeML document to k_cat and Km by Bayesian inference (Catalax)"),
                             "A live demo of each task first, then you work in pairs",
                             "The checks in the task card say when you are done",
                             "At the end we compare everybody's parameters and discuss"])

    s = slide("Two columns", "Toolkit", "One repository, two ways to work",
              "tinyurl.com/enzymeml2026 · start with the README",
              notes="9:16 · 3 min. README first. Two ways. With a language model: any chat model, free or by "
                    "subscription (ChatGPT, Claude, Gemini, …); paste the tool card, then the task card; run the code it "
                    "writes; paste errors back; the checks decide. Without writing code: the Colab link opens a prepared "
                    "notebook with the tools installed and the data loaded; run it cell by cell, change a window, a "
                    "prior, a series; ask the model inside Colab to explain any cell. notebooks/ are the reference "
                    "solutions, open to everyone; checkpoints/ holds the result of task 1. Locally: uv sync.")
    text(s.placeholders[1], [("With a language model", None),
                             ("Any chat model, ", "free or by subscription: ChatGPT, Claude, Gemini, …"),
                             ("Paste ", "the tool card and the task card; run the code, paste errors back"),
                             ("The checks ", "decide when you are done"),
                             ("notebooks/ ", "are the reference solutions, checkpoints/ the result of task 1")])
    text(s.placeholders[2], [("Without writing code", None),
                             ("Open the Colab link: ", "a prepared notebook, tools installed, data loaded"),
                             ("Run it cell by cell; ", "change a window, a prior, a series"),
                             ("Ask the model in Colab ", "to explain any cell")])

    s = slide("Content", "Task 1", "Task 1: from chromatograms to EnzymeML",
              notes="9:15 · Live demo 15 min, then hands-on 9:30–10:15. Demo: paste chromhandler.md, then the task card, "
                    "then 'Let's start with task 1'. Let the assistant read the data and answer the first question; show "
                    "the peak plot. Accept the calibration explicitly ('my decision, not the assistant's'). Deliberate "
                    "mistake: when asked for the reaction window, say 'the same as the standards'; chromhandler warns "
                    "'No peaks found for Neu5Ac', the document has no Neu5Ac values. Say why (the shift on the peak plot), "
                    "correct it, continue. The questions on the slide are what every pair answers; we compare at 11:25.")
    text(s.placeholders[1], [("Goal: ", "an EnzymeML document with the calibrated Neu5Ac time course of every reaction"),
                             ("Your decision: ", "the Neu5Ac retention window, different in standards and reactions"),
                             ("Questions to answer", None),
                             "How many reactions and standards are in the data, and what was varied?",
                             "Where does Neu5Ac elute, in the standards and in the reactions?",
                             "What is the calibration slope, and how well does the line fit?",
                             "Does every reaction have all its time points, and which reactions form product?"])

    s = slide("Content", "Task 2", "Task 2: kinetic parameters by Bayesian inference",
              "v = k_cat · [NeuS] · [ManNAc] · [PEP] / ((Km_ManNAc + [ManNAc]) (Km_PEP + [PEP]))",
              notes="10:30 · Live demo 10 min, then hands-on 10:40–11:25. Paste catalax.md, then the task card. "
                    "enable_x64 first. Only Neu5Ac has data; in Catalax 0.5.5 every state stays observable and the "
                    "unmeasured ones get NaN arrays (observable=False breaks the sampler in this version). The priors and the "
                    "sampler settings are in the card; they are decisions, say so. Show the posterior table, the trace "
                    "and the fit plot. Those who did not finish task 1 start from checkpoints/neus_enzymeml.json.")
    text(s.placeholders[1], [("Goal: ", "posterior distributions of k_cat, Km_ManNAc and Km_PEP, with a fit plot"),
                             ("Model: ", "the enzyme is in the rate law, only Neu5Ac is measured, "
                                        "the metal cofactor is left out (a simplification)"),
                             ("Your decisions: ", "the priors, the assumed measurement noise, the sampler settings"),
                             ("Questions to answer", None),
                             "What are k_cat, Km_ManNAc and Km_PEP, and how uncertain is each?",
                             "Do the two chains agree, and were there divergences?",
                             "Is the posterior clear of the prior bounds, or does a bound decide the answer?",
                             "Does one model describe both series?"])

    s = slide("Figure", "Reference result", "The reference fit, and an open question",
              notes="11:25 · 25 min. First collect everybody's kcat, Km_ManNAc, Km_PEP: how much do they differ and why "
                    "(windows, priors, reactions used)? Then the misfit: one shared kcat over-predicts the ManNAc series "
                    "and under-predicts the PEP series; the series were measured on different days and differ by roughly "
                    "25 % in activity. Ask: a per-day activity factor, a new experiment, both? Which decisions did the "
                    "assistant try to make for you, and which did you take back?")
    drop(s.placeholders[1])
    picture(s, FIGS / "model_fit.png", X, TOP, CW, 2.75)
    table(s, [["Parameter", "Posterior mean ± sd"],                 # notebooks/02_kinetic_model.ipynb
              ["k_cat", "364 ± 6 min⁻¹  (6.1 s⁻¹, 9.4 U/mg)"],
              ["Km_ManNAc", "1.53 ± 0.19 mM"],
              ["Km_PEP", "0.59 ± 0.07 mM"]], X, 4.75, [1.9, 3.9], row_h=0.36)
    place(s.placeholders[2], X + 6.2, 4.75, CW - 6.2, BOTTOM - 4.75)
    text(s.placeholders[2], ["One shared k_cat over-predicts the ManNAc series and under-predicts the PEP series",
                             "The two series were measured on different days and differ by roughly 25 % in activity",
                             "What would you do next?"])

    s = slide("Content", "Wrap-up", "What to take home",
              notes="11:50 · 10 min. Take-home and feedback round. Ask explicitly what did not work: that is what we need "
                    "to improve the cards. The cards are reusable as SKILL.md / AGENTS.md for coding agents.")
    text(s.placeholders[1], ["A one-page card is enough for an assistant to drive our tools",
                             "The decisions and the checks stay with the scientist",
                             "The cards are reusable as SKILL.md or AGENTS.md in coding agents",
                             "What did not work for you today is the most useful feedback for us"])

    s = slide("End", None, "Thank you", notes="11:58 · Close. The repository stays up: tinyurl.com/enzymeml2026, or the "
                                                 "QR code. Questions in the break or by mail.")
    two_lines(s, "tinyurl.com/enzymeml2026", "Max Häußler · University of Freiburg")
    picture(s, FIGS / "qr_repository.png", 11.0, 2.35, 1.5, 1.5)

    for s in prs.slides:                                 # unused kicker/subtitle/citation prompts
        for ph in list(s.placeholders):
            if ph.has_text_frame and not ph.text_frame.text.strip():
                ph._element.getparent().remove(ph._element)
    prs.save(OUT)
    print(f"wrote {OUT} ({len(prs.slides)} slides)")
    check(OUT)


def check(path):
    """Per slide: layout, pictures, title; fails on leftover placeholder prompts or empty placeholders."""
    for i, s in enumerate(Presentation(path).slides, 1):
        texts = [sh.text_frame.text for sh in s.shapes if sh.has_text_frame]
        assert not [t for t in texts if any(p in t for p in PROMPTS)], f"slide {i}: prompt text left"
        assert all(ph.text_frame.text.strip() for ph in s.placeholders if ph.has_text_frame), f"slide {i}: empty placeholder"
        pics = sum(sh.shape_type == MSO_SHAPE_TYPE.PICTURE for sh in s.shapes)
        print(f"{i:2d}  {s.slide_layout.name:12s} {pics} pic  {s.shapes.title.text if s.shapes.title else ''}")


if __name__ == "__main__":
    main()
