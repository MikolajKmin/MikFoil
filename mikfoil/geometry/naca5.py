import numpy as np
from typing import Tuple

NACA5_PARAMS = {
    (2, 0): (0.0580, 361.400, 0.0),
    (3, 0): (0.2025, 15.957, 0.0),
    (4, 0): (0.2900, 3.230, 0.0),
    (5, 0): (0.3814, 1.229, 0.0),
    (2, 1): (0.1300, 51.640, 0.000764),
    (3, 1): (0.2680, 32.020, 0.04075),
    (4, 1): (0.3814, 15.520, 0.1009),
    (5, 1): (0.4855, 8.647, 0.1584),
}


def get_naca5_constants(p_val: int, q_val: int, lift_coefficient: int) -> Tuple[float, float, float]:
    r_const, k1_base, k2_k1_ratio = NACA5_PARAMS[(p_val, q_val)]
    lift_scale = lift_coefficient / 2.0
    k1_scaled = k1_base * lift_scale

    return r_const, k1_scaled, k2_k1_ratio


def compute_naca5_camber(r_const: float, k1_const: float, k2_k1_ratio: float, q_val: int, chord: float,
                         x_coordinates: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    x_normalized = x_coordinates / chord
    y_camber = np.zeros_like(x_coordinates)
    camber_slope = np.zeros_like(x_coordinates)

    front_mask = x_normalized < r_const
    back_mask = x_normalized >= r_const

    xf = x_normalized[front_mask]
    xb = x_normalized[back_mask]

    if q_val == 0:
        y_camber[front_mask] = (k1_const / 6.0) * (xf**3 - 3.0 * r_const * xf**2 + (r_const**2) * (3.0 - r_const) * xf)
        camber_slope[front_mask] = (k1_const / 6.0) * (3.0 * xf**2 - 6.0 * r_const * xf + (r_const**2) * (3.0 - r_const))
        
        y_camber[back_mask] = (k1_const * r_const**3 / 6.0) * (1.0 - xb)
        camber_slope[back_mask] = -(k1_const * r_const**3 / 6.0)

    elif q_val == 1:
        y_camber[front_mask] = (k1_const / 6.0) * ((xf - r_const)**3 - k2_k1_ratio * (1.0 - r_const)**3 * xf - r_const**3 * xf + r_const**3)
        camber_slope[front_mask] = (k1_const / 6.0) * (3.0 * (xf - r_const)**2 - k2_k1_ratio * (1.0 - r_const)**3 - r_const**3)
        
        y_camber[back_mask] = (k1_const / 6.0) * (k2_k1_ratio * (xb - r_const)**3 - k2_k1_ratio * (1.0 - r_const)**3 * xb - r_const**3 * xb + r_const**3)
        camber_slope[back_mask] = (k1_const / 6.0) * (3.0 * k2_k1_ratio * (xb - r_const)**2 - k2_k1_ratio * (1.0 - r_const)**3 - r_const**3)

    return y_camber * chord, camber_slope
