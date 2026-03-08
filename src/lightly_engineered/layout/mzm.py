import gdsfactory as gf

from lightly_engineered.config import MZMConfig, PhaseShifterConfig
from lightly_engineered.layout.phase_shifter import phase_shifter_straight
from lightly_engineered.pdk.cells import mmi1x2, mmi2x1


@gf.cell
def mzm(mzm_cfg: MZMConfig | None = None, ps_cfg: PhaseShifterConfig | None = None):
    mzm_cfg = mzm_cfg or MZMConfig()
    ps_cfg = ps_cfg or PhaseShifterConfig()

    c = gf.Component()

    sp = c << mmi1x2()
    cb = c << mmi2x1()

    top = c << phase_shifter_straight(length=mzm_cfg.phase_shifter_length_um, cfg=ps_cfg)
    bot = c << phase_shifter_straight(length=mzm_cfg.phase_shifter_length_um, cfg=ps_cfg)

    x0 = 200.0
    top.move((x0, +mzm_cfg.arm_spacing_um / 2))
    bot.move((x0, -mzm_cfg.arm_spacing_um / 2))
    cb.move((x0 + mzm_cfg.phase_shifter_length_um + 200.0, 0))

    gf.routing.route_bundle(
        c,
        ports1=[sp.ports["o2"], sp.ports["o3"]],
        ports2=[top.ports["o1"], bot.ports["o1"]],
        cross_section="strip",
    )
    gf.routing.route_bundle(
        c,
        ports1=[top.ports["o2"], bot.ports["o2"]],
        ports2=[cb.ports["o1"], cb.ports["o2"]],
        cross_section="strip",
    )

    c.add_port("o1", port=sp.ports["o1"])
    c.add_port("o2", port=cb.ports["o3"])
    return c
