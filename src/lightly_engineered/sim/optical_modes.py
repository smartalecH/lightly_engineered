from dataclasses import dataclass

import gdsfactory as gf
from gdsfactory.pdk import get_active_pdk
from gdsfactory.technology.layer_stack import LayerLevel

from lightly_engineered.config import StackConfig, PhaseShifterConfig
from lightly_engineered.pdk.cross_sections import xs_phase_shifter
from lightly_engineered.pdk.layer_stack import get_layer_stack
from lightly_engineered.pdk.layers import LAYER


@dataclass
class OpticalModeResult:
    neff: list[complex]
    raw: object


def solve_cross_section_modes(
    wavelength_um: float = 1.31,
    stack_cfg: StackConfig | None = None,
    ps_cfg: PhaseShifterConfig | None = None,
    num_modes: int = 4,
    include_doped_channels: bool = True,
) -> OpticalModeResult:
    from gplugins.femwell.mode_solver import compute_component_slice_modes

    stack_cfg = stack_cfg or StackConfig()
    ps_cfg = ps_cfg or PhaseShifterConfig()

    # Ensure a PDK is active so gdsfactory component factories can resolve defaults.
    try:
        get_active_pdk()
    except ValueError:
        gf.gpdk.PDK.activate()

    layer_stack = get_layer_stack(stack_cfg)
    if include_doped_channels:
        # Include side-channel doped masks as optical silicon regions so the mode
        # mesh captures lateral silicon channels around the rib.
        layer_stack.layers.update(
            {
                "p_active": LayerLevel(
                    layer=LAYER.P,
                    zmin=0.0,
                    thickness=stack_cfg.si_thickness_um,
                    material="si",
                    mesh_order=3,
                ),
                "n_active": LayerLevel(
                    layer=LAYER.N,
                    zmin=0.0,
                    thickness=stack_cfg.si_thickness_um,
                    material="si",
                    mesh_order=3,
                ),
                "p_contact": LayerLevel(
                    layer=LAYER.PPP,
                    zmin=0.0,
                    thickness=stack_cfg.si_thickness_um,
                    material="si",
                    mesh_order=4,
                ),
                "n_contact": LayerLevel(
                    layer=LAYER.NPP,
                    zmin=0.0,
                    thickness=stack_cfg.si_thickness_um,
                    material="si",
                    mesh_order=4,
                ),
            }
        )
    xs = xs_phase_shifter(ps_cfg)
    component = gf.components.straight(length=10, cross_section=xs)
    x_mid = component.xsize / 2
    xsection_bounds = [
        [x_mid, component.dbbox().bottom],
        [x_mid, component.dbbox().top],
    ]

    modes = compute_component_slice_modes(
        component=component,
        xsection_bounds=xsection_bounds,
        layer_stack=layer_stack,
        wavelength=wavelength_um,
        num_modes=num_modes,
        order=2,
        wafer_padding=2.0,
    )

    neff = [complex(m.n_eff) for m in modes.modes]
    return OpticalModeResult(neff=neff, raw=modes)
