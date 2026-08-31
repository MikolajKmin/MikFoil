import matplotlib.pyplot as plt

from mikfoil.case import Case
from mikfoil.data_management.surface_data import load_surface_data


def plot_cp_comparison(case: Case) -> None:
    x_su2 = load_surface_data(case, source="SU2", surface="upper", variable="x")
    cp_su2 = load_surface_data(case, source="SU2", surface="upper", variable="cp")

    x_xfoil = load_surface_data(case, source="xfoil", surface="upper", variable="x")
    cp_xfoil = load_surface_data(case, source="xfoil", surface="upper", variable="cp")

    x_exp = load_surface_data(case, source="EXPERIMENT", surface="upper", variable="x")
    cp_exp = load_surface_data(case, source="EXPERIMENT", surface="upper", variable="cp")

    fig, ax = plt.subplots()

    ax.plot(x_su2, cp_su2, label="SU2")

    if x_xfoil is not None and len(x_xfoil) > 0:
        ax.plot(x_xfoil, cp_xfoil, label="XFOIL", linestyle="--")

    if x_exp is not None and len(x_exp) > 0:
        ax.scatter(x_exp, cp_exp, label="Experiment", color="black", marker="o", facecolors="none")

    ax.set_xlabel("x/c")
    ax.set_ylabel(r"$C_p$")
    ax.invert_yaxis()
    ax.grid()
    ax.legend()

    title = f"Cp Comparison | {case.name}"
    ax.set_title(title)

    save_path = case.validation_dir / "Cp_validation.png"
    fig.savefig(save_path)
    plt.close(fig)




def plot_cf_comparison(case: Case) -> None:
    x_su2 = load_surface_data(case, source="SU2", surface="upper", variable="x")
    cf_su2 = load_surface_data(case, source="SU2", surface="upper", variable="cf")

    x_xfoil = load_surface_data(case, source="xfoil", surface="upper", variable="x")
    cf_xfoil = load_surface_data(case, source="xfoil", surface="upper", variable="cf")

    figure, graph = plt.subplots()

    graph.plot(x_su2, cf_su2, label="SU2")

    if x_xfoil is not None and len(x_xfoil) > 0:
        graph.plot(x_xfoil, cf_xfoil, label="XFOIL", linestyle="--")

    x_exp = load_surface_data(case, source="EXPERIMENT", surface="upper", variable="x")
    cf_exp = load_surface_data(case, source="EXPERIMENT", surface="upper", variable="cf")

    if x_exp is not None and len(x_exp) > 0:
        graph.scatter(x_exp, cf_exp, label="Experiment", color="black")

    graph.set_xlabel("x/c")
    graph.set_ylabel(r"$C_f$")
    graph.grid()
    graph.legend()

    title = f"Cf Comparison | {case.name}"
    graph.set_title(title)

    save_path = case.validation_dir / "Cf_validation.png"
    figure.savefig(save_path)
    plt.close(figure)



