import gdsfactory as gf

from lightly_engineered.pdk.cross_sections import xs_strip


@gf.cell
def directional_coupler(length: float = 20.0, gap: float = 0.20, width: float = 0.45):
    return gf.components.coupler(
        gap=gap,
        length=length,
        cross_section=xs_strip(width=width),
    )


@gf.cell
def mmi1x2():
    return gf.components.mmi1x2()


@gf.cell
def mmi2x1():
    # gdsfactory v9 exposes mmi1x2 but not mmi2x1; build it by rotation + port remap.
    c = gf.Component()
    ref = c << gf.components.mmi1x2()
    ref.rotate(180)
    c.add_port("o1", port=ref.ports["o2"])
    c.add_port("o2", port=ref.ports["o3"])
    c.add_port("o3", port=ref.ports["o1"])
    return c
