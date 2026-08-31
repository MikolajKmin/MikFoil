from mikfoil.case import Case
from mikfoil.validation.xfoil import run_xfoil, read_XFOIL_surface_data, read_xfoil_coefficients
from mikfoil.validation.experimental import read_experimental_surface_data
from mikfoil.data_management.surface_data import add_surface_data
from mikfoil.postprocessing.comparison_plots import plot_cp_comparison, plot_cf_comparison

def perform_validation(case: Case) -> None:
    run_xfoil(case)

    if case.results.xfoil_converged:
        xfoil_df = read_XFOIL_surface_data(case)
        add_surface_data(case, xfoil_df)
            
    if case.experimental_data_file:
        validation_df = read_experimental_surface_data(case)
        add_surface_data(case, validation_df)

    plot_cp_comparison(case)
    plot_cf_comparison(case)
