import gdsfactory as gf

from lightly_engineered.config import PhaseShifterConfig
from lightly_engineered.pdk.cross_sections import xs_phase_shifter


@gf.cell
def phase_shifter_straight(length: float = 2000.0, cfg: PhaseShifterConfig | None = None):
    cfg = cfg or PhaseShifterConfig()
    c = gf.Component()
    ref = c << gf.components.straight(length=length, cross_section=xs_phase_shifter(cfg))
    c.add_ports(ref.ports)
    return c
