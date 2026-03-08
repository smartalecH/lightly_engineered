# Silicon MZM tutorial (O-band)

This tutorial shows how to use `lightly_engineered` to build a **45CLO-like surrogate silicon Mach-Zehnder modulator** and extract key EO metrics in the **O-band (1.26-1.36 um)**.

## What is grounded vs guessed

Grounded in the public 45CLO material:

- top silicon thickness: **160 nm**
- slab option: **50 nm**
- BOX thickness: **2 um**
- RF-friendly metal stack exists in the platform

Guesses in this surrogate model:

- rib width
- exact implant windows
- exact dopant profiles
- exact contact setbacks
- exact electrode geometry

That is enough for a serious surrogate flow even if it is not a foundry signoff model.

## 1. Plot the arm cross section (gdsfactory-native objects)

The cross-section visualization in the notebook now uses:

```python
from lightly_engineered.pdk.cross_sections import xs_phase_shifter
from lightly_engineered.pdk.layer_stack import get_layer_stack

xs = xs_phase_shifter()
layer_stack = get_layer_stack()
```

with section geometry from `xs` and vertical placement from `layer_stack`.

## 2. Define the layer stack

- 160 nm top Si
- 50 nm slab
- 2 um BOX
- simple upper metal layers for future RF work

## 3. Define the phase-shifter cross section

The core cross-section definition is in `src/lightly_engineered/pdk/cross_sections.py`.

```python
from lightly_engineered.pdk.cross_sections import xs_phase_shifter

xs = xs_phase_shifter()
```

This creates:

- the rib waveguide
- the slab region
- active P/N marker regions
- heavily doped contact regions

## 4. Build the MZM layout in gdsfactory

The main device builder is in `src/lightly_engineered/layout/mzm.py`.

```python
from lightly_engineered.layout.mzm import mzm

c = mzm()
c.show()
```

The straight phase shifter used in each arm lives in:

- `src/lightly_engineered/layout/phase_shifter.py`

The current MZM uses MMIs, but you can swap in directional couplers later through the PDK layer.

## 5. Solve optical modes and extract O-band dispersion

The optical mode wrapper is in `src/lightly_engineered/sim/optical_modes.py`.

```python
from lightly_engineered.sim.optical_modes import solve_cross_section_modes

result = solve_cross_section_modes(wavelength_um=1.31)
print(result.neff)
```

Then sweep wavelength over O-band to compute and plot:

- effective index `n_eff(lambda)`
- group index `n_g(lambda) = n_eff - lambda * dn_eff/dlambda`

Also plot the mode field intensity at O-band center (1.31 um).

## 5. Run electro-optic compact-model build

The EO build workflow is implemented in:

- `src/lightly_engineered/workflows/build_compact_model.py`

It combines:

- optical mode solve (`sim/optical_modes.py`)
- carrier/bias sweep (`sim/tcad.py`)
- capacitance extraction (`sim/electrostatics.py`)

### 5.1 Surrogate-only run

```bash
uv run --python 3.11 --extra full python -m lightly_engineered.workflows.build_compact_model \
  --tcad-backend surrogate \
  --electrostatics-backend surrogate \
  --out outputs/phase_shifter_compact.json
```

### 5.2 Use DEVSIM and Palace result files

The workflow can ingest solver outputs from JSON files.

Expected DEVSIM result JSON keys:

- `voltage_v`
- `carrier_delta_cm3`
- `delta_neff_real`
- `delta_loss_db_per_cm`
- `r_per_m`

Expected Palace result JSON keys:

- `voltage_v`
- `c_per_m`
- `depletion_width_um`

Run with real-solver data:

```bash
uv run --python 3.11 --extra full python -m lightly_engineered.workflows.build_compact_model \
  --tcad-backend devsim \
  --electrostatics-backend palace \
  --devsim-results-file outputs/devsim_sweep.json \
  --palace-results-file outputs/palace_sweep.json \
  --out outputs/phase_shifter_compact.json
```

## 6. Extract frequency-domain electrical and EO response

Using the compact model and RLGC line:

- compute contact/transmission-line parameters vs frequency (`Zc`, attenuation)
- estimate EO frequency response and report `f3dB`

This is intended as a first-order EO bandwidth prediction.

## 7. Extract wavelength-domain optical link metrics

Sweep O-band wavelengths and compute:

- insertion loss vs wavelength
- extinction ratio vs wavelength

In this surrogate tutorial we include an explicit baseline passive loss term for realistic IL plotting.

## 8. Extract VpiL at O-band center

The notebook now includes an explicit `VπL` section for the modulator arm cross section.

Convention used:

- single-arm phase shift: find `Vπ` where `|Δφ(V)| = π`
- push-pull differential drive: find `Vπ` where `|Δφ_diff(Vdiff)| = π`
- convert to `VπL` with `L` in cm:
  `VπL = Vπ * L_cm`
- if `π` is not crossed in the available bias range, use a small-signal extrapolated `Vπ` from the slope near 0 V

Implementation detail:

- if `outputs/devsim_sweep.json` exists, the cell uses it (`backend='devsim'`)
- otherwise it falls back to the surrogate TCAD sweep

This gives both:

- `VπL_single` (single-arm convention)
- `VπL_pushpull` (differential push-pull convention)

## 9. Why this structure matters

The point is not just one MZM. The point is to make a reusable framework for:

- modulators
- photonic links
- coherent front ends
- larger silicon photonics systems

That is why the package separates:

- PDK definitions
- layout generators
- simulation wrappers
- compact models
- tutorials
- Quarto posts

## 10. Sweep MZM response

After building the compact model:

```bash
uv run --python 3.11 --extra full python -m lightly_engineered.workflows.sweep_mzm \
  --compact-model outputs/phase_shifter_compact.json \
  --out outputs/mzm_sweep.json
```

This gives you the path from:

1. layout
2. optical mode solve
3. bias-dependent carrier solve
4. capacitance extraction
5. compact model build
6. static and dynamic MZM response

## 11. Extract mode-index sensitivity vs voltage and wavelength

To get physically meaningful `dn_eff/dV`, use a DEVSIM-to-FEMWELL sweep:

1. Solve carrier distributions in DEVSIM vs bias (`n(x,z,V)`, `p(x,z,V)`).
2. Convert carriers to optical material perturbation and solve FEMWELL modes at each `(V, λ)`.
3. Store `n_eff(V, λ)` and compute `∂n_eff/∂V`.

The notebook reads this file when present:

- `outputs/devsim_femwell_neff_sweep.json`

Expected keys:

- `wavelength_um`: 1D array
- `voltage_v`: 1D array
- `neff_real`: 2D array with shape `[len(wavelength_um), len(voltage_v)]`

If this file is missing, the notebook falls back to the surrogate path so plots still run.

From `∂n_eff/∂V`, it also reports small-signal `VπL` estimates:

- single-arm: `VπL ≈ λ / (2 * |∂n_eff/∂V|)` (with `λ` in cm)
- push-pull differential: half the single-arm value

## 12. Run DEVSIM directly from the notebook

The notebook now has an optional DEVSIM launcher cell (`run_devsim` toggle).

It calls:

- `devsim scripts/devsim_pn_sweep.py`

and passes:

- `LE_DEVSIM_OUT` (target JSON path, typically `outputs/devsim_sweep.json`)
- `LE_VOLTAGE_GRID` (comma-separated bias list)

Template deck script:

- `scripts/devsim_pn_sweep.py`

This template defines the output JSON contract expected by the rest of the tutorial.
By default it raises until you replace it with a real DEVSIM deck.
For plumbing tests only, set `LE_ALLOW_TEMPLATE_SURROGATE=1`.
