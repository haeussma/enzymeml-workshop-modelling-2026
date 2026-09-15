# Task 2 · Kinetic model

Paste `catalax.md` into the chat first, then this file, then write: *Let's start with task 2.*

## What you want

The posterior distributions of `kcat`, `Km_ManNAc` and `Km_PEP` (mean ± sd and 3–97 % interval)
from the 24 Neu5Ac time courses in `neus_enzymeml.json` (your result of task 1, or
`checkpoints/neus_enzymeml.json`), a corner plot, and a plot of data and model.

## The model

Two-substrate Michaelis–Menten with the enzyme concentration in the rate law:

```
v = kcat * NeuS * ManNAc * PEP / ((Km_ManNAc + ManNAc) * (Km_PEP + PEP))
d[ManNAc]/dt = −v     d[PEP]/dt = −v     d[Neu5Ac]/dt = +v     d[NeuS]/dt = 0
```

States: `ManNAc`, `PEP`, `Neu5Ac`, `NeuS`. Units mM and min, so `kcat` is in 1/min and `Km` in mM.

## Data rules

- Only Neu5Ac has data. Fill `ManNAc`, `PEP` and `NeuS` with NaN arrays and leave every state
  observable (the default).
- Initial ManNAc and PEP: the nominal values from `conditions.csv` (columns `ManNAc`, `PEP`;
  `sample_id` equals the measurement id). Initial NeuS comes from the document (4.14·10⁻⁴ mM).
- Priors, all log-uniform: `kcat` 1 … 1e4 1/min, `Km_ManNAc` and `Km_PEP` 1e-3 … 100 mM.
- Measurement noise: `yerrs = 0.05` mM (assumed Neu5Ac noise), Gaussian likelihood
  (`likelihood=dist.Normal`).

## Steps

1. `enable_x64`, `set_host_device_count(2)`, load the document, build the dataset, apply the
   data rules.
2. Build the model and set the priors.
3. Sample with `MCMCConfig(num_warmup=500, num_samples=1000, num_chains=2,
   chain_method="parallel", likelihood=dist.Normal)` and `run_mcmc(..., yerrs=0.05, ...)`.
   Print the wall time, the summary, and a table of mean, sd and 3–97 % interval per parameter
   (`kcat` also in 1/s).
4. Run the checks and draw the corner plot.
5. Set the posterior means as parameter values and plot data and model with
   `Dataset.plot(predictor=model)` on the dataset without the NaN arrays: one panel per reaction,
   ManNAc series (`MAN_*`) and PEP series (`PEP_*`).

## Checks (expected values)

- `r_hat < 1.01` for every parameter, zero divergences.
- Bound pressure: the 0.5–99.5 % range of every parameter at least a factor 3 inside its prior
  bounds (expected: more than one decade for all three).
- Posterior correlations |r| < 0.9 (expected: `kcat`–`Km_ManNAc` ≈ 0.6, `kcat`–`Km_PEP` ≈ 0.5,
  `Km_ManNAc`–`Km_PEP` ≈ 0.1).
- `kcat` ≈ 364 ± 6 1/min (≈ 6.1 1/s), `Km_ManNAc` ≈ 1.5 ± 0.2 mM, `Km_PEP` ≈ 0.6 ± 0.07 mM;
  estimated noise `sigma` ≈ 0.09 mM. Sampling takes about 10 s on a laptop, longer in Colab.
- The plot: the model over-predicts the ManNAc series slightly and under-predicts the PEP
  series. Point this out to the scientist; the two series were measured on different days.
