#!/usr/bin/env python3
import argparse
from place_cell_simulations import (
    generate_trajectory,
    save_dataset,
    generate_place_cell_spikes,
    generate_noise_cell_spikes,
    compute_empirical_rate_maps,
    compute_theoretical_rate_maps,
    occupancy_plot,
    plot_position,
    plot_spike_raster,
    plot_empirical_vs_theoretical_rate,
    plot_rate_maps
)
import numpy as np
import os


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=str, default="data/toy_example.npz")
    p.add_argument("--preview", type=str, default="data/preview.png")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(args.preview) or ".", exist_ok=True)

    # generate trajectory and make plots 
    traj = generate_trajectory(track_length = 1.0, dt = 0.005, duration_s = 300.0, theta = 1.0, mu = 0.0, sigma = 0.4, v0 = 0.0) 

    fig1, _ =  occupancy_plot(time = traj["time"], pos = traj["pos"], track_length = traj["meta"]["track_length"], n_bins = 50)
    
    fig2, _ = plot_position(traj["time"], pos = traj["pos"], track_length = traj["meta"]["track_length"])
    
    # parameters for place cells
    n_cells = 20
    centers = np.linspace(0.1, 0.9, n_cells)
    sigmas = np.full(n_cells, 0.1)
    peak_rates = np.random.uniform(5, 20, n_cells)
    baseline_rate = 0.5
    
    # parameters for noise cells
    n_noise = 10
    min_noise_rate = 0.1
    max_noise_rate = 1.0

    # generate spikes and rates for place cells
    spikes, spike_times, spike_pos, spike_counts = generate_place_cell_spikes(centers, sigmas, peak_rates, baseline_rate,
                               traj['pos'], traj['time'], traj['dt']) 

    empirical_rate_maps, bin_centers = compute_empirical_rate_maps(n_bins = 100, track_length = traj["meta"]["track_length"], pos = traj["pos"], dt = traj["dt"], 
                                spike_postions = spike_pos) 
    
    theoretical_rates, x = compute_theoretical_rate_maps(track_length=traj["meta"]["track_length"], centers = centers, sigma_pf = sigmas, peak_rates = peak_rates, 
                                  baseline_rate = baseline_rate)
    
    # generate spikes for noise cells
    noise_spikes = generate_noise_cell_spikes(n_noise = n_noise, min_rate = min_noise_rate, max_rate = max_noise_rate,  time = traj['time'], dt = traj['dt'])
    
    # save dataset (trajectory only for now) and additional arrays
    save_dataset({"time": traj["time"], "pos": traj["pos"], "vel": traj["vel"], "meta": traj["meta"]}, args.out)
    print("Saved dataset to", args.out)

    # create figures with spike raster and empirical vs theoretical rate maps of place cells 
    fig3, _ = plot_spike_raster(spike_times = spike_times, duration = traj["meta"]["duration"], centers = centers)

    fig4, _ = plot_empirical_vs_theoretical_rate(empirical_rates = empirical_rate_maps, theoretical_rates = theoretical_rates, 
                                       bin_centers = bin_centers, centers = centers, peak_rates = peak_rates, 
                                       x = x, track_length = traj["meta"]["track_length"])
    

    # join spikes of place cells and noise cells and save figure
    all_spikes = np.vstack([spikes, noise_spikes])
    fig5, _ = plot_rate_maps(spikes = all_spikes, positions = traj["pos"], times = traj["time"], n_bins = 50, smooth_sigma = 1.0)
    
    # Save ratemap of all neurons
    fig5.savefig(args.preview, dpi=150)
    print("Saved preview to", args.preview)


if __name__ == "__main__":
    main()
