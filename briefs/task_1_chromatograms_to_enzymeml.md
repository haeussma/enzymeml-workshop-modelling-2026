# Task 1 · From chromatograms to an EnzymeML document

Paste `chromhandler.md` into the chat first, then this file, then write: *Let's start with task 1.*

## What you want

An EnzymeML document `neus_enzymeml.json` with the Neu5Ac concentration time courses of all
24 reactions, calibrated with the five standards.

## The experiment

Neu5Ac synthase (NeuS) catalyses `ManNAc + PEP → Neu5Ac + Pi` at pH 7.5 and 37 °C.
Only the product Neu5Ac is quantified. PubChem CIDs: ManNAc 11096158, PEP 1005, Neu5Ac 439197.

## Data (folder `data/`)

- `calibration/CAL_1.txt … CAL_5.txt`: standards with 1, 2, 3, 4 and 5 mM Neu5Ac
  (they also contain ManNAc and PEP; ignore those).
- `kinetic_series/<sample_id>/<sample_id>_<minutes>min.txt`: 24 reactions, six injections
  each. `MAN_*`: ManNAc varied, PEP fixed. `PEP_*`: PEP varied, ManNAc fixed.
- `conditions.csv`: initial concentrations in mM per `sample_id`: `ManNAc`, `PEP`, `Neu5Ac`
  (0 in the reactions), `NeuS` (the enzyme, 4.14·10⁻⁴ mM). The column `enzyme` is the same
  enzyme amount in mg/mL; ignore it.

## Where Neu5Ac elutes

Standards and reactions were measured in different sessions; the retention time shifted.

| | window |
| --- | --- |
| standards | 11.41 ± 0.05 min |
| reactions | 10.05 ± 0.20 min |

Confirm both windows on a plot of all peaks (retention time against area) before using them.

## Steps

1. Read the 24 reaction folders (`mode="timecourse"`) and the calibration folder
   (`mode="calibration"`, values 1 … 5 mM).
2. Plot all peaks; confirm the windows.
3. On the calibration handler: define Neu5Ac with the standards window, auto-assign,
   `add_standard`. Print slope and R².
4. Add the calibrated Neu5Ac to every reaction handler with the reactions window. Define
   ManNAc and PEP with their initial concentrations from `conditions.csv` (`retention_time=None`)
   and NeuS as the protein.
5. `to_enzymeml(..., calculate_concentration=True, extrapolate=True)`; save as `neus_enzymeml.json`.
6. Plot Neu5Ac against time for both series and run the checks.

## Checks (expected values)

- 24 reactions, 5 standards; 6 time points per reaction, strictly increasing.
- Calibration slope ≈ 239 000 area per mM, R² ≥ 0.99.
- 24 measurements in the document, each with 6 Neu5Ac values.
- Neu5Ac rises by more than 0.2 mM in every reaction with ManNAc ≥ 1 mM and PEP ≥ 1 mM
  (14 reactions). Reactions with ManNAc = 0 or PEP = 0 stay near zero. The remaining
  reactions have one substrate below 1 mM and form little product; no check for them.
