from mikfoil.case import Case
import pyvista as pv
import numpy as np



def create_contours(case: Case) -> None:
    vtu_path = case.su2_dir / "volume.vtu"
    if not vtu_path.exists():
        return
        
    volume_mesh = pv.read(str(vtu_path))
    bounds = [-0.5, 1.5, -0.5, 0.5, -1.0, 1.0]
    near_field = volume_mesh.clip_box(bounds, invert=False)

    scalars_to_plot = [
        "Mach", 
        "Pressure", 
        "Eddy_Viscosity", 
        "LM_gamma", 
        "LM_gamma_eff", 
        "LM_gamma_sep", 
        "Turb_Kin_Energy"
    ]

    mesh_viewer = pv.Plotter(off_screen=True)
    for scalar in scalars_to_plot:
        if scalar in volume_mesh.array_names:
            mesh_viewer.clear()
            mesh_viewer.add_mesh(near_field, scalars=scalar, cmap="jet", show_edges=False)
            mesh_viewer.view_xy()
            mesh_viewer.screenshot(case.contours_dir / f"contour_{scalar.lower()}.png")
    mesh_viewer.close()
    pv.close_all()



