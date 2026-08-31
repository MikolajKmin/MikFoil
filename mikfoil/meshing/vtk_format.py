import numpy as np
import pyvista as pv
from pathlib import Path
from mikfoil.meshing.mesh_types import Mesh

def export_vtk_mesh(grid: Mesh, filepath: str | Path) -> None:
    points_3d = grid.points
    x = points_3d[:, :, 0]
    y = points_3d[:, :, 1]
    z = np.zeros_like(x)
    
    structured = pv.StructuredGrid(x, y, z)
    structured.save(str(filepath))
