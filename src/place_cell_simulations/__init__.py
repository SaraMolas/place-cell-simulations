from .movement import generate_trajectory
from .spikes import generate_place_cell_spikes, generate_noise_cell_spikes
from .utils import compute_empirical_rate_maps, compute_theoretical_rate_maps, save_dataset
from .plots import plot_position, plot_spike_raster, plot_empirical_vs_theoretical_rate, plot_rate_maps

__all__ = [
    "generate_trajectory",
    "save_dataset",
    "generate_place_cell_spikes",
    "generate_noise_cell_spikes",
    "compute_empirical_rate_maps",
    "compute_theoretical_rate_maps",
    "occupancy_plot",
    "plot_position",
    "plot_spike_raster",
    "plot_empirical_vs_theoretical_rate",
    "plot_rate_maps"
]