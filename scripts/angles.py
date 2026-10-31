#!/usr/bin/env python3
"""Angles of the IBM double pendulum (Asseman et al. 2018) from the marker pixels.

CSV columns: x_red, y_red, x_green, y_green, x_blue, y_blue (pixels, image y points down).
red = pivot, green = end of arm 1 (91 mm), blue = end of arm 2 (70 mm); time step 1/400 s.
θ1 = angle of arm 1, θ2 = angle of arm 2, both from the downward vertical, counter-clockwise on screen, unwrapped.

    python angles.py [run]   -> angles_run<run>.csv, angles_run<run>.png
"""
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
DT = 1 / 400


def angles(run):
    a = np.loadtxt(ROOT / "data/ibm/original" / f"{run}.csv", delimiter=",")
    r, g, b = a[:, 0:2], a[:, 2:4], a[:, 4:6]
    th1 = np.unwrap(np.arctan2(g[:, 0] - r[:, 0], g[:, 1] - r[:, 1]))
    th2 = np.unwrap(np.arctan2(b[:, 0] - g[:, 0], b[:, 1] - g[:, 1]))
    return np.arange(len(a)) * DT, th1, th2


def main():
    run = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    t, th1, th2 = angles(run)
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    np.savetxt(out / f"angles_run{run}.csv", np.c_[t, th1, th2], delimiter=",",
               header="t_s,theta1_rad,theta2_rad", comments="", fmt="%.6f")
    fig, axs = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    for ax, th, name in zip(axs, (th1, th2), ("θ1 (arm 1)", "θ2 (arm 2)")):
        ax.plot(t, np.degrees(th), lw=0.8, color="#1f5fa8")
        ax.set_ylabel(f"{name}, degrees")
        ax.grid(alpha=0.3)
    axs[1].set_xlabel("t, s (Δt = 1/400 s)")
    fig.suptitle(f"IBM double pendulum, run {run}: {len(t)} frames, {t[-1]:.1f} s")
    fig.savefig(out / f"angles_run{run}.png", dpi=130, bbox_inches="tight")
    print("saved", out / f"angles_run{run}.csv", out / f"angles_run{run}.png")
    for name, th in (("θ1", th1), ("θ2", th2)):
        print(f"{name}: start {np.degrees(th[0]):7.1f}°, min {np.degrees(th.min()):8.1f}°, "
              f"max {np.degrees(th.max()):8.1f}°, end {np.degrees(th[-1]):8.1f}°")


if __name__ == "__main__":
    main()
