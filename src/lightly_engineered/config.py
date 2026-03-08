from dataclasses import dataclass

'''
This is a "practical" photonics PDK based on what's publicly available for the 
GlobalFoundries 45CLO process. Not every parameter needed for a PDK is listed 
publicly, however, so reasonable parameters are used in those places (simply 
so the simulations and design also make sense).

The intent of this "pretend" PDK is to be educational, and to demonstrate 
what's feasable when one applies LLMs + open source tooling to design entire 
integrated photonic + electronic systems at scale.

If any value here closely resembles values not disclosed publicly, it's purely accidental.
'''


@dataclass(frozen=True)
class StackConfig:
    # Publication-grounded values from:
    # Rakowski et al., OFC 2020 (45CLO), "Platform Overview" section:
    # - 160 nm top silicon
    # - 2 um buried oxide
    # - partially etched 50 nm slab waveguides (KG)
    si_thickness_um: float = 0.160
    slab_thickness_um: float = 0.050
    box_thickness_um: float = 2.0
    # Modeling assumption:
    # Not specified in the paper; chosen as a practical oxide cladding height
    # for mode solving in this surrogate workflow.
    top_clad_thickness_um: float = 2.0


@dataclass(frozen=True)
class PhaseShifterConfig:
    # Geometry assumptions for a believable 45CLO-like depletion PN phase shifter.
    # These are not published as an exact foundry cross section in the cited paper.
    rib_width_um: float = 0.45
    slab_width_um: float = 6.0
    active_width_um: float = 0.30
    active_gap_um: float = 0.00
    contact_offset_um: float = 1.20
    contact_width_um: float = 0.80

    # Doping assumptions used for surrogate TCAD/electro-optic trends.
    # Not extracted from foundry signoff decks.
    p_active_cm3: float = 5e17
    n_active_cm3: float = 5e17
    p_access_cm3: float = 1e19
    n_access_cm3: float = 1e19
    p_contact_cm3: float = 1e20
    n_contact_cm3: float = 1e20


@dataclass(frozen=True)
class MZMConfig:
    # O-band default is aligned with the 45CLO publication statement that
    # devices operate in C and O bands.
    wavelength_um: float = 1.31
    # Device-length/layout values below are design choices for this tutorial.
    phase_shifter_length_um: float = 2000.0
    arm_spacing_um: float = 40.0
