from dataclasses import dataclass
import json
from pathlib import Path
from typing import Literal
import warnings

import numpy as np

from lightly_engineered.config import PhaseShifterConfig, StackConfig


EPS0_F_PER_M = 8.854_187_812_8e-12
EPS_SI = 11.7


@dataclass
class ElectrostaticsSweepResult:
    voltage_v: np.ndarray
    c_per_m: np.ndarray
    depletion_width_um: np.ndarray


@dataclass(frozen=True)
class PalaceRunConfig:
    results_file: Path | None = None


ElectrostaticsBackend = Literal["auto", "surrogate", "palace"]


def _surrogate_electrostatics(
    ps_cfg: PhaseShifterConfig,
    stack_cfg: StackConfig,
    voltage_v: np.ndarray,
) -> ElectrostaticsSweepResult:
    """Surrogate junction capacitance extraction."""
    # Junction capacitance per unit length scales with lateral overlap width.
    width_eff_m = max(ps_cfg.active_width_um, 0.05) * 1e-6

    # Smooth depletion approximation around near-zero bias.
    w0_um = 0.16
    w_dep_um = w0_um * np.sqrt(np.maximum(0.4 - voltage_v, 0.06) / 0.4)
    w_dep_m = w_dep_um * 1e-6

    c_per_m = 2.0 * EPS0_F_PER_M * EPS_SI * width_eff_m / np.maximum(w_dep_m, 20e-9)
    return ElectrostaticsSweepResult(
        voltage_v=voltage_v,
        c_per_m=c_per_m,
        depletion_width_um=w_dep_um,
    )


def _load_palace_results(cfg: PalaceRunConfig) -> ElectrostaticsSweepResult:
    if cfg.results_file is None:
        raise FileNotFoundError("No Palace results file was provided.")
    payload = json.loads(cfg.results_file.read_text())
    return ElectrostaticsSweepResult(
        voltage_v=np.asarray(payload["voltage_v"], dtype=float),
        c_per_m=np.asarray(payload["c_per_m"], dtype=float),
        depletion_width_um=np.asarray(payload["depletion_width_um"], dtype=float),
    )


def extract_capacitance_sweep(
    ps_cfg: PhaseShifterConfig | None = None,
    stack_cfg: StackConfig | None = None,
    voltage_v: np.ndarray | None = None,
    backend: ElectrostaticsBackend = "auto",
    palace: PalaceRunConfig | None = None,
) -> ElectrostaticsSweepResult:
    """Capacitance sweep using Palace data when available, with surrogate fallback."""
    ps_cfg = ps_cfg or PhaseShifterConfig()
    stack_cfg = stack_cfg or StackConfig()
    palace = palace or PalaceRunConfig()
    voltage_v = (
        np.asarray(voltage_v, dtype=float)
        if voltage_v is not None
        else np.linspace(-2.0, 2.0, 21)
    )

    if backend == "surrogate":
        return _surrogate_electrostatics(ps_cfg=ps_cfg, stack_cfg=stack_cfg, voltage_v=voltage_v)

    if backend in ("auto", "palace"):
        try:
            return _load_palace_results(cfg=palace)
        except Exception as exc:
            if backend == "palace":
                raise RuntimeError(f"Failed to load Palace results: {exc}") from exc
            warnings.warn(
                f"Palace results unavailable ({exc}); using surrogate electrostatics model.",
                RuntimeWarning,
                stacklevel=2,
            )
            return _surrogate_electrostatics(ps_cfg=ps_cfg, stack_cfg=stack_cfg, voltage_v=voltage_v)

    raise ValueError(f"Unsupported electrostatics backend: {backend}")
