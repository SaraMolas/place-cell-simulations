

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
    # set random seed
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

def generate_trajectory_with_undersampling(track_length: float = 1.0, dt: float = 0.005, duration_s: float = 300.0, 
                        theta: float = 1.0, mu: float = 0.0, sigma: float = 0.4, v0: float = 0.0, last_zone_frac: float = 0.1,
                        p_reject: float = 0.85, seed: Optional[int] = 42) -> Dict[str, np.ndarray]:
    """
    Simulate a 1D trajectory with UNDERSAMPLING along a linear track using an Ornstein-Uhlenbeck process for velocity.

    Simulate a barrier towards the end of the track, where the animal has a high probability of being reflected back when 
    trying to enter. For the default parameters, the last 10% of the track is undersampled by 85%. 

    Returns a dict with keys: "time" (s), "position" (m), "velocity" (m/s), and "meta" (dict of parameters).
    """
    # Last-zone under-sampling
    last_zone = track_length * (1.0 - last_zone_frac)  # 0.9 m
    p_reject = 0.85                  # probability to reject entry into last zone when moving right

    # set random seed
    rng = np.random.default_rng(seed)
    n_steps = int(np.ceil(duration_s/ dt))
    time = np.arange(n_steps) * dt

    # Initial state
    pos = np.zeros(n_steps, dtype=np.float32)
    speed = np.zeros(n_steps, dtype=np.float32)   # non-negative speed magnitude
    direction = np.ones(n_steps, dtype=np.int8)   # +1 = moving right, -1 = moving left

    pos[0] = 0.0        # start at left end (0.0)
    speed[0] = v0
    direction[0] = +1   # start moving to the right

    # -----------------------
    # Simulation loop
    # -----------------------
    for t in range(n_steps - 1):
        # update speed (OU on the magnitude, reflect at zero)
        ds = theta * (mu - speed[t]) * dt + sigma * np.sqrt(dt) * rng.standard_normal()
        speed[t+1] = speed[t] + ds
        if speed[t+1] < 0:
            speed[t+1] = 0.0

        # tentative next position
        next_pos = pos[t] + direction[t] * speed[t+1] * dt

        # If moving right and attempting to enter last zone, probabilistically reject / reflect
        if direction[t] == 1 and pos[t] < last_zone and next_pos >= last_zone:
            if rng.random() < p_reject:
                # reject the attempted entry: reflect to just inside last_zone
                # compute overshoot and reflect
                overshoot = next_pos - last_zone
                next_pos = last_zone - overshoot
                # damp and reverse a bit to encourage moving left afterwards
                speed[t+1] = speed[t+1] * 0.5
                direction[t+1] = -1
                # store and continue
                pos[t+1] = np.clip(next_pos, 0.0, track_length)
                continue

        # handle boundary hits: if we exceed right end or go below 0, reflect and flip direction
        if next_pos < 0.0:
            # reflect and flip
            overshoot = -next_pos
            next_pos = overshoot
            direction[t+1] = +1  # move right after bounce
            # optionally damp speed a bit
            speed[t+1] = speed[t+1] * 0.6
        elif next_pos > track_length:
            overshoot = next_pos - track_length
            next_pos = track_length - overshoot
            direction[t+1] = -1  # move left after bounce
            speed[t+1] = speed[t+1] * 0.6
        else:
            # otherwise keep same direction
            direction[t+1] = direction[t]

        # commit position
        pos[t+1] = np.clip(next_pos, 0.0, track_length)

    # return parameters used for simulating movement
    meta = {
        "track_length": float(track_length),
        "dt": float(dt),
        "duration_s": float(duration_s),
        "theta": float(theta),
        "mu": float(mu),
        "sigma": float(sigma),
        "seed": int(seed) if seed is not None else None,
        "last_zone_frac": float(last_zone_frac),
        "p_reject": float(p_reject),
    }

    return {"time": time, "pos": pos, "velocity": speed, "meta": meta}