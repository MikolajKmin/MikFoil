from dataclasses import dataclass
import numpy as np



@dataclass(frozen=True)
class AirfoilGeometry:
    upper_surface: np.ndarray
    lower_surface: np.ndarray
    chord: float  # [m]
