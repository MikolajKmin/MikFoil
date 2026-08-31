import numpy as np
from mikfoil.geometry.geometry_types import AirfoilGeometry
from mikfoil.case import MeshConfig
from mikfoil.meshing.airfoil_normals import get_airfoil_normals
from mikfoil.meshing.farfield_mesh import build_farfield_curve
from mikfoil.meshing.mesh_math import smooth_geometric_spacing
from mikfoil.meshing.interpolation import orthogonal_splines
import math
import pyvista as pv


pv.set_jupyter_backend('static')
def plot_growth_vectors(geom: AirfoilGeometry):
    """Plots growth vectors (normals) used to extrude the mesh."""
    points = np.vstack([geom.upper_surface[::-1], geom.lower_surface[1:]])
    chord = np.max(points[:, 0]) - np.min(points[:, 0])
    normals = get_airfoil_normals(points, chord)
    
    # Weight used for blending (from leading edge = 0 to trailing edge = 1)
    weights = np.clip((points[:, 0] - np.min(points[:, 0])) / chord, 0.0, 1.0) ** 2.0
    
    points_3d = np.column_stack((points[:, 0], points[:, 1], np.zeros(len(points))))
    normals_3d = np.column_stack((normals[:, 0], normals[:, 1], np.zeros(len(normals))))
    
    cloud = pv.PolyData(points_3d)
    cloud['normals'] = normals_3d
    cloud['Blending Weight'] = weights
    
    arrows = cloud.glyph(orient='normals', scale=False, factor=0.07)
    
    af_poly = pv.PolyData(points_3d)
    af_poly.lines = np.hstack([[len(points)]] + list(range(len(points))))
    
    plotter = pv.Plotter(notebook=True)
    plotter.enable_2d_style()
    plotter.enable_parallel_projection()
    
    plotter.add_mesh(af_poly, color='black', line_width=2, lighting=False)
    plotter.add_mesh(arrows, scalars='Blending Weight', cmap='viridis', lighting=False)
    
    plotter.view_xy()
    plotter.show()

def calculate_first_layer_height(y_plus: float, reynolds: float, chord: float):
    """Estimates absolute first cell layer height using Schlichting's empirical correlation."""
    
    # Schlichting's empirical correlation for Cf
    Cf = math.pow(2.0 * math.log10(reynolds) - 0.65, -2.3)
    
    # Calculate height from inverted y+ definition
    height = y_plus / (reynolds * math.sqrt(Cf / 2.0)) * chord
    
    print(f"Target y+: {y_plus}")
    print(f"Reynolds Number: {reynolds:.1e}")
    print(f"Computed Skin Friction (Cf): {Cf:.6f}")
    print(f"Computed First Layer Height: {height:.6f} meters")

def plot_boundary_points(geom: AirfoilGeometry, config: MeshConfig):
    """Plots the outer boundary domain."""
    points = np.vstack([geom.upper_surface[::-1], geom.lower_surface[1:]])
    x_te = np.max(points[:, 0])
    x_le = np.min(points[:, 0])
    x_ac = x_le + 0.25 * config.chord
    
    le_idx = np.argmin(points[:, 0])
    N_upper = le_idx + 1
    N_lower = len(points) - le_idx
    
    farfield = build_farfield_curve(x_te, x_ac, config.domain_radius, N_upper, N_lower)
    
    af_cloud = pv.PolyData(np.column_stack((points[:, 0], points[:, 1], np.zeros_like(points[:, 0]))))
    ff_cloud = pv.PolyData(np.column_stack((farfield[:, 0], farfield[:, 1], np.zeros_like(farfield[:, 0]))))
    
    plotter = pv.Plotter(notebook=True)
    plotter.enable_2d_style()
    plotter.enable_parallel_projection()
    
    plotter.add_points(af_cloud, color='black', point_size=8, render_points_as_spheres=True, lighting=False)
    plotter.add_points(ff_cloud, color='red', point_size=8, render_points_as_spheres=True, lighting=False)
    
    plotter.view_xy()
    plotter.show()

def plot_orthogonal_splines(geom: AirfoilGeometry, config: MeshConfig):
    """Plots radial splines connecting the airfoil to the boundary."""
    points = np.vstack([geom.upper_surface[::-1], geom.lower_surface[1:]])
    chord = config.chord
    
    x_te = np.max(points[:, 0])
    x_le = np.min(points[:, 0])
    x_ac = x_le + 0.25 * chord
    
    le_idx = np.argmin(points[:, 0])
    N_upper = le_idx + 1
    N_lower = len(points) - le_idx
    
    normals = get_airfoil_normals(points, chord)
    
    farfield = build_farfield_curve(x_te, x_ac, config.domain_radius, N_upper, N_lower)
    

    D_vec = farfield - points
    D_avg = np.mean(np.linalg.norm(D_vec, axis=1))
    
    s_tangent = np.mean(np.linalg.norm(np.diff(farfield, axis=0), axis=1))
    
    t = smooth_geometric_spacing(config.first_layer_height, s_tangent, D_avg)
    
    if getattr(config, "use_normals", True):
        front_mesh = orthogonal_splines(points, farfield, normals, t, D_avg)
    else:
        from mikfoil.meshing.interpolation import linear_splines
        front_mesh = linear_splines(points, farfield, t)
                  
    plotter = pv.Plotter(notebook=True)
    plotter.enable_2d_style()
    plotter.enable_parallel_projection()
    
    points_3d = np.column_stack((points[:, 0], points[:, 1], np.zeros(len(points))))
    farfield_3d = np.column_stack((farfield[:, 0], farfield[:, 1], np.zeros(len(farfield))))
    
    af_poly = pv.PolyData(points_3d)
    af_poly.lines = np.hstack([[len(points)]] + list(range(len(points))))
    
    ff_poly = pv.PolyData(farfield_3d)
    ff_poly.lines = np.hstack([[len(farfield)]] + list(range(len(farfield))))
    
    plotter.add_mesh(af_poly, color='black', line_width=2, lighting=False)
    plotter.add_mesh(ff_poly, color='red', line_width=2, lighting=False)
    
    all_spline_points = []
    lines_array = []
    pt_idx = 0
    num_t = front_mesh.shape[1]
    
    for i in range(0, len(points), 4):
        spline_pts = front_mesh[i, :, :]
        pts_3d = np.column_stack((spline_pts[:, 0], spline_pts[:, 1], np.zeros(num_t)))
        all_spline_points.append(pts_3d)
        lines_array.extend([num_t] + list(range(pt_idx, pt_idx + num_t)))
        pt_idx += num_t
        
    splines_poly = pv.PolyData(np.vstack(all_spline_points))
    splines_poly.lines = np.array(lines_array)
    plotter.add_mesh(splines_poly, color='gray', line_width=1, opacity=0.7, lighting=False)
    
    plotter.view_xy()
    plotter.show()



plot_mesh_splines = plot_orthogonal_splines
