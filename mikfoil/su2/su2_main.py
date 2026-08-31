import os
import shutil
import subprocess
import time
from mikfoil.case import Case
from mikfoil.su2.restart_selection import get_best_restart_file
from mikfoil.su2.config_generation import generate_su2_config

def run_cfd(case: Case) -> None:
    """Executes the SU2 solver via CLI and logs the output, using available restart flowfields if applicable."""
    case.results.load_from_yaml(case.dir)
    if case.results.success:
        return
        
    best_restart_file = get_best_restart_file(case)
    if best_restart_file:
        case.restart = True
        shutil.copy2(best_restart_file, case.su2_dir / "restart.dat")
    else:
        case.restart = False

    # Generate configuration using the dynamic template renderer
    final_config_str = generate_su2_config(case)
    case.write_config(final_config_str)
    
    su2_path = os.getenv("SU2_CFD_PATH") or shutil.which("SU2_CFD")
    if not su2_path and os.getenv("SU2_RUN"):
        su2_path = shutil.which("SU2_CFD", path=os.getenv("SU2_RUN"))

    if not su2_path:
        raise FileNotFoundError('SU2_CFD executable not found. Please set the SU2_CFD_PATH or SU2_RUN environment variable or add it to your system PATH.')
        
    log_path = case.su2_dir / 'su2_log.txt'
    start_time = time.time()
    
    with open(log_path, 'w') as log_file:
        subprocess.run(
            [su2_path, 'config.cfg'],
            cwd=str(case.su2_dir),
            check=True,
            stdout=log_file,
            stderr=subprocess.STDOUT
        )
        
    simulation_time = time.time() - start_time
    case.results.success = True
    case.results.execution_time = simulation_time
