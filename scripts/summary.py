#!/usr/bin/env python3
"""One line per learned run, steps 1–3,500: start angles, 90° crossings, P one step after a crossing,
median P on the other steps, entropy minimum. Appends to results/summary_scale4.csv.

    python summary.py <run>
"""
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main():
    run = int(sys.argv[1])
    d = pd.read_csv(ROOT / "results" / f"ska_run{run}_scale4.csv").iloc[:3500].reset_index(drop=True)
    v = d.v.to_numpy()
    cross = np.r_[False, np.sign(v[1:]) != np.sign(v[:-1])]
    after = np.r_[False, cross[:-1]]
    after[:2] = False
    rest = d.P[~after].iloc[2:]
    row = dict(run=run, theta1_start_deg=round(np.degrees(d.theta1[0]), 1), theta2_start_deg=round(np.degrees(d.theta2[0]), 1),
               crossings=int(cross[2:].sum()), P_after_crossing=round(d.P[after].mean(), 4),
               P_after_crossing_std=round(d.P[after].std(), 4), P_other_median=round(rest.median(), 3),
               other_below_0_6=int((rest < 0.6).sum()), H_min=round(d.entropy.min(), 3),
               H_min_step=int(d.entropy.idxmin() + 1))
    out = ROOT / "results" / "summary_scale4.csv"
    t = pd.read_csv(out) if out.exists() else pd.DataFrame()
    t = pd.concat([t[t.run != run] if len(t) else t, pd.DataFrame([row])]).sort_values("run")
    t.to_csv(out, index=False)
    print(" ".join(f"{k}={v}" for k, v in row.items()))


if __name__ == "__main__":
    main()
