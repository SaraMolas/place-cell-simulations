"""
Generate synthetic spike trains for place cells and noise cells.
"""
import numpy as np
from typing import Dict, Optional, Tuple

def generate_place_cell_spikes(centers: np.ndarray, sigma_pf: np.ndarray, peak_rates: np.ndarray, baseline_rate: float,
                               pos: np.ndarray, time: np.ndarray, duration_s: float, dt: float, seed: Optional[int]=42) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    
    """
    Generate spikes for place cells on a 1D track.
    
    Parameters
    ----------
    centers : ndarray, shape (n_cells,)
        Place field centers (meters).
    sigma_pf : ndarray, shape (n_cells,)
        Place field widths (standard deviation in meters).
    peak_rates : ndarray, shape (n_cells,)
        Peak firing rates (Hz).
    baseline_rate : float
        Baseline firing rate (Hz).
    """

    if len(centers) != len(sigma_pf) or len(centers) != len(peak_rates):
        raise ValueError("Length of centers, sigma_pf, and peak_rates must match.")
    
    if pos.ndim != 1 or time.ndim != 1:
        raise ValueError("pos and time must be 1D arrays.")
    
    if len(pos) != len(time):
        raise ValueError("pos and time must have the same length.")

    n_neurons = len(centers)
    n_steps = int(duration_s / dt)
    rates = np.zeros((n_neurons, n_steps))
    for i in range(n_neurons):
        rates[i] = baseline_rate + peak_rates[i] * np.exp(-0.5 * ((pos - centers[i]) / sigma_pf[i])**2)

    # Generate spikes: Bernoulli approximation for inhomogeneous Poisson
    rng = np.random.default_rng(seed)  # new rng for spikes
    spikes = rng.random(size=(n_neurons, n_steps)) < (rates * dt)

    # Extract spike times and positions
    spike_times = [time[spikes[i]] for i in range(n_neurons)]
    spike_positions = [pos[spikes[i]] for i in range(n_neurons)]
    spike_counts = np.sum(spikes, axis=1)

    return spikes, spike_times, spike_positions, spike_counts

def generate_noise_cell_spikes(n_noise: int, min_rate: int, max_rate: int, duration_s: float, 
                                dt: float, seed: Optional[int]=42) -> Tuple[np.ndarray]:
    """
    Generate spikes for noise cells (firing independent of position) on a 1D track.
    """

    noise_rates = np.random.uniform(min_rate, max_rate, size=n_noise)  # Hz, random per neuron

    # expand rates to all timesteps
    n_steps = int(duration_s / dt)
    noise_rates_matrix = noise_rates[:, None] * np.ones((n_noise, n_steps))

    # simulate spikes: Bernoulli draws
    rng = np.random.default_rng(seed)
    noise_spikes = rng.random(size=(n_noise, n_steps)) < (noise_rates_matrix * dt)

    return noise_spikes