import gdsfactory as gf
from gdsfactory.cross_section import CrossSection, Section

from lightly_engineered.config import PhaseShifterConfig
from lightly_engineered.pdk.layers import LAYER


def xs_strip(width: float = 0.45) -> CrossSection:
    return gf.cross_section.cross_section(width=width, layer=LAYER.WG)


def xs_phase_shifter(cfg: PhaseShifterConfig | None = None) -> CrossSection:
    cfg = cfg or PhaseShifterConfig()
    active_offset = cfg.active_width_um / 2 + cfg.active_gap_um / 2

    # Cross-section composition:
    # - rib + slab layers are 45CLO-like (160 nm Si, 50 nm slab via StackConfig)
    # - doped regions/contact offsets are tutorial assumptions for a realistic
    #   depletion-style modulator surrogate, not foundry-verified dimensions.
    sections = [
        Section(width=cfg.slab_width_um, offset=0, layer=LAYER.SLAB, name="slab"),
        Section(
            width=cfg.rib_width_um,
            offset=0,
            layer=LAYER.WG,
            name="rib",
            port_names=("o1", "o2"),
        ),
        Section(width=cfg.active_width_um, offset=-active_offset, layer=LAYER.P, name="p_active"),
        Section(width=cfg.active_width_um, offset=+active_offset, layer=LAYER.N, name="n_active"),
        Section(width=cfg.contact_width_um, offset=-cfg.contact_offset_um, layer=LAYER.PPP, name="p_contact"),
        Section(width=cfg.contact_width_um, offset=+cfg.contact_offset_um, layer=LAYER.NPP, name="n_contact"),
    ]
    return CrossSection(sections=sections)
