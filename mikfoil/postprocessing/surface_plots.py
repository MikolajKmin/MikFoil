import matplotlib.pyplot as plt
import pyvista as pv
import pandas as pd
import numpy as np

from mikfoil.case import Case
from mikfoil.data_management.surface_data import load_surface_data


def plot_cp(case: Case) -> None:
    x_upper = load_surface_data(case, source="SU2", surface="upper", variable="x")
    cp_upper = load_surface_data(case, source="SU2", surface="upper", variable="cp")

    x_lower = load_surface_data(case, source="SU2", surface="lower", variable="x")
    cp_lower = load_surface_data(case, source="SU2", surface="lower", variable="cp")

    figure, graph = plt.subplots()

    graph.plot(x_upper, cp_upper, label="Upper Surface")
    graph.plot(x_lower, cp_lower, label="Lower Surface")

    graph.set_xlabel("x/c")
    graph.set_ylabel("$C_p$")
    graph.invert_yaxis()
    graph.grid()
    graph.legend()

    title = f"Pressure Coefficient | {case.name}"
    graph.set_title(title)

    figure.savefig(case.plots_dir / "cp.png")
    plt.close(figure)


def plot_cf(case: Case) -> None:
    x_upper = load_surface_data(case, source="SU2", surface="upper", variable="x")
    cf_upper = load_surface_data(case, source="SU2", surface="upper", variable="cf")

    x_lower = load_surface_data(case, source="SU2", surface="lower", variable="x")
    cf_lower = load_surface_data(case, source="SU2", surface="lower", variable="cf")

    figure, ax = plt.subplots()

    ax.plot(x_upper, cf_upper, label="Upper Surface")
    ax.plot(x_lower, cf_lower, label="Lower Surface")

    ax.axhline(0, color="black")
    ax.set_xlabel("x/c")
    ax.set_ylabel("$C_f$")
    ax.grid()
    ax.legend()

    title = f"Skin Friction | {case.name}"
    ax.set_title(title)

    figure.savefig(case.plots_dir / "cf.png")
    plt.close(figure)


def plot_yplus(case: Case) -> None:
    x_upper = load_surface_data(case, source="SU2", surface="upper", variable="x")
    yplus_upper = load_surface_data(case, source="SU2", surface="upper", variable="yplus")

    x_lower = load_surface_data(case, source="SU2", surface="lower", variable="x")
    yplus_lower = load_surface_data(case, source="SU2", surface="lower", variable="yplus")

    figure, ax = plt.subplots()

    ax.plot(x_upper, yplus_upper, label="Upper Surface")
    ax.plot(x_lower, yplus_lower, label="Lower Surface")

    ax.set_xlabel("x/c")
    ax.set_ylabel("$y^+$")
    ax.grid()
    ax.legend()

    title = f"Y-Plus \n {case.name}"
    ax.set_title(title)

    figure.savefig(case.plots_dir / "yplus.png")
    plt.close(figure)

def plot_lm_gamma(case: Case) -> None:
    file_path = case.dir / "surface_data.csv"
    if not file_path.exists() or "LM_gamma" not in pd.read_csv(file_path, nrows=0).columns:
        return

    x_upper = load_surface_data(case, source="SU2", surface="upper", variable="x")
    lm_gamma_upper = load_surface_data(case, source="SU2", surface="upper", variable="LM_gamma")

    x_lower = load_surface_data(case, source="SU2", surface="lower", variable="x")
    lm_gamma_lower = load_surface_data(case, source="SU2", surface="lower", variable="LM_gamma")

    figure, ax = plt.subplots()

    ax.plot(x_upper, lm_gamma_upper, label="Upper Surface")
    ax.plot(x_lower, lm_gamma_lower, label="Lower Surface")

    ax.set_xlabel("x/c")
    ax.set_ylabel(r"$\gamma$")
    ax.grid()
    ax.legend()

    title = rf"LM $\gamma$ \n {case.name}"
    ax.set_title(title)

    figure.savefig(case.plots_dir / "lm_gamma.png")
    plt.close(figure)
