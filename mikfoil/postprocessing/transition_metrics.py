"""
Flow Separation and Transition Module

Physics Context:
- LM_gamma (Intermittency): The primary variable in the Langtry-Menter (gamma-Re_theta) model. 
  It ranges from 0 (laminar) to 1 (fully turbulent). It models natural, bypass, and wake-induced transition.
- LM_gamma_eff (Effective Intermittency): Incorporates both the base intermittency and the 
  separation-induced intermittency to give the final value used to scale the turbulence production.
- LM_gamma_sep (Separation Intermittency): Specifically models transition due to laminar separation bubbles.
  When this value goes above 0, it indicates that the flow has separated laminarly and is transitioning.
"""
from typing import Dict, Optional
import numpy as np
import pandas as pd
from mikfoil.case import Case
from mikfoil.data_management.surface_data import load_surface_data

def calculate_transition_and_separation(case: Case) -> Optional[Dict[str, float]]:
    file_path = case.dir / "surface_data.csv"
    if not file_path.exists() or "LM_gamma" not in pd.read_csv(file_path, nrows=0).columns:
        return None

    upper_metrics = _analyze_surface(case, 'upper')
    lower_metrics = _analyze_surface(case, 'lower')
    
    return {**upper_metrics, **lower_metrics}

def _analyze_surface(case: Case, surface: str) -> Dict[str, float]:
    x_coords = load_surface_data(case, source='SU2', surface=surface, variable='x')
    gamma = load_surface_data(case, source='SU2', surface=surface, variable='LM_gamma')
    gamma_sep = load_surface_data(case, source='SU2', surface=surface, variable='LM_gamma_sep')
    
    transition_x = _find_transition_point(x_coords, gamma)
    separation_x = _find_separation_point(x_coords, gamma_sep)
    
    return {
        f'transition_{surface}_x': transition_x,
        f'separation_{surface}_x': separation_x
    }

def _find_transition_point(x: np.ndarray, gamma: np.ndarray, threshold: float = 0.5) -> float:
    if len(gamma) == 0:
        return -1.0
    
    transition_indices = np.where(gamma > threshold)[0]
    if len(transition_indices) > 0:
        return float(x[transition_indices[0]])
    return -1.0

def _find_separation_point(x: np.ndarray, gamma_sep: np.ndarray, threshold: float = 0.01) -> float:
    if len(gamma_sep) == 0:
        return -1.0
    
    separation_indices = np.where(gamma_sep > threshold)[0]
    if len(separation_indices) > 0:
        return float(x[separation_indices[0]])
    return -1.0
