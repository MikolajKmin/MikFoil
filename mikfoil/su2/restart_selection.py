import re
import shutil
from pathlib import Path
from mikfoil.case import Case

MAX_AOA_DIFF = 5.0

def _calculate_penalty(target_case: Case, file_aoa: float, file_mach: float, file_re: float) -> float | None:
    
    aoa_diff = abs(target_case.aoa - file_aoa)
    if aoa_diff > MAX_AOA_DIFF:
        return None
    aoa_penalty = aoa_diff * 100.0

    if target_case.mach > 0:
        mach_penalty = abs(target_case.mach - file_mach) / target_case.mach * 1000.0
    else:
        mach_penalty = 0

    if target_case.reynolds > 0:
        re_penalty = abs(target_case.reynolds - file_re) / target_case.reynolds * 100.0
    else:
        re_penalty = 0

    return aoa_penalty + mach_penalty + re_penalty

def get_best_restart_file(case: Case) -> Path | None:

    if not case.restart:
        return None
    
    cases_dir = case.project_dir / "cases"
    if not cases_dir.exists():
        return None
    
    best_file = None
    min_penalty = float('inf')
    pattern = re.compile(r'_AoA_([0-9\.\-]+)_M_([0-9\.\-]+)_Re_([0-9\.\-eE]+)')
    
    # We scan all case directories inside cases_dir
    for case_dir in cases_dir.iterdir():
        if not case_dir.is_dir():
            continue
            
        match = pattern.search(case_dir.name)
        if not match:
            continue
            
        # The restart file naturally lives in su2_dir / restart.dat
        file_path = case_dir / "su2" / "restart.dat"
        if not file_path.exists():
            continue
            
        file_aoa = float(match.group(1))
        file_mach = float(match.group(2))
        file_re = float(match.group(3))
        
        penalty = _calculate_penalty(case, file_aoa, file_mach, file_re)
        if penalty is not None:
            if penalty < min_penalty:
                min_penalty = penalty
                best_file = file_path
                
    return best_file

