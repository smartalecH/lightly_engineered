from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from lightly_engineered.config import MZMConfig
from lightly_engineered.models.phase_shifter import PhaseShifterCompact
from lightly_engineered.sim.electrostatics import (
    ElectrostaticsBackend,
    PalaceRunConfig,
    extract_capacitance_sweep,
)
from lightly_engineered.sim.optical_modes import solve_cross_section_modes
from lightly_engineered.sim.tcad import TCADBackend, DevsimRunConfig, run_carrier_bias_sweep


def build_phase_shifter_compact(
    wavelength_um: float = 1.31,
    length_um: float = 2_000.0,
    voltage_v: np.ndarray | None = None,
    tcad_backend: TCADBackend = "auto",
    electrostatics_backend: ElectrostaticsBackend = "auto",
    devsim_results_file: Path | None = None,
    palace_results_file: Path | None = None,
) -> PhaseShifterCompact:
    voltage_v = (
        np.asarray(voltage_v, dtype=float)
        if voltage_v is not None
        else np.linspace(-2.0, 2.0, 21)
    )
    optical = solve_cross_section_modes(wavelength_um=wavelength_um, num_modes=1)
    tcad = run_carrier_bias_sweep(
        voltage_v=voltage_v,
        backend=tcad_backend,
        devsim=DevsimRunConfig(results_file=devsim_results_file),
    )
    electro = extract_capacitance_sweep(
        voltage_v=voltage_v,
        backend=electrostatics_backend,
        palace=PalaceRunConfig(results_file=palace_results_file),
    )

    neff0 = np.real(optical.neff[0])
    neff_grid = neff0 + tcad.delta_neff_real + 1j * (tcad.delta_loss_db_per_cm / 8.686)

    return PhaseShifterCompact(
        wavelength_um=wavelength_um,
        length_um=length_um,
        voltage_grid=tcad.voltage_v,
        neff_grid=neff_grid,
        loss_grid_db_per_cm=tcad.delta_loss_db_per_cm,
        c_per_m=float(np.mean(electro.c_per_m)),
        r_per_m=float(np.mean(tcad.r_per_m)),
    )


def save_compact_model(model: PhaseShifterCompact, path: Path) -> None:
    payload = dict(
        wavelength_um=float(model.wavelength_um),
        length_um=float(model.length_um),
        voltage_grid=model.voltage_grid.tolist(),
        neff_grid_real=np.real(model.neff_grid).tolist(),
        neff_grid_imag=np.imag(model.neff_grid).tolist(),
        loss_grid_db_per_cm=model.loss_grid_db_per_cm.tolist(),
        c_per_m=float(model.c_per_m),
        r_per_m=float(model.r_per_m),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("outputs/phase_shifter_compact.json"))
    parser.add_argument("--wavelength-um", type=float, default=MZMConfig().wavelength_um)
    parser.add_argument("--length-um", type=float, default=MZMConfig().phase_shifter_length_um)
    parser.add_argument(
        "--tcad-backend",
        choices=("auto", "surrogate", "devsim"),
        default="auto",
    )
    parser.add_argument(
        "--electrostatics-backend",
        choices=("auto", "surrogate", "palace"),
        default="auto",
    )
    parser.add_argument("--devsim-results-file", type=Path, default=None)
    parser.add_argument("--palace-results-file", type=Path, default=None)
    args = parser.parse_args()

    model = build_phase_shifter_compact(
        wavelength_um=args.wavelength_um,
        length_um=args.length_um,
        tcad_backend=args.tcad_backend,
        electrostatics_backend=args.electrostatics_backend,
        devsim_results_file=args.devsim_results_file,
        palace_results_file=args.palace_results_file,
    )
    save_compact_model(model, args.out)
    print(f"Wrote compact model: {args.out}")
    print(f"c_per_m={model.c_per_m:.4e}, r_per_m={model.r_per_m:.4e}")


if __name__ == "__main__":
    main()
