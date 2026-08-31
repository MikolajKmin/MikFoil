from pathlib import Path
from typing import List

from mikfoil.case import Case, MeshConfig

def create_validation_cases(aspire_folder: Path) -> List[Case]:
    """Looks through a folder for all .csv files satisfying naming convention of aspire airfoil cases"""
    cases = []
    aspire_files = aspire_folder.rglob("*.csv")

    for aspire_file in aspire_files:
        if "coordinates" in aspire_file.stem:
            continue
        case = read_validation_case(aspire_file)
        cases.append(case)
    return cases

def read_validation_case(aspire_file: Path) -> Case:
    """Parses an experimental Aspire CSV file to generate a Case object."""
    file_stem = aspire_file.stem

    airfoil, remaining = file_stem.split("_A", maxsplit=1)
    airfoil = airfoil.replace(" ", "_")
    aoa, remaining = remaining.split("_M", maxsplit=1)
    aoa = aoa.replace("m", "-")
    mach, remaining = remaining.split("_Re", maxsplit=1)
    reynolds = remaining.split("_", maxsplit=1)[0]

    mesh_config = MeshConfig()

    case = Case(
        airfoil=airfoil,
        aoa=float(aoa),
        mach=float(mach),
        reynolds=float(reynolds),
        experimental_data_file=aspire_file.resolve(),
        mesh_config=mesh_config,
    )

    return case