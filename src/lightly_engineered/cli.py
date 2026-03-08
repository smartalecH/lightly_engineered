import argparse
from pathlib import Path

from lightly_engineered.layout.mzm import mzm
from lightly_engineered.sim.optical_modes import solve_cross_section_modes
from lightly_engineered.workflows.build_compact_model import (
    build_phase_shifter_compact,
    save_compact_model,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("show-layout")
    sub.add_parser("run-modes")
    compact = sub.add_parser("build-compact")
    compact.add_argument("--out", type=Path, default=Path("outputs/phase_shifter_compact.json"))
    compact.add_argument(
        "--tcad-backend",
        choices=("auto", "surrogate", "devsim"),
        default="auto",
    )
    compact.add_argument(
        "--electrostatics-backend",
        choices=("auto", "surrogate", "palace"),
        default="auto",
    )
    compact.add_argument("--devsim-results-file", type=Path, default=None)
    compact.add_argument("--palace-results-file", type=Path, default=None)

    args = parser.parse_args()

    if args.cmd == "show-layout":
        c = mzm()
        c.show()
    elif args.cmd == "run-modes":
        result = solve_cross_section_modes()
        print(result.neff)
    elif args.cmd == "build-compact":
        model = build_phase_shifter_compact(
            tcad_backend=args.tcad_backend,
            electrostatics_backend=args.electrostatics_backend,
            devsim_results_file=args.devsim_results_file,
            palace_results_file=args.palace_results_file,
        )
        save_compact_model(model, args.out)
        print(args.out)
