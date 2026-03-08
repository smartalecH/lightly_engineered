#!/usr/bin/env python3
"""Template DEVSIM bias sweep deck for lightly_engineered.

Run with:
  devsim scripts/devsim_pn_sweep.py

Environment inputs expected from the notebook cell:
  LE_DEVSIM_OUT=<path to output JSON>
  LE_VOLTAGE_GRID=<comma-separated voltages>

Required JSON keys produced:
  voltage_v
  carrier_delta_cm3
  delta_neff_real
  delta_loss_db_per_cm
  r_per_m
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np


def _parse_voltage_grid() -> np.ndarray:
    raw = os.environ.get("LE_VOLTAGE_GRID", "-2,-1,0,1,2")
    return np.asarray([float(x) for x in raw.split(",")], dtype=float)


def _output_path() -> Path:
    out = os.environ.get("LE_DEVSIM_OUT", "outputs/devsim_sweep.json")
    return Path(out)


def _surrogate_for_pipeline_test(voltage_v: np.ndarray) -> dict[str, list[float]]:
    # Optional path for validating notebook plumbing before real DEVSIM deck setup.
    # Enable with: LE_ALLOW_TEMPLATE_SURROGATE=1
    carrier_delta_cm3 = 1.2e17 * np.tanh(voltage_v / 1.4)
    delta_neff_real = -1.6e-4 * (carrier_delta_cm3 / 1e17)
    delta_loss_db_per_cm = 0.42 * np.abs(carrier_delta_cm3 / 1e17)
    r_per_m = 1e3 * 14.0 / (1.0 + 0.30 * np.maximum(voltage_v, 0.0))
    return {
        "voltage_v": voltage_v.tolist(),
        "carrier_delta_cm3": carrier_delta_cm3.tolist(),
        "delta_neff_real": delta_neff_real.tolist(),
        "delta_loss_db_per_cm": delta_loss_db_per_cm.tolist(),
        "r_per_m": r_per_m.tolist(),
    }


def main() -> None:
    voltage_v = _parse_voltage_grid()
    out = _output_path()
    out.parent.mkdir(parents=True, exist_ok=True)

    if os.environ.get("LE_ALLOW_TEMPLATE_SURROGATE", "0") == "1":
        payload = _surrogate_for_pipeline_test(voltage_v)
        out.write_text(json.dumps(payload, indent=2))
        print(f"Wrote surrogate pipeline test file: {out}")
        return

    raise RuntimeError(
        "Template script not yet connected to a physical DEVSIM deck. "
        "Replace main() with your device mesh/material/contact/bias solve and "
        "write the required JSON keys listed in this file header. "
        "For a temporary plumbing test, set LE_ALLOW_TEMPLATE_SURROGATE=1."
    )


if __name__ == "__main__":
    main()
