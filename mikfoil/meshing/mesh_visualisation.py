import pyvista as pv
import numpy as np
from pathlib import Path
from mikfoil.meshing.mesh_types import Mesh

def _create_structured_pv_grid(grid: Mesh) -> pv.StructuredGrid:

    pts = grid.points
    x = pts[:, :, 0]
    y = pts[:, :, 1]
    z = np.zeros_like(x)
    return pv.StructuredGrid(x, y, z)

def visualize_mesh_interactive(grid: Mesh) -> None:
    """Opens an interactive mesh GUI."""
    structured = _create_structured_pv_grid(grid)
    
    pv.set_jupyter_backend('trame')
        
    plotter = pv.Plotter()
    plotter.enable_2d_style()
    plotter.enable_parallel_projection()
    plotter.add_mesh(structured, show_edges=True, color="white", edge_color="black", line_width=0.5, lighting=False)
    plotter.view_xy()
    # plotter.add_title("Generated Mesh")
    plotter.show()

def export_mesh_plot_near(grid: Mesh, out_path: str | Path) -> None:
    """Exports a PNG of the near-field mesh."""
    structured = _create_structured_pv_grid(grid)
    
    mesh_viewer = pv.Plotter(off_screen=True)
    mesh_viewer.add_mesh(structured, show_edges=True, color="white", edge_color="black", line_width=0.5)
    mesh_viewer.view_xy()
    mesh_viewer.camera.position = (0.5, 0.0, 3.5)
    mesh_viewer.camera.focal_point = (0.5, 0.0, 0.0)
    mesh_viewer.screenshot(str(out_path))
    mesh_viewer.close()

def export_mesh_plot_far(grid: Mesh, out_path: str | Path) -> None:
    """Exports a PNG of the far-field mesh."""
    structured = _create_structured_pv_grid(grid)
    
    mesh_viewer = pv.Plotter(off_screen=True)
    mesh_viewer.add_mesh(structured, show_edges=True, color="white", edge_color="black", line_width=0.5)
    mesh_viewer.view_xy()
    mesh_viewer.camera.position = (0.5, 0.0, 40.0)
    mesh_viewer.camera.focal_point = (0.5, 0.0, 0.0)
    mesh_viewer.screenshot(str(out_path))
    mesh_viewer.close()
