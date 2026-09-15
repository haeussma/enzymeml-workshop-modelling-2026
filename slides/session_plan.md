# Session plan · Wednesday 16 September 2026, 9:00–12:00

Hands-on session 2, 7th EnzymeML Workshop. Deck: `slides/workshop.pptx`.

## Before the session

- Make `github.com/haeussma/enzymeml-workshop-modelling-2026` public; open the Colab link from the README once
  and run the first cell (install + clone, about 2 min) to be sure it works.
- Have a chat assistant open in a second window with an empty conversation.
- Print or share the README link; participants need only that link.

## Run of show

| Time | Block | What happens |
| --- | --- | --- |
| 9:00 | Introduction (15 min) | Slides: a year of language models; the assistant types, you decide; workflow; the reaction; where the product elutes; how the session runs; the toolkit. |
| 9:15 | Live demo task 1 (15 min) | See script below. Ends with `neus_enzymeml.json` and the time-course plot. |
| 9:30 | Hands-on task 1 (45 min) | Participants work in pairs. Walk around; watch for the failure modes below. |
| 10:15 | Break (15 min) | |
| 10:30 | Live demo task 2 (10 min) | Paste `catalax.md` + `task_2_kinetic_model.md`; sample (10 s locally); show the summary, the corner plot and the fit plot. |
| 10:40 | Hands-on task 2 (45 min) | Those who did not finish task 1 start from `checkpoints/neus_enzymeml.json`. |
| 11:25 | Compare and discuss (25 min) | Collect `kcat`, `Km_ManNAc`, `Km_PEP` from every pair on one slide or whiteboard. Then the misfit question. |
| 11:50 | Wrap-up (10 min) | Take-home slide; ask what did not work: that is the feedback we need. |

## Live demo script, task 1

1. Open Colab, run the first cell while talking (2 min of install time is the moment to explain
   the two cards).
2. Paste `briefs/chromhandler.md`, then `briefs/task_1_chromatograms_to_enzymeml.md`, then
   "Let's start with task 1."
3. Run the reading step; show the count: 24 reactions, 5 standards.
4. Show the peak plot; point at the two Neu5Ac clusters and the shift between sessions.
5. Show slope and R²; accept the calibration explicitly ("this is my decision, not the
   assistant's").
6. **The deliberate mistake:** when the assistant asks for the window in the reactions, say
   "the same as in the standards, 11.41 ± 0.05". Chromhandler prints a warning table "No peaks
   found for Neu5Ac in 6 measurement(s)" per reaction, the document contains Neu5Ac with
   0 values, and the check "6 values per reaction" fails. Say why: the retention time shifted
   between the sessions, the plot in step 4 showed it. Correct to 10.05 ± 0.20 and continue.
   (Alternative mistake: 10.63 ± 0.15 catches the ManNAc peak; the "product" then starts at
   5 mM and falls, and the rise check fails.)
7. Export; run the checks; show the time-course plot. Point at the controls with no product.

Note: a window that is too wide does not fail. If several peaks lie in it, chromhandler takes
the one closest to the given retention time and prints a warning with the candidates.

## Failure modes to watch for during hands-on

- Only one card pasted, or the task card first: the assistant invents an API. Fix: paste both,
  tool card first.
- The assistant "assigns" peaks without `auto_assign=True`: no peaks assigned, calibration has no
  points. Fix: point to the card section "Define molecules and assign peaks".
- Window too wide or too narrow: see the demo mistake.
- Concentrations missing in the document: `extrapolate=True` forgotten (t = 0 lies below the
  lowest standard).
- Task 2, parameters at the prior bounds, `sigma` of the order of mM, hundreds of divergences,
  minutes per iteration: the assistant used `observable=False` for the unmeasured states.
  In Catalax 0.5.5 this breaks the sampler; every state stays observable and the unmeasured
  ones get NaN arrays (the card says so).
- Task 2, error about inconsistent states or a shape error: the NaN filling is missing.
- Task 2, nonsense posterior: `enable_x64()` was not called first.
- Task 2 takes 10 s here; expect a few minutes in Colab (compilation plus slower CPUs).
- Colab: the first cell was skipped; nothing is installed. Run it.
- The assistant loses the card in a long chat: start a new chat and paste again.

## Discussion prompts, 11:25

- Everybody's `kcat` on one line: how much do they differ, and why (windows, bounds, which
  reactions were used)?
- The reference fit over-predicts the ManNAc series and under-predicts the PEP series. The
  series were measured on different days. What would you do next: a per-day activity factor,
  a new experiment, both?
- Which decisions did the assistant try to make for you? Which did you take back?
