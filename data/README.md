# The dataset: initial-rate kinetics of Neu5Ac synthase

Source: Çakar MM, Milčić N, Andreadaki T, Charnock S, Fessner W-D, Findrik Blažević Z (2024). Kinetic
characterization of two neuraminic acid synthases and evaluation of their application potential.
*Appl Microbiol Biotechnol* 108, 446. <https://doi.org/10.1007/s00253-024-13277-1>. Cite the paper
if you use the data.

Neu5Ac synthase (NeuS) condenses N-acetylmannosamine (ManNAc) and phosphoenolpyruvate (PEP)
into N-acetylneuraminic acid (Neu5Ac, sialic acid):

```
ManNAc + PEP  →  Neu5Ac + Pi        (NeuS, divalent metal cofactor, H2O)
```

![reaction scheme](../slides/figures/reaction_scheme.png)

The reaction was followed by HPLC with a photodiode-array detector (215 nm); the chromatograms
are Shimadzu LabSolutions ASCII exports with a peak table.

| Molecule | Role | PubChem CID | Quantified here |
| --- | --- | --- | --- |
| ManNAc | substrate | 11096158 | no |
| PEP | substrate | 1005 | no (elutes as two peaks) |
| Neu5Ac | product | 439197 | **yes** |

## Files

| Path | Content |
| --- | --- |
| `calibration/CAL_1.txt … CAL_5.txt` | Five calibration standards with 1, 2, 3, 4 and 5 mM of ManNAc, PEP and Neu5Ac each. |
| `kinetic_series/MAN_*/` | ManNAc series: 13 reactions, ManNAc varied 0–100 mM, PEP fixed at 20 mM. |
| `kinetic_series/PEP_*/` | PEP series: 11 reactions, PEP varied 0–20 mM, ManNAc fixed at 50 mM. |
| `conditions.csv` | Initial concentrations of every reaction and standard, by `sample_id`. |

Each reaction folder holds six exports named `<sample_id>_<minutes>min.txt`, one per sampling
time from 0 to about 15 min.

`conditions.csv` columns: `ManNAc`, `PEP`, `Neu5Ac`, `NeuS` in mM; `enzyme` is the same NeuS
concentration in mg/mL (0.016 mg/mL in the reaction). `NeuS` = 0.016 g/L ÷ 38 649.8 g/mol =
4.14·10⁻⁴ mM; molar mass of the NeuS monomer from ESI-MS.

## Where the product elutes

Retention times shifted between the two measurement sessions; the elution order is the same.

| | Neu5Ac retention time | suggested window |
| --- | --- | --- |
| calibration standards | 11.35–11.50 min | 11.41 ± 0.05 min |
| kinetic samples | 9.80–10.35 min | 10.05 ± 0.20 min |

The substrates are not quantified in this workshop: the substrate concentrations enter the model
as their known initial values from `conditions.csv`.

## Kinetic model

Two-substrate Michaelis–Menten with the enzyme concentration in the rate law, so `kcat` is
reported directly:

```
v = kcat · [NeuS] · [ManNAc] · [PEP] / ((Km_ManNAc + [ManNAc]) · (Km_PEP + [PEP]))
d[ManNAc]/dt = d[PEP]/dt = −v        d[Neu5Ac]/dt = +v        d[NeuS]/dt = 0
```

Units: concentrations in mM, time in min, so `kcat` is in min⁻¹ and `Km` in mM.
Only Neu5Ac is observable: it is the only state with data, so it alone enters the likelihood;
ManNAc, PEP and NeuS are simulated from their initial values.
The metal cofactor is not part of the model (a simplification).
