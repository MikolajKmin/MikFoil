import numpy as np
from typing import Tuple


def compute_naca4_camber(max_camber: float, camber_pos: float, chord: float, x_coordinates: np.ndarray) -> Tuple[
    np.ndarray, np.ndarray]:
    y_camber = np.zeros_like(x_coordinates)
    camber_slope = np.zeros_like(x_coordinates)

    front_mask = x_coordinates < (camber_pos * chord)
    back_mask = x_coordinates >= (camber_pos * chord)
    x_normalized = x_coordinates / chord

    # Guard against division by zero when camber_pos is zero (symmetric airfoil)
    if camber_pos != 0:
        xf = x_normalized[front_mask]
        y_camber[front_mask] = (max_camber / camber_pos**2) * (2.0 * camber_pos * xf - xf**2) * chord
        camber_slope[front_mask] = (2.0 * max_camber / camber_pos**2) * (camber_pos - xf)

        xb = x_normalized[back_mask]
        y_camber[back_mask] = (max_camber / (1.0 - camber_pos)**2) * ((1.0 - 2.0 * camber_pos) + 2.0 * camber_pos * xb - xb**2) * chord
        camber_slope[back_mask] = (2.0 * max_camber / (1.0 - camber_pos)**2) * (camber_pos - xb)

    return y_camber, camber_slope
