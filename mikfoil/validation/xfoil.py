import subprocess
from pathlib import Path
import os
import shutil
import pandas as pd
import numpy as np

from mikfoil.case import Case
from mikfoil.data_management.surface_data import _split_surface_data

from jinja2 import Environment, FileSystemLoader

def run_xfoil(case: Case) -> None:
    XFOIL_EXECUTABLE = os.environ.get("XFOIL_PATH") or shutil.which("xfoil")
    if not XFOIL_EXECUTABLE:
        raise FileNotFoundError("xfoil executable not found. Please set the XFOIL_PATH environment variable or add it to your system PATH.")
        
    commands = _generate_xfoil_commands(case)
    xfoil_log_file = case.validation_dir / "xfoil_log.txt"
    with open(xfoil_log_file, "w") as log_file:
        subprocess.run([XFOIL_EXECUTABLE], input=commands.encode(), cwd=case.validation_dir, stdout=log_file, stderr=subprocess.STDOUT)

    check_xfoil_convergence(case)

def _generate_xfoil_commands(case: Case) -> str:
    dat_file = case.dir / f"{case.airfoil_name}.dat"
    local_dat = case.validation_dir / f"{case.airfoil_name}.dat"
    if dat_file.exists():
        shutil.copy(str(dat_file), str(local_dat))
        
    core_file = Path(__file__).parent / "core_configs" / f"{case.xfoil_config}.xfoil"
    target_path = core_file if core_file.exists() else (case.project_dir / case.xfoil_config)
    
    env = Environment(loader=FileSystemLoader(str(target_path.parent)))
    template = env.get_template(target_path.name)
    
    return template.render(case=case)


def read_XFOIL_surface_data(case: Case) -> pd.DataFrame:
    WHITESPACE_SEPARATOR: str = r"\s+"
    cp_path = case.validation_dir / "xfoil_cp.txt"
    dump_path = case.validation_dir / "xfoil_dump.txt"

    surface_data = pd.read_csv(cp_path, sep=WHITESPACE_SEPARATOR, skiprows=3, names=["x", "y", "cp"])
    dump_data = pd.read_csv(dump_path, sep=WHITESPACE_SEPARATOR, skiprows=1, usecols=[6], names=["cf"])
    
    surface_data["cf"] = dump_data["cf"]

    surface_data["yplus"] = np.nan
    surface_data["source"] = "xfoil"

    surface_data = _split_surface_data(surface_data)
    surface_data = surface_data[["x", "y", "cp", "yplus", "cf", "source", "surface"]]

    return surface_data

def check_xfoil_convergence(case: Case) -> None:
    polar_path = case.validation_dir / "xfoil_polar.txt"
    if polar_path.exists() and polar_path.stat().st_size > 50:
        case.results.xfoil_converged = True
    else:
        case.results.xfoil_converged = False


def read_xfoil_coefficients(case: Case) -> dict:
    polar_path = case.validation_dir / "xfoil_polar.txt"

    with open(polar_path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    data_line = lines[-1].split()

    return {
        "xfoil_CL": float(data_line[1]), 
        "xfoil_CD": float(data_line[2]),
        "xfoil_CM": float(data_line[4]), 
        "xfoil_top_Xtr": float(data_line[5]), 
        "xfoil_bot_Xtr": float(data_line[6])
    }
