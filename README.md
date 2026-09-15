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

You need an AI assistant and a place where its code runs. Three ways:

1. **A coding assistant on your computer** (Claude Code, Codex, Cursor, …): clone the repository
   and give the assistant the two cards of the task (below). It installs the tools itself; the
   tool cards say how.

   ```bash
   git clone https://github.com/haeussma/enzymeml-workshop-modelling-2026
   ```

2. **A chat assistant only** (ChatGPT, Claude, Gemini, …): open the starter notebook in Google
   Colab
   [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/haeussma/enzymeml-workshop-modelling-2026/blob/main/notebooks/00_start_here.ipynb)
   (Google account needed; click *Run anyway* on Colab's warning). Its first cell installs the
   tools and downloads the data, about 30 s. Paste the two cards into the chat, paste the code the
   assistant writes into new cells, run them, and paste errors and outputs back into the chat.
   Colab's own Gemini panel (the ✨ icon) can be the assistant.
3. **No assistant that runs code?** Team up with someone who has one.

The cards are in `briefs/`: a **tool card** tells the assistant how to use Chromhandler or
Catalax, a **task card** tells it what you want from this dataset. Paste the tool card, then the
task card, then write: *Let's start with task 1.* Then:

- Run the code it gives you. If there is an error, paste the error back.
- Look at every plot before you continue. The assistant will ask you for decisions, e.g. where
  the peak is. Those are yours to make.
- The task card lists checks. You are done when they pass and you can answer the questions below.

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
