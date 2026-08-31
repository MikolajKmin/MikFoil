import pandas as pd

from mikfoil.case import Case


def read_history_data(case: Case) -> pd.DataFrame:
    file_path = case.su2_dir / "history.csv"
    history_df = pd.read_csv(file_path)
    history_df.columns = history_df.columns.str.strip(' "')

    return history_df


def extract_aero_coefficients(case: Case) -> tuple[float, float, float]:
    history_df = read_history_data(case)
    last_iteration = history_df.iloc[-1]

    lift = float(last_iteration["CL"])
    drag = float(last_iteration["CD"])
    moment = float(last_iteration["CMz"])

    return lift, drag, moment
