#!/usr/bin/env python3
"""Largest Lyapunov exponent λ of the simulated double pendulum (start θ1 = θ2 = 150° at rest), and the same
growth rate measured on what SKA learned from runs A and B (θ2 differs by 0.001°).

Trajectory: Benettin method. A reference and a neighbour separated by d0 = 1e-8 in phase space
(θ1, ω1, θ2, ω2) are integrated together; every τ = 0.01 s the separation d is measured, ln(d/d0) added,
and the neighbour put back at distance d0 along the same direction. λ = Σ ln(d/d0) / T, in 1/s.
The doubling time of an error is ln 2 / λ.

SKA: |z_A − z_B| and |H_A − H_B| along steps 3–3,500; the rate is the slope of ln|difference| against t
(least squares), in 1/s, the same unit as λ.

    python lyapunov.py   -> ../results/lyapunov.png, printed values
"""
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from simulate import TH1, TH2, rhs                                 # noqa: E402

D0, TAU, T = 1e-8, 0.01, 44.0


def benettin():
    y = np.array([TH1, 0.0, TH2, 0.0])
    u = np.array([0.0, 0.0, 1.0, 0.0]) * D0
    s, ts, lam = 0.0, [], []
    for k in range(int(T / TAU)):
        a = solve_ivp(rhs, (0, TAU), y, method="DOP853", rtol=1e-12, atol=1e-12).y[:, -1]
        b = solve_ivp(rhs, (0, TAU), y + u, method="DOP853", rtol=1e-12, atol=1e-12).y[:, -1]
        d = np.linalg.norm(b - a)
        s += np.log(d / D0)
        u = (b - a) * D0 / d
        y = a
        ts.append((k + 1) * TAU)
        lam.append(s / ((k + 1) * TAU))
    return np.array(ts), np.array(lam)


def ska_rate(col):
    A = pd.read_csv(ROOT / "results" / "ska_runsim_a_scale4.csv").iloc[2:3500]
    B = pd.read_csv(ROOT / "results" / "ska_runsim_b_scale4.csv").iloc[2:3500]
    t, d = A.t_s.to_numpy(), np.abs(A[col].to_numpy() - B[col].to_numpy())
    m = d > 0
    return t, d, np.polyfit(t[m], np.log(d[m]), 1)[0]


def main():
    ts, lam = benettin()
    print(f"trajectory: λ = {lam[-1]:.3f} 1/s  (at 10 s: {lam[int(10 / TAU) - 1]:.3f}, at 20 s: {lam[int(20 / TAU) - 1]:.3f}); "
          f"an error doubles every {np.log(2) / lam[-1]:.3f} s")
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.2))
    axs[0].plot(ts, lam, lw=1, color="#1f5fa8")
    axs[0].set_xlabel("t, s")
    axs[0].set_ylabel("λ, 1/s")
    axs[0].set_title(f"Trajectory: largest Lyapunov exponent, λ = {lam[-1]:.2f} 1/s")
    axs[0].grid(alpha=0.3)
    for col, lab, c in (("knowledge", "|z_A − z_B|", "#1f5fa8"), ("entropy", "|H_A − H_B|", "#e8a33d")):
        t, d, r = ska_rate(col)
        print(f"SKA {col}: growth rate of {lab} = {r:.3f} 1/s; median difference {np.median(d):.3g}")
        axs[1].semilogy(t, d, lw=0.6, color=c, label=f"{lab}, rate {r:.3f} 1/s")
    axs[1].set_xlabel("t, s (steps 3–3,500)")
    axs[1].set_ylabel("difference between runs A and B")
    axs[1].set_title("SKA: difference between the two learned runs")
    axs[1].legend()
    axs[1].grid(alpha=0.3)
    out = ROOT / "results" / "lyapunov.png"
    fig.savefig(out, dpi=130, bbox_inches="tight")
    print("saved", out)


if __name__ == "__main__":
    main()
