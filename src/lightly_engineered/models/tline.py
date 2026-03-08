from dataclasses import dataclass
import numpy as np


@dataclass
class RLGCLine:
    r_per_m: float
    l_per_m: float
    g_per_m: float
    c_per_m: float

    def gamma(self, omega: np.ndarray) -> np.ndarray:
        jw = 1j * omega
        return np.sqrt((self.r_per_m + jw * self.l_per_m) * (self.g_per_m + jw * self.c_per_m))

    def zc(self, omega: np.ndarray) -> np.ndarray:
        jw = 1j * omega
        return np.sqrt((self.r_per_m + jw * self.l_per_m) / (self.g_per_m + jw * self.c_per_m))
