# From HPLC chromatograms to enzyme kinetics, with an AI assistant

In this workshop you turn raw HPLC data of a real enzyme into kinetic parameters
(`kcat`, `Km`). An AI assistant writes and runs the code; **you make the scientific decisions and
check the results.** No programming experience is needed.

You will:

1. read raw chromatograms, find the product peak and calibrate it
   (tool: [Chromhandler](https://github.com/FAIRChemistry/Chromhandler)),
2. save the concentration time courses as an EnzymeML document,
3. infer the parameters of a kinetic model from them, as posterior distributions
   (tool: [Catalax](https://github.com/FAIRChemistry/Catalax)).

## The data come from this paper

> Çakar MM, Milčić N, Andreadaki T, Charnock S, Fessner W-D, Findrik Blažević Z (2024).
> **Kinetic characterization of two neuraminic acid synthases and evaluation of their application
> potential.** *Applied Microbiology and Biotechnology* 108, 446.
> <https://doi.org/10.1007/s00253-024-13277-1>

The HPLC data of the *Neisseria meningitidis* Neu5Ac synthase in this repository were measured
for that study. If you use the data, cite the paper.

## The experiment

The enzyme is the N-acetylneuraminic acid synthase of *Neisseria meningitidis* (NeuS, also named
NeuB or SiaC; UniProt [Q57265](https://www.uniprot.org/uniprotkb/Q57265), 349 residues,
38.3 kDa). It condenses two substrates into sialic acid and releases phosphate:

![ManNAc + PEP → Neu5Ac + Pi](slides/figures/reaction_scheme.png)

| Abbreviation | Compound | Role | PubChem CID |
| --- | --- | --- | --- |
| ManNAc | N-acetyl-D-mannosamine | substrate | 11096158 |
| PEP | phosphoenolpyruvate | substrate | 1005 |
| Neu5Ac | N-acetylneuraminic acid (sialic acid) | product | 439197 |
| Pi | inorganic phosphate | by-product | 1061 |

Product formation was followed by HPLC; the instrument software exported one peak table per
injection, and those exports plus the initial concentrations are the data. Details, including
where Neu5Ac elutes: [data/README.md](data/README.md).

## How to do it

Everything the assistant needs is in `briefs/`, as one-page cards: a **tool card** tells it how
to use Chromhandler or Catalax, a **task card** tells it what you want from this dataset. Pick
the route that matches what you have.

### Route A · a coding assistant on your computer

Claude Code, Codex, Cursor or another agent that runs code on your machine.

1. Clone the repository and open it in the agent:

   ```bash
   git clone https://github.com/haeussma/enzymeml-workshop-modelling-2026
   ```

2. Give the agent the two cards of the task (task 1: `briefs/chromhandler.md` and
   `briefs/task_1_chromatograms_to_enzymeml.md`) and write: *Let's start with task 1.*
3. It installs the tools itself (the tool cards say how) and works through the task. Look at
   every plot it shows; the decisions are yours.

### Route B · a chat assistant only

ChatGPT, Claude, Gemini or any chat that cannot run code. The code runs in a Google Colab
notebook instead, and you carry text between the two.

1. Open the starter notebook
   [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/haeussma/enzymeml-workshop-modelling-2026/blob/main/notebooks/00_start_here.ipynb)
   (Google account needed; click *Run anyway* on Colab's warning) and run its first cell. It
   installs the tools and downloads the data, about 30 s.
2. Open the chat in a second tab. Copy the two cards of the task from GitHub
   (open the file, *Copy raw file*) and paste them into the chat, tool card first, then write:
   *Let's start with task 1.* Colab's own Gemini panel (the ✨ icon) can be the chat; it sees the
   notebook and its outputs.
3. For every snippet the assistant gives you: add a code cell in the notebook, paste, run.
   Paste the printed output or the error back into the chat; for plots, upload the image.
4. The assistant asks for decisions, e.g. where the peak is. Those are yours.

### Route C · no assistant that runs code

Team up with someone on route A or B. The decisions and the checks are the interesting part,
and they take two people as well as one.

### In every route

- Run the code you are given; if there is an error, paste it back.
- Look at every plot before you continue.
- The task card lists checks. You are done when they pass and you can answer the questions of
  the task below.

## Task 1: from chromatograms to EnzymeML

Cards: [briefs/chromhandler.md](briefs/chromhandler.md) and
[briefs/task_1_chromatograms_to_enzymeml.md](briefs/task_1_chromatograms_to_enzymeml.md).
Result: an EnzymeML document with the calibrated Neu5Ac time course of every reaction.

What to look for in this dataset:

1. **Plot the data.** All peaks of all injections against their retention time. Where does Neu5Ac
   elute, in the standards and in the reactions?
2. **Check how the kinetic assay was designed.** How many reactions and standards are there, what
   was varied between the reactions, what was kept fixed?
3. **Calibrate.** What are the calibration parameters, and how well does the line fit the
   standards?
4. **Set the retention window for the reactions** (it differs from the standards) and assign the
   product peak in every chromatogram.
5. **Export the EnzymeML document** and check it: does every reaction have all its time points,
   and which reactions form product?

## Task 2: kinetic parameters by Bayesian inference

Cards: [briefs/catalax.md](briefs/catalax.md) and
[briefs/task_2_kinetic_model.md](briefs/task_2_kinetic_model.md). Start from your task 1
document, or from [checkpoints/neus_enzymeml.json](checkpoints/neus_enzymeml.json).
Result: posterior distributions of `kcat`, `Km_ManNAc` and `Km_PEP`, with corner and fit plots.

What to look for:

1. **Plot the time courses** from the EnzymeML document.
2. **Define the model and the priors.** The enzyme is in the rate law; only Neu5Ac is measured.
3. **Infer the kinetic parameters.** `kcat`, `Km_ManNAc` and `Km_PEP`, each with its uncertainty.
4. **Check the sampler.** Do the chains agree? Divergences? Is the posterior clear of the prior
   bounds, or does a bound decide the answer?
5. **What is the correlation between the kinetic parameters?** Which pairs trade off against
   each other, and why?
6. **Does one model describe both series?** Plot data and model together.

## What is in this repository

```
README.md        you are here
briefs/          tool cards and task cards to paste into the assistant
data/            raw HPLC exports, initial concentrations, data description
notebooks/       00_start_here (Colab starter) and the reference solutions of both tasks
checkpoints/     result of task 1, to start task 2 directly
slides/          workshop slides and figures
```

## Tools and versions

| Package | Version | Role |
| --- | --- | --- |
| chromhandler | 0.10.11 | read HPLC data, assign peaks, calibrate, export EnzymeML |
| catalax | 0.5.5 | kinetic models, Bayesian parameter inference (HMC) |
| Python | 3.11–3.13 | |

The assistant installs them; the tool cards carry the commands (a fresh virtual environment,
pinned versions). If you install by hand, do the same. Two things to know about Catalax 0.5.5,
both handled in the tool card: call `catalax.enable_x64()` before anything else, and leave every
model state observable with NaN arrays for the unmeasured ones (`observable=False` silently
breaks the sampler in this version).

## Reference solutions

At the end of the workshop, compare your result with one way of doing it: the notebooks
[01_hplc_to_enzymeml.ipynb](notebooks/01_hplc_to_enzymeml.ipynb) and
[02_kinetic_model.ipynb](notebooks/02_kinetic_model.ipynb). They run in Colab without any
installation:

| | |
| --- | --- |
| Task 1 · chromatograms → EnzymeML | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/haeussma/enzymeml-workshop-modelling-2026/blob/main/notebooks/01_hplc_to_enzymeml.ipynb) |
| Task 2 · kinetic model by Bayesian inference | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/haeussma/enzymeml-workshop-modelling-2026/blob/main/notebooks/02_kinetic_model.ipynb) |

Posterior mean ± sd (3–97 % interval); 2 chains × (500 warmup + 1000 samples), Gaussian
likelihood, log-uniform priors:

| Result | Value |
| --- | --- |
| Neu5Ac calibration | 239 349 area per mM, R² = 0.999 |
| `kcat` | 364 ± 6 min⁻¹ (353–374; 6.1 s⁻¹, 9.4 U/mg) |
| `Km_ManNAc` | 1.53 ± 0.19 mM (1.16–1.89) |
| `Km_PEP` | 0.59 ± 0.07 mM (0.45–0.72) |
| estimated noise `sigma` | 0.09 mM |

One shared `kcat` over-predicts the ManNAc series and under-predicts the PEP series: the two
series, measured on different days, differ in enzyme activity by roughly 25 %. A good question
for the discussion.
