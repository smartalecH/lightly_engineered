from dataclasses import dataclass


@dataclass(frozen=True)
class StackConfig:
    si_thickness_um: float = 0.160
    slab_thickness_um: float = 0.050
    box_thickness_um: float = 2.0
    top_clad_thickness_um: float = 2.0


@dataclass(frozen=True)
class PhaseShifterConfig:
    rib_width_um: float = 0.45
    slab_width_um: float = 6.0
    active_width_um: float = 0.30
    active_gap_um: float = 0.00
    contact_offset_um: float = 1.20
    contact_width_um: float = 0.80

    p_active_cm3: float = 5e17
    n_active_cm3: float = 5e17
    p_access_cm3: float = 1e19
    n_access_cm3: float = 1e19
    p_contact_cm3: float = 1e20
    n_contact_cm3: float = 1e20


@dataclass(frozen=True)
class MZMConfig:
    wavelength_um: float = 1.31
    phase_shifter_length_um: float = 2000.0
    arm_spacing_um: float = 40.0
