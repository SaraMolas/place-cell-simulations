"""
Plots for visualizing trajectories and neural activity.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d


def occupancy_plot(pos: np.ndarray, track_length: float, n_bins: int):
    """
    Plot occupancy histogram.
    """
    bins = np.linspace(0.0, track_length, n_bins + 1)
    hist, _ = np.histogram(pos, bins=bins)
    occupancy = hist.astype(float) / hist.sum()
    centers_plot = 0.5 * (bins[:-1] + bins[1:])

    fig, ax = plt.subplots(figsize=(12, 5))
    plt.bar(centers_plot, occupancy, width=centers_plot[1]-centers_plot[0], color='C1', edgecolor='k', alpha=0.8)
    plt.xlabel("position (m)")
    plt.ylabel("occupancy fraction")
    plt.title("Occupancy of regions along track")
    plt.xlim(0, track_length)
    plt.xticks(np.linspace(0, track_length, 11))
    plt.show()

    return fig, ax

def plot_position(time: np.ndarray, pos: np.ndarray, track_length: float):
    """
    Plot trajectory along track.
    """
    fig, ax = plt.subplots(figsize=(12, 5))
    plt.plot(time, pos, linewidth=0.4)
    plt.ylabel("position (m)")
    plt.title("Movement trajectory along track")
    plt.show()

    return fig, ax

def plot_spike_raster(spike_times: np.ndarray, duration: float, centers: np.array):
    """
    Plot spike raster of all neurons.
    """
    n_neurons = len(spike_times)
    
    if n_neurons != len(centers):
        raise ValueError("Number of neurons and number of centers must match.")
    
    n_neurons = len(spike_times)
    
    fig, ax = plt.subplots(figsize=(10, 2 + 0.5 * n_neurons))
    for i in range(n_neurons):
        plt.scatter(spike_times[i], np.ones_like(spike_times[i]) * i, s=10)
    plt.yticks(np.arange(n_neurons), [f'Cell {i} (center={centers[i]:.2f} m)' for i in range(n_neurons)])
    plt.xlabel('Time (s)')
    plt.title('Spike raster')
    plt.ylabel('Neurons')
    plt.ylim(-0.5, n_neurons - 0.5)
    plt.xlim(0, duration)
    plt.show()

    return fig, ax

def plot_empirical_vs_theoretical_rate(empirical_rates: np.ndarray, theoretical_rates: np.ndarray, 
                                       bin_centers: np.ndarray, centers: np.ndarray, peak_rates: np.ndarray, 
                                       x: np.ndarray, track_length: float):
    """
    Plot empirical and theoretical rate maps for all neurons.
    """
    # Empirical rate maps vs theoretical
    n_neurons = empirical_rates.shape[0]

    if n_neurons != theoretical_rates.shape[0]:
        raise ValueError("Number of neurons in empirical and theoretical rates must match.")
    if n_neurons != len(centers) or n_neurons != len(peak_rates):
        raise ValueError("Number of neurons and number of centers/peak rates must match.")
    if empirical_rates.shape[1] != theoretical_rates.shape[1]:
        raise ValueError("Empirical and theoretical rates must have the same number of position bins.")
    if empirical_rates.shape[1] != len(bin_centers):
        raise ValueError("Number of position bins in empirical rates and bin centers must match.")
    
    fig, ax = plt.subplots(figsize=(10, 2 + 0.5 * n_neurons))
    for i in range(n_neurons):
        plt.subplot(n_neurons, 1, i+1)
        plt.plot(bin_centers, empirical_rates[i], label='Empirical rate (spikes / occupancy)')
        plt.plot(x, theoretical_rates[i], label='Theoretical Gaussian rate', linestyle='--')
        plt.ylabel('Firing rate (Hz)')
        plt.title(f'Cell {i} place field: center={centers[i]:.2f} m, peak={peak_rates[i]} Hz')
        plt.xlim(0, track_length)
        plt.legend()
    plt.xlabel('Position (m)')
    plt.tight_layout()
    plt.show()
    return fig, ax

def plot_rate_maps(spikes: np.ndarray, positions: np.ndarray, times: np.ndarray, n_bins: int=50, smooth_sigma: float=1.0):
    """
    Plot firing rate heatmap for a population of neurons on a 1D track.
    
    Parameters
    ----------
    spikes : ndarray, shape (n_cells, n_timepoints)
        Binary spike matrix (1 = spike, 0 = no spike).
    positions : ndarray, shape (n_timepoints,)
        Position of the animal at each time point.
    times : ndarray, shape (n_timepoints,)
        Time vector (seconds).
    n_bins : int
        Number of spatial bins along the track.
    smooth_sigma : float
        Standard deviation for Gaussian smoothing (in bins).
    """
    n_cells = spikes.shape[0]
    
    # Bin positions
    pos_bins = np.linspace(positions.min(), positions.max(), n_bins+1)
    digitized = np.digitize(positions, pos_bins) - 1  # bin indices
    
    # Occupancy (time spent in each position bin)
    dt = np.mean(np.diff(times))
    occupancy = np.zeros(n_bins)
    for b in range(n_bins):
        occupancy[b] = np.sum(digitized == b) * dt
    
    # Avoid divide by zero
    occupancy[occupancy == 0] = np.nan
    
    # Compute firing rate per neuron per position bin
    rate_map = np.zeros((n_cells, n_bins))
    for i in range(n_cells):
        spike_counts, _ = np.histogram(positions[spikes[i] == 1], bins=pos_bins)
        rate_map[i, :] = spike_counts / occupancy
    
    # Smooth along position axis
    if smooth_sigma > 0:
        rate_map = gaussian_filter1d(rate_map, sigma=smooth_sigma, axis=1, mode="nearest")
    
    # Plot heatmap
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.imshow(rate_map, aspect="auto", origin="lower", 
               extent=[positions.min(), positions.max(), 0, n_cells],
               cmap="viridis")
    plt.colorbar(label="Firing rate (Hz)")
    plt.xlabel("Position along track (m)")
    plt.ylabel("Neuron index")
    plt.title("Firing rate heatmap")
    plt.show()

    return fig, ax
    