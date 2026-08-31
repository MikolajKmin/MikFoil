import shutil
from pathlib import Path

from mikfoil.case import Case
from mikfoil.data_management.history_data import extract_aero_coefficients
from mikfoil.data_management.surface_data import read_SU2_surface_data, save_surface_data
from mikfoil.postprocessing.history_plots import plot_convergence
from mikfoil.postprocessing.surface_plots import plot_cp, plot_cf, plot_yplus, plot_lm_gamma
from mikfoil.postprocessing.contour_plots import create_contours
from mikfoil.postprocessing.transition_metrics import calculate_transition_and_separation
from mikfoil.postprocessing.comparison_plots import plot_cp_comparison, plot_cf_comparison

from mikfoil.geometry.geometry_main import create_airfoil
from mikfoil.geometry.selig_format import export_selig_dat

from mikfoil.meshing.meshing_main import generate_mesh
from mikfoil.meshing.mesh_math import first_layer_from_yplus
from mikfoil.meshing.mesh_metrics import compute_mesh_metrics
from mikfoil.meshing.su2_format import export_su2_mesh
from mikfoil.meshing.mesh_visualisation import export_mesh_plot_near, export_mesh_plot_far

from mikfoil.su2.su2_main import run_cfd
from mikfoil.validation.validation_main import perform_validation
from mikfoil.validation.xfoil import read_xfoil_coefficients


def generate_mesh_from_case(case: Case) -> None:
    if case.target_y_plus is not None:
        case.mesh_config.first_layer_height = first_layer_from_yplus(
            case.reynolds, 
            case.target_y_plus, 
            case.mesh_config.chord
        )
    
    geom = create_airfoil(case.airfoil, case.mesh_config)

    if isinstance(case.airfoil, Path):
        shutil.copy2(case.airfoil, case.dir / f"{case.airfoil_name}.dat")
    else:
        export_selig_dat(geom, case.airfoil_name, case.dir / f"{case.airfoil_name}.dat")
        
    mesh = generate_mesh(geom, case.mesh_config)
    
    export_su2_mesh(mesh, str(case.mesh_path))
    export_mesh_plot_near(mesh, case.contours_dir / "mesh_near.png")
    export_mesh_plot_far(mesh, case.contours_dir / "mesh_far.png")
    
    metrics = compute_mesh_metrics(mesh)
    case.results.mesh_number_of_cells = metrics["total_cells"]
    case.results.mesh_min_angle = metrics["min_angle"]
    case.results.mesh_max_skewness = metrics["max_skewness"]
    case.results.save_to_yaml(case.dir)


def execute_case(case: Case) -> None:
    case.setup()
    case.results.load_from_yaml(case.dir)
    
    if not case.results.success and not case.restart:
        generate_mesh_from_case(case)

    run_cfd(case)

    if not case.results.success:
        return

    save_results(case)
    perform_validation(case)

    create_plots(case)
    create_contours(case)
    compile_case_data(case)


def save_results(case: Case) -> None:
    su2_surface_df = read_SU2_surface_data(case)
    save_surface_data(case, su2_surface_df)


def create_plots(case: Case) -> None:
    plot_cp(case)
    plot_cf(case)
    plot_yplus(case)
    plot_lm_gamma(case)
    plot_convergence(case)
    plot_cp_comparison(case)
    plot_cf_comparison(case)


def compile_case_data(case: Case) -> None:
    lift, drag, moment = extract_aero_coefficients(case)
    case.results.cl = lift
    case.results.cd = drag
    case.results.cm = moment

    if case.results.xfoil_converged:
        xfoil_results = read_xfoil_coefficients(case)
        if xfoil_results and xfoil_results.get("xfoil_CL") != "No data":
            case.results.xfoil_cl = xfoil_results.get("xfoil_CL")
            case.results.xfoil_cd = xfoil_results.get("xfoil_CD")
            case.results.xfoil_cm = xfoil_results.get("xfoil_CM")

    transition_data = calculate_transition_and_separation(case)
    if transition_data:
        case.results.upper_transition_x = transition_data.get("transition_upper_x")
        case.results.upper_separation_x = transition_data.get("separation_upper_x")

    case.results.save_to_yaml(case.dir)
