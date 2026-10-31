#!/usr/bin/env python3
"""Two simulated runs of an ideal double pendulum that start 0.001° apart (θ2), to compare with SKA.

Point masses m1 = m2, arms l1 = 0.091 m, l2 = 0.070 m (the IBM pendulum), g = 9.81 m/s², no friction,
released at rest. Equations of motion: the standard Lagrangian ones. Integration: scipy solve_ivp
(DOP853, rtol = atol = 1e-12), sampled at 400 Hz like the camera, 17,782 frames (as IBM run 0).
Start: θ1 = θ2 = 150° at rest (sim_a) and θ2 + 0.001° (sim_b): enough energy for the arms to flip over.

    python simulate.py   -> ../data/sim/sim_a.csv, sim_b.csv (t_s, theta1_rad, theta2_rad)
                            ../results/sim_divergence.png
"""
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

ROOT = pathlib.Path(__file__).resolve().parents[1]
L1, L2, M1, M2, G = 0.091, 0.070, 1.0, 1.0, 9.81
FPS, N = 400, 17782
TH1, TH2, D = np.radians(150.0), np.radians(150.0), np.radians(0.001)


def rhs(t, y):
    a, wa, b, wb = y
    d = a - b
    den = 2 * M1 + M2 - M2 * np.cos(2 * d)
    da = (-G * (2 * M1 + M2) * np.sin(a) - M2 * G * np.sin(a - 2 * b)
          - 2 * np.sin(d) * M2 * (wb ** 2 * L2 + wa ** 2 * L1 * np.cos(d))) / (L1 * den)
    db = (2 * np.sin(d) * (wa ** 2 * L1 * (M1 + M2) + G * (M1 + M2) * np.cos(a)
          + wb ** 2 * L2 * M2 * np.cos(d))) / (L2 * den)
    return [wa, da, wb, db]


def run(th2):
    t = np.arange(N) / FPS
    s = solve_ivp(rhs, (0, t[-1]), [TH1, 0, th2, 0], t_eval=t, method="DOP853", rtol=1e-12, atol=1e-12)
    return t, s.y[0], s.y[2]


def main():
    out = ROOT / "data" / "sim"
    out.mkdir(parents=True, exist_ok=True)
    R = {}
    for name, th2 in (("sim_a", TH2), ("sim_b", TH2 + D)):
        t, a, b = run(th2)
        R[name] = (t, a, b)
        np.savetxt(out / f"{name}.csv", np.c_[t, a, b], delimiter=",", header="t_s,theta1_rad,theta2_rad",
                   comments="", fmt="%.10f")
    t = R["sim_a"][0]
    d1, d2 = (np.degrees(np.abs(R["sim_a"][k] - R["sim_b"][k])) for k in (1, 2))
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.semilogy(t, d1, lw=0.8, label="|Δθ1|")
    ax.semilogy(t, d2, lw=0.8, label="|Δθ2|")
    ax.axvline(3500 / FPS, color="grey", ls="--", lw=0.8)
    ax.set_xlabel("t, s")
    ax.set_ylabel("difference between the two runs, degrees")
    ax.set_title("Two simulated runs, θ2 differs by 0.001° at the start (dashed: step 3,500)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.savefig(ROOT / "results" / "sim_divergence.png", dpi=130, bbox_inches="tight")
    for s in (1, 2, 4, 8.75, 20, 44):
        k = min(int(s * FPS), N - 1)
        print(f"t = {s:5g} s: |Δθ1| = {d1[k]:.3g}°, |Δθ2| = {d2[k]:.3g}°")


if __name__ == "__main__":
    main()
