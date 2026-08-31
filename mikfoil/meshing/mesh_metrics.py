import numpy as np
import pyvista as pv
from mikfoil.meshing.mesh_types import Mesh

def compute_mesh_metrics(grid: Mesh) -> dict:
    """Computes cell count, minimum angle, and maximum skewness of the mesh."""
    pts = grid.points
    x = pts[:, :, 0]
    y = pts[:, :, 1]
    z = np.zeros_like(x)
    
    pv_grid = pv.StructuredGrid(x, y, z)
    
    min_angle = pv_grid.cell_quality(quality_measure='min_angle')['min_angle'].min()
    max_skew = pv_grid.cell_quality(quality_measure='skew')['skew'].max()
    
    return {
        'total_cells': int(pv_grid.n_cells),
        'min_angle': float(min_angle),
        'max_skewness': float(max_skew)
    }
