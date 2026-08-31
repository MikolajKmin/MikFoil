import numpy as np
import scipy.interpolate as interp
from typing import Tuple

NACA_T0: float = 0.2969
NACA_T1: float = 0.1260
NACA_T2: float = 0.3516
NACA_T3: float = 0.2843
NACA_T4: float = 0.1036


def compute_thickness_distribution(thickness: float, chord: float, x_coordinates: np.ndarray) -> np.ndarray:
    x_normalized = x_coordinates / chord
    thickness_scale = 5.0 * thickness * chord

    term_0 = NACA_T0 * np.sqrt(x_normalized)
    term_1 = NACA_T1 * x_normalized
    term_2 = NACA_T2 * (x_normalized ** 2)
    term_3 = NACA_T3 * (x_normalized ** 3)
    term_4 = NACA_T4 * (x_normalized ** 4)

    poly_terms = term_0 - term_1 - term_2 + term_3 - term_4

    return thickness_scale * poly_terms


def build_surface_coordinates(x_coordinates: np.ndarray, y_camber: np.ndarray, thickness_distribution: np.ndarray,
                              theta: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    thickness_x = thickness_distribution * np.sin(theta)
    thickness_y = thickness_distribution * np.cos(theta)

    x_upper = x_coordinates - thickness_x
    y_upper = y_camber + thickness_y
    upper_surface = np.column_stack((x_upper, y_upper))

    x_lower = x_coordinates + thickness_x
    y_lower = y_camber - thickness_y
    lower_surface = np.column_stack((x_lower, y_lower))

    # Fix the heart-shaped cusp at the leading edge caused by camber line singularity at x=0
    idx_min_x = np.argmin(upper_surface[:, 0])
    if upper_surface[idx_min_x, 0] < 0.0 and idx_min_x > 0:
        true_le = upper_surface[idx_min_x].copy()
        # Remove the backwards-curving points that create the cleft
        upper_surface = upper_surface[idx_min_x:]
        # Close the lower surface to the true leading edge
        lower_surface[0] = true_le

    return upper_surface, lower_surface


def resample_curve_by_arc_length(curve_points: np.ndarray, config, fineness: float) -> np.ndarray:
    diffs = np.diff(curve_points, axis=0)
    segment_lengths = np.linalg.norm(diffs, axis=1)
    
    # Filter identical points so cumulative_length is strictly increasing (required for CubicSpline)
    unique_idx = np.concatenate(([True], segment_lengths > 1e-12))
    curve_points = curve_points[unique_idx]
    diffs = np.diff(curve_points, axis=0)
    segment_lengths = np.linalg.norm(diffs, axis=1)
    
    cumulative_length = np.zeros(len(curve_points))
    cumulative_length[1:] = np.cumsum(segment_lengths)
    
    total_length = cumulative_length[-1]
    
    if total_length == 0:
        return curve_points
        
    s_fine = np.linspace(0.0, total_length, 2000)
    
    s_le = config.s_le / fineness
    s_mid = config.s_mid / fineness
    s_te = config.s_te / fineness
    
    s_norm = s_fine / total_length
    
    # Vectorized computation of the density function using np.piecewise
    spacing = np.piecewise(
        s_norm,
        [s_norm < 0.2, s_norm > 0.8],
        [
            lambda s: (1.0 - (s / 0.2)) * s_le + (s / 0.2) * s_mid,
            lambda s: (1.0 - ((s - 0.8) / 0.2)) * s_mid + ((s - 0.8) / 0.2) * s_te,
            s_mid
        ]
    )
    
    density = 1.0 / spacing
    
    ds = s_fine[1] - s_fine[0]
    integral = np.cumsum(density) * ds
    integral -= integral[0]
    
    N_surface_points = int(np.round(integral[-1]))
    if N_surface_points < 10:
        N_surface_points = 10
        
    points = np.linspace(0.0, integral[-1], N_surface_points)
    target_lengths = np.interp(points, integral, s_fine)
    
    resampled = np.zeros((N_surface_points, 2))
    cs_x = interp.CubicSpline(cumulative_length, curve_points[:, 0])
    cs_y = interp.CubicSpline(cumulative_length, curve_points[:, 1])
    resampled[:, 0] = cs_x(target_lengths)
    resampled[:, 1] = cs_y(target_lengths)
    
    return resampled


