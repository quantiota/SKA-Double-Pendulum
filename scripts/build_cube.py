#!/usr/bin/env python3
"""VR cube (z, ż, P) of a pendulum run, built on template_vr.html (the genomics VR page).

From the 3rd step to step <last>: z = ‖Z‖, ż = Δz/Δt (backward), P = exp(−|ΔH/H|).
Colours from the input v = cos(θ2 − θ1): v rising (r > 0), v falling (r < 0), v crossing 0
(the arms pass 90° to each other, where the return jumps).

    python build_cube.py <run.csv> <last step> [H] -> ../vr/<stem>_steps<last>_vr.html
    H: entropy on the vertical axis instead of P -> ../vr/<stem>_steps<last>_entropy_vr.html
"""
import json
import pathlib
import sys

import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
NAMES = ["v rising (r > 0)", "v falling (r < 0)", "v crosses 0 (arms at 90°)"]
COLORS = ["#4e9be6", "#e8a33d", "#e05a7a"]


def swap(s, o, n):
    assert s.count(o) == 1, o
    return s.replace(o, n)


def main():
    csv, last = pathlib.Path(sys.argv[1]), int(sys.argv[2])
    ent = len(sys.argv) > 3 and sys.argv[3] == "H"
    s0 = (HERE / "template_vr.html").read_text(encoding="utf-8")
    i = s0.find("const D ="); e = s0.find("};", i) + 1
    d = pd.read_csv(csv).iloc[:last]
    z, H, dt, v, r = (d[c].to_numpy(float) for c in ("knowledge", "entropy", "delta_t", "v", "ret"))
    zd = np.r_[np.nan, np.diff(z)] / dt
    P = np.r_[np.nan, np.exp(-np.abs(np.diff(H) / H[1:]))]
    cross = np.r_[False, np.sign(v[1:]) != np.sign(v[:-1])]
    t = np.where(cross, 2, np.where(r > 0, 0, 1))
    c = slice(2, None)
    Y = H if ent else P
    D = dict(z=np.round(z[c], 2).tolist(), zd=np.round(zd[c], 1).tolist(), p=np.round(Y[c], 4).tolist(),
             t=t[c].tolist(), names=NAMES, colors=COLORS, zmax=float(z[c].max()), zdmax=float(np.nanmax(zd[c])),
             zdmin=float(np.nanmin(zd[c])))
    if ent:
        D.update(hmin=float(H[c].min()), hmax=float(H[c].max()))
    s = s0[:i] + "const D = " + json.dumps(D, separators=(",", ":"), ensure_ascii=False) + ";" + s0[e + 1:]
    s = swap(s, "const toZ = v => -(v / D.zdmax - 0.5) * SIZE;",
             "const toZ = v => -((v - D.zdmin) / (D.zdmax - D.zdmin) - 0.5) * SIZE;")
    s = swap(s, "<title>Transition Probability VR</title>", f"<title>Double Pendulum SKA{' Entropy' if ent else ''}</title>")
    src = (f"Simulated ideal double pendulum, run {csv.stem.split('_')[2][-1].upper()} (released at rest from "
           f"θ1 = θ2 = 150°; run B: θ2 + 0.001°)" if "runsim" in csv.stem
           else f"IBM double pendulum (Asseman et al. 2018), run {csv.stem}")
    desc = (f"{src}, steps 3–{last:,} "
            f"({last / 400:.2f} s at 400 Hz). Input: the return of v = cos(θ2 − θ1). ")
    s = s.replace(s[s.find("<p>E. coli"):s.find("Horizontal axes:")], f"<p>{desc}")
    s = s.replace(s[s.find("vertical axis: P.") + len("vertical axis: P."):s.find("</p>", s.find("vertical axis: P."))],
                  " 3 colours from the input v.")
    if ent:
        s = swap(s, "const toY = v => v * SIZE;                   // P      -> height",
                 "const toY = v => (v - D.hmin) / (D.hmax - D.hmin) * SIZE;   // H -> height")
        s = swap(s, "lab('P', -SIZE/2 - 0.08, SIZE + 0.06, -SIZE/2);", "lab('H', -SIZE/2 - 0.08, SIZE + 0.06, -SIZE/2);")
        s = swap(s, "lab(p.toFixed(2), -SIZE/2 - 0.12, p * SIZE, -SIZE/2, 0.06);",
                 "lab((D.hmin + p * (D.hmax - D.hmin)).toFixed(2), -SIZE/2 - 0.12, p * SIZE, -SIZE/2, 0.06);")
        s = swap(s, "lab('Transition probability P in the phase space (z, ż)'", "lab('Entropy H in the phase space (z, ż)'")
        s = swap(s, "<h1>Transition probability P in the phase space (z, ż)</h1>", "<h1>Entropy H in the phase space (z, ż)</h1>")
        s = swap(s, "vertical axis: P.", "vertical axis: H, the entropy of the learner.")
    out = HERE.parent / "vr" / f"{csv.stem}_steps{last}{'_entropy' if ent else ''}_vr.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(s, encoding="utf-8")
    print("saved", out, {n: int((t[c] == k).sum()) for k, n in enumerate(NAMES)})


if __name__ == "__main__":
    main()
