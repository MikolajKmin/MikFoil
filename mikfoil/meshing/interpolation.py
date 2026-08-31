import numpy as np
from scipy.interpolate import CubicHermiteSpline

def linear_splines(airfoil_points: np.ndarray, farfield_points: np.ndarray, spacing_t: np.ndarray) -> np.ndarray:
    """Interpolates a volume grid linearly between the airfoil and farfield boundaries."""
    w_airfoil = 1.0 - spacing_t
    w_farfield = spacing_t
    
    # i: point index along the curve
    # j: radial layer index
    # k: spatial coordinate (x, y)
    mesh_airfoil = np.einsum('j,ik->ijk', w_airfoil, airfoil_points)
    mesh_farfield = np.einsum('j,ik->ijk', w_farfield, farfield_points)
    
    return mesh_airfoil + mesh_farfield

def orthogonal_splines(airfoil_points: np.ndarray, farfield_points: np.ndarray, normals: np.ndarray, spacing_t: np.ndarray, distance_avg: float) -> np.ndarray:
    """Interpolates a volume grid using cubic Hermite splines to enforce orthogonality at the airfoil surface."""
    P0 = airfoil_points
    P1 = farfield_points
    M0 = normals * distance_avg
    M1 = farfield_points - airfoil_points
    
    spline = CubicHermiteSpline(x=[0, 1], y=np.stack([P0, P1]), dydx=np.stack([M0, M1]), axis=0)
    return spline(spacing_t).transpose(1, 0, 2)
