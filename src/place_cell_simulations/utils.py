
"""
Additional utility functions.
"""
from typing import Dict, Any, Tuple
import numpy as np
import json
import os

def save_dataset(dataset: Dict[str, Any], out_file: str) -> None:
    """
    Save dataset to compressed npz. meta is JSON-serialized.
    """
    os.makedirs(os.path.dirname(out_file) or ".", exist_ok=True)
    meta = json.dumps(dataset.get("meta", {}))
    np.savez_compressed(out_file, time=dataset["time"], pos=dataset["pos"], vel=dataset["vel"], meta=meta)

def compute_empirical_rate_maps(n_bins: int, track_length: float, pos: np.ndarray, dt: float, 
                                spike_positions: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute empirical rate maps for all neurons.
    """
    n_neurons = spike_positions.shape[0]
    bins = np.linspace(0, track_length, n_bins + 1)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    occupancy, _ = np.histogram(pos, bins=bins)
    occupancy_time = occupancy * dt
    empirical_rate_maps = np.zeros((n_neurons, n_bins))
    for i in range(n_neurons):
        sc, _ = np.histogram(spike_positions[i], bins=bins)
        with np.errstate(divide='ignore', invalid='ignore'):
            empirical_rate_maps[i] = np.where(occupancy_time > 0, sc / occupancy_time, 0.0)
    
    return empirical_rate_maps, bin_centers

def compute_theoretical_rate_maps(track_length: float, centers: np.ndarray, sigma_pf: np.ndarray, peak_rates: np.ndarray, 
                                  baseline_rate: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute theoretical Gaussian rate maps for all neurons.
    """

    if len(centers) != len(sigma_pf) or len(centers) != len(peak_rates):
        raise ValueError("Length of centers, sigma_pf, and peak_rates must match.")
    
    n_neurons = len(centers)    
    x = np.linspace(0, track_length, 500)
    theoretical_rates = np.zeros((n_neurons, x.size))
    for i in range(n_neurons):
        theoretical_rates[i] = baseline_rate + peak_rates[i] * np.exp(-0.5 * ((x - centers[i]) / sigma_pf[i])**2)

    return theoretical_rates, x