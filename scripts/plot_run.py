#!/usr/bin/env python3
"""Figures of one SKA pendulum run (results/ska_run<run>_scale<s>.csv).

    python plot_run.py <run.csv>
        -> <stem>_series.png   v = cos(θ2 − θ1), input x, entropy H, P along the run
           <stem>_cube.png     the (z, ż, P) cube, z = ‖Z‖, ż = Δz/Δt, coloured by time
"""
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main():
    csv = pathlib.Path(sys.argv[1])
    d = pd.read_csv(csv)
    stem = csv.with_suffix("")
    t = d.t_s.to_numpy()

    fig, axs = plt.subplots(4, 1, figsize=(12, 9), sharex=True)
    for ax, col, lab in zip(axs, ("v", "x_input", "entropy", "P"),
                            ("v = cos(θ2 − θ1)", "input x", "entropy H", "P")):
        ax.plot(t, d[col], lw=0.5, color="#1f5fa8")
        ax.set_ylabel(lab)
        ax.grid(alpha=0.3)
    axs[-1].set_xlabel("t, s (Δt = 1/400 s)")
    fig.suptitle(csv.stem)
    fig.savefig(f"{stem}_series.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    z = d.knowledge.to_numpy(float)
    zd = np.r_[np.nan, np.diff(z)] / d.delta_t.to_numpy(float)
    c = slice(2, None)
    fig = plt.figure(figsize=(9, 8))
    ax = fig.add_subplot(projection="3d")
    sc = ax.scatter(z[c], zd[c], d.P.to_numpy()[c], c=t[c], cmap="viridis", s=1)
    ax.set_xlabel("z = ‖Z‖")
    ax.set_ylabel("ż")
    ax.set_zlabel("P")
    fig.colorbar(sc, ax=ax, shrink=0.6, label="t, s")
    fig.suptitle(f"{csv.stem}: (z, ż, P)")
    fig.savefig(f"{stem}_cube.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print("saved", f"{stem}_series.png", f"{stem}_cube.png")


if __name__ == "__main__":
    main()
