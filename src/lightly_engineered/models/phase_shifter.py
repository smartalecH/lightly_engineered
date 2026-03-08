from dataclasses import dataclass
import numpy as np


@dataclass
class PhaseShifterCompact:
    wavelength_um: float
    length_um: float
    voltage_grid: np.ndarray
    neff_grid: np.ndarray
    loss_grid_db_per_cm: np.ndarray
    c_per_m: float
    r_per_m: float

    def neff(self, v: float) -> complex:
        re = np.interp(v, self.voltage_grid, np.real(self.neff_grid))
        im = np.interp(v, self.voltage_grid, np.imag(self.neff_grid))
        return re + 1j * im

    def delta_phase(self, v: float, vref: float = 0.0) -> float:
        dneff = np.real(self.neff(v) - self.neff(vref))
        return 2 * np.pi * dneff * self.length_um / self.wavelength_um
