import numpy as np
from mikfoil.meshing.mesh_types import Mesh
from mikfoil.case import MeshConfig

from .airfoil_normals import get_airfoil_normals
from .farfield_mesh import build_farfield_curve
from .mesh_math import smooth_geometric_spacing
from .interpolation import orthogonal_splines, linear_splines
from .wake import calculate_wake_x_positions, extrude_wake_meshes

def assemble_c_grid_blocks(front_mesh: np.ndarray, wake_upper_mesh: np.ndarray, wake_lower_mesh: np.ndarray) -> np.ndarray:
    return np.concatenate([wake_upper_mesh[1:][::-1], front_mesh, wake_lower_mesh[1:]], axis=0)

def _generate_radial_front_mesh(airfoil_points: np.ndarray, config: MeshConfig, initial_height: float) -> np.ndarray:
    chord = config.chord
    radius = config.domain_radius
    
    N_airfoil = len(airfoil_points)
    x_te = np.max(airfoil_points[:, 0])
    x_le = np.min(airfoil_points[:, 0])
    x_ac = x_le + 0.25 * chord
    
    le_idx = np.argmin(airfoil_points[:, 0])
    N_upper = le_idx + 1
    N_lower = N_airfoil - le_idx
    
    farfield_points = build_farfield_curve(x_te, x_ac, radius, N_upper, N_lower)
    
    D_vec = farfield_points - airfoil_points
    D_avg = float(np.mean(np.linalg.norm(D_vec, axis=1)))
    
    s_tangent = float(np.mean(np.linalg.norm(np.diff(farfield_points, axis=0), axis=1)))
    
    t = smooth_geometric_spacing(initial_height, s_tangent, D_avg)
    
    if getattr(config, "use_normals", True):
        normals = get_airfoil_normals(airfoil_points, chord)
        return orthogonal_splines(airfoil_points, farfield_points, normals, t, D_avg)
    else:
        return linear_splines(airfoil_points, farfield_points, t)

def _generate_wake_mesh(front_mesh: np.ndarray, config: MeshConfig, dx_te: float) -> tuple[np.ndarray, np.ndarray, int]:
    wake_length = config.wake_length
    
    wake_x_positions = calculate_wake_x_positions(wake_length, dx_te, config.wake_growth_rate)
    
    upper_te_line = front_mesh[0, :, :]
    lower_te_line = front_mesh[-1, :, :]
    
    wake_upper_mesh, wake_lower_mesh = extrude_wake_meshes(upper_te_line, lower_te_line, wake_x_positions)
    
    num_wake_pts = len(wake_x_positions)
    return wake_upper_mesh, wake_lower_mesh, num_wake_pts

def build_structured_c_grid(airfoil_points: np.ndarray, config: MeshConfig, initial_height: float, growth_rate: float) -> Mesh:
    N_airfoil = len(airfoil_points)
    
    front_mesh = _generate_radial_front_mesh(airfoil_points, config, initial_height)
    
    dx_te = float(np.linalg.norm(airfoil_points[0] - airfoil_points[1]))
    
    wake_upper_mesh, wake_lower_mesh, num_wake_pts = _generate_wake_mesh(front_mesh, config, dx_te)
    
    final_grid = assemble_c_grid_blocks(front_mesh, wake_upper_mesh, wake_lower_mesh)
    
    return Mesh(points=final_grid, num_wake_pts=num_wake_pts, num_airfoil_pts=N_airfoil)
