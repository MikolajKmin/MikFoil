import numpy as np
from mikfoil.case import MeshConfig
from mikfoil.geometry.geometry_types import AirfoilGeometry
from mikfoil.meshing.mesh_types import Mesh
from .structured_grid import build_structured_c_grid

def generate_mesh(airfoil_geometry: AirfoilGeometry, config: MeshConfig) -> Mesh:
    upper_reversed = airfoil_geometry.upper_surface[::-1]
    combined_points = np.vstack([upper_reversed, airfoil_geometry.lower_surface[1:]])
    
    mesh = build_structured_c_grid(
        airfoil_points=combined_points,
        config=config,
        initial_height=config.first_layer_height,
        growth_rate=config.radial_growth_rate
    )
    
    return mesh
