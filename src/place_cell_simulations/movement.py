

"""
Trajectory generation
"""
from typing import Dict, Optional
import numpy as np


def generate_trajectory(track_length: float = 1.0, dt: float = 0.005, duration_s: float = 300.0, 
                        theta: float = 1.0, mu: float = 0.0, sigma: float = 0.4, v0: float = 0.0, 
                        seed: Optional[int] = 42) -> Dict[str, np.ndarray]:
    """
    Simulate a 1D trajectory along a linear track using an Ornstein-Uhlenbeck process for velocity.

    Returns a dict with keys: "time" (s), "position" (m), "velocity" (m/s), and "meta" (dict of parameters).
    """

    rng = np.random.default_rng(seed)
    n_steps = int(np.ceil(duration_s/ dt))
    time = np.arange(n_steps) * dt

    # Initialize arrays
    pos = np.zeros(n_steps)
    vel = np.zeros(n_steps)
    pos[0] = 0.5  # start in middle
    vel[0] = v0

    # simulate velocity (OU) and integrate to position with reflecting boundaries
    for t in range(n_steps - 1):
        vel[t+1] = vel[t] + theta * (mu - vel[t]) * dt + sigma * np.sqrt(dt) * rng.standard_normal()
        pos[t+1] = pos[t] + vel[t+1] * dt
        # reflect at boundaries
        if pos[t+1] < 0:
            pos[t+1] = -pos[t+1]
            vel[t+1] = -vel[t+1]
        elif pos[t+1] > track_length:
            pos[t+1] = 2*track_length - pos[t+1]
            vel[t+1] = -vel[t+1]

    # return parameters used for simulating movement
    meta = {
        "track_length": float(track_length),
        "dt": float(dt),
        "duration_s": float(duration_s),
        "theta": float(theta),
        "mu": float(mu),
        "sigma": float(sigma),
        "seed": int(seed) if seed is not None else None,
    }

    return {"time": time, "pos": pos, "velocity": vel, "meta": meta}