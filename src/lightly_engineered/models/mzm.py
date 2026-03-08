from dataclasses import dataclass
import numpy as np

from lightly_engineered.models.phase_shifter import PhaseShifterCompact
from lightly_engineered.models.tline import RLGCLine


@dataclass
class PushPullMZM:
    top: PhaseShifterCompact
    bot: PhaseShifterCompact
    rf_line: RLGCLine | None = None

    def transmission(self, vdiff: float, vcm: float = 0.0) -> float:
        vt = vcm + 0.5 * vdiff
        vb = vcm - 0.5 * vdiff

        phit = self.top.delta_phase(vt)
        phib = self.bot.delta_phase(vb)
        eout = 0.5 * (np.exp(1j * phit) + np.exp(1j * phib))
        return float(np.abs(eout) ** 2)
