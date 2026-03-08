from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from lightly_engineered.models.mzm import PushPullMZM
from lightly_engineered.models.phase_shifter import PhaseShifterCompact
from lightly_engineered.models.tline import RLGCLine


def load_compact_model(path: Path) -> PhaseShifterCompact:
    payload = json.loads(path.read_text())
    neff_grid = np.asarray(payload["neff_grid_real"]) + 1j * np.asarray(payload["neff_grid_imag"])
    return PhaseShifterCompact(
        wavelength_um=float(payload["wavelength_um"]),
        length_um=float(payload["length_um"]),
        voltage_grid=np.asarray(payload["voltage_grid"], dtype=float),
        neff_grid=neff_grid.astype(complex),
        loss_grid_db_per_cm=np.asarray(payload["loss_grid_db_per_cm"], dtype=float),
        c_per_m=float(payload["c_per_m"]),
        r_per_m=float(payload["r_per_m"]),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--compact-model",
        type=Path,
        default=Path("outputs/phase_shifter_compact.json"),
    )
    parser.add_argument("--out", type=Path, default=Path("outputs/mzm_sweep.json"))
    parser.add_argument("--vmin", type=float, default=-2.0)
    parser.add_argument("--vmax", type=float, default=2.0)
    parser.add_argument("--npts", type=int, default=101)
    parser.add_argument("--vcm", type=float, default=0.0)
    args = parser.parse_args()

    ps = load_compact_model(args.compact_model)
    line = RLGCLine(
        r_per_m=ps.r_per_m,
        l_per_m=0.45e-6,
        g_per_m=1e-3,
        c_per_m=ps.c_per_m,
    )
    device = PushPullMZM(top=ps, bot=ps, rf_line=line)

    vdiff = np.linspace(args.vmin, args.vmax, args.npts)
    transmission = np.asarray([device.transmission(vd, vcm=args.vcm) for vd in vdiff], dtype=float)

    l = ps.length_um * 1e-6
    c_total = ps.c_per_m * l
    r_total = ps.r_per_m * l
    f3db_hz = 1.0 / (2.0 * np.pi * r_total * c_total)

    payload = dict(
        vdiff_v=vdiff.tolist(),
        transmission=transmission.tolist(),
        t_min=float(np.min(transmission)),
        t_max=float(np.max(transmission)),
        extinction_db=float(10.0 * np.log10(np.max(transmission) / max(np.min(transmission), 1e-12))),
        rc_f3db_hz=float(f3db_hz),
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2))
    print(f"Wrote sweep: {args.out}")
    print(f"Extinction={payload['extinction_db']:.2f} dB, RC f3dB={payload['rc_f3db_hz']:.3e} Hz")


if __name__ == "__main__":
    main()
