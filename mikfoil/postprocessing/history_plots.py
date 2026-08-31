import pandas as pd
from matplotlib import pyplot as plt

from mikfoil.data_management.history_data import read_history_data
from mikfoil.case import Case


def plot_convergence(case: Case) -> None:
    history_df = read_history_data(case)
    iterations = history_df["Inner_Iter"]
    lift = history_df["CL"]
    drag = history_df["CD"]

    figure, lift_axis = plt.subplots()

    lift_axis.plot(iterations, lift, color="tab:blue")
    lift_axis.set_yscale("symlog", linthresh=0.1)
    lift_axis.set_xlabel("Iterations")
    lift_axis.set_ylabel("Lift Coefficient ($C_L$)", color="tab:blue")
    lift_axis.tick_params(axis="y", labelcolor="tab:blue")
    lift_axis.grid()

    drag_axis = lift_axis.twinx()
    drag_axis.plot(iterations, drag, color="tab:red")
    drag_axis.set_yscale("symlog", linthresh=0.001)
    drag_axis.set_ylabel("Drag Coefficient ($C_D$)", color="tab:red")
    drag_axis.tick_params(axis="y", labelcolor="tab:red")

    title = f"Aerodynamic Convergence | {case.name}"
    lift_axis.set_title(title)

    figure.tight_layout()
    figure.savefig(case.plots_dir / "convergence.png")
    plt.close(figure)
