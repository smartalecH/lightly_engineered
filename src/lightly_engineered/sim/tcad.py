from dataclasses import dataclass
import json
from pathlib import Path
from typing import Literal
import warnings

import numpy as np

from lightly_engineered.config import PhaseShifterConfig


@dataclass
class TCADSweepResult:
    voltage_v: np.ndarray
    carrier_delta_cm3: np.ndarray
    delta_neff_real: np.ndarray
    delta_loss_db_per_cm: np.ndarray
    r_per_m: np.ndarray


@dataclass(frozen=True)
class DevsimRunConfig:
    results_file: Path | None = None


TCADBackend = Literal["auto", "surrogate", "devsim"]


def _surrogate_tcad(
    ps_cfg: PhaseShifterConfig,
    voltage_v: np.ndarray,
) -> TCADSweepResult:
    """Surrogate carrier sweep used when a DEVSIM result is unavailable."""
    # Reverse bias lowers free carrier overlap; forward bias increases it.
    # This smooth approximation keeps the sign/shape physically plausible.
    active_doping = 0.5 * (ps_cfg.p_active_cm3 + ps_cfg.n_active_cm3)
    carrier_delta_cm3 = 0.18 * active_doping * np.tanh(voltage_v / 1.2)

    # Plasma-dispersion surrogate: more carriers -> lower index.
    delta_neff_real = -1.7e-4 * (carrier_delta_cm3 / 1e17)

    # Free-carrier absorption surrogate.
    delta_loss_db_per_cm = 0.45 * np.abs(carrier_delta_cm3 / 1e17)

    # Sheet/contact resistance drops with forward bias due to higher carrier density.
    r0 = 14.0  # ohm / mm equivalent trend anchor
    r_per_m = 1e3 * r0 / (1.0 + 0.35 * np.maximum(voltage_v, 0.0))

    return TCADSweepResult(
        voltage_v=voltage_v,
        carrier_delta_cm3=carrier_delta_cm3,
        delta_neff_real=delta_neff_real,
        delta_loss_db_per_cm=delta_loss_db_per_cm,
        r_per_m=r_per_m,
    )


def _load_devsim_results(
    cfg: DevsimRunConfig,
) -> TCADSweepResult:
    if cfg.results_file is None:
        raise FileNotFoundError("No DEVSIM results file was provided.")
    payload = json.loads(cfg.results_file.read_text())
    return TCADSweepResult(
        voltage_v=np.asarray(payload["voltage_v"], dtype=float),
        carrier_delta_cm3=np.asarray(payload["carrier_delta_cm3"], dtype=float),
        delta_neff_real=np.asarray(payload["delta_neff_real"], dtype=float),
        delta_loss_db_per_cm=np.asarray(payload["delta_loss_db_per_cm"], dtype=float),
        r_per_m=np.asarray(payload["r_per_m"], dtype=float),
    )


def run_carrier_bias_sweep(
    ps_cfg: PhaseShifterConfig | None = None,
    voltage_v: np.ndarray | None = None,
    backend: TCADBackend = "auto",
    devsim: DevsimRunConfig | None = None,
) -> TCADSweepResult:
    """Carrier sweep using DEVSIM data when available, with surrogate fallback."""
    ps_cfg = ps_cfg or PhaseShifterConfig()
    devsim = devsim or DevsimRunConfig()
    voltage_v = (
        np.asarray(voltage_v, dtype=float)
        if voltage_v is not None
        else np.linspace(-2.0, 2.0, 21)
    )

    if backend == "surrogate":
        return _surrogate_tcad(ps_cfg=ps_cfg, voltage_v=voltage_v)

    if backend in ("auto", "devsim"):
        try:
            return _load_devsim_results(cfg=devsim)
        except Exception as exc:
            if backend == "devsim":
                raise RuntimeError(f"Failed to load DEVSIM results: {exc}") from exc
            warnings.warn(
                f"DEVSIM results unavailable ({exc}); using surrogate TCAD model.",
                RuntimeWarning,
                stacklevel=2,
            )
            return _surrogate_tcad(ps_cfg=ps_cfg, voltage_v=voltage_v)

    raise ValueError(f"Unsupported TCAD backend: {backend}")
