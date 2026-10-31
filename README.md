# SKA Double Pendulum

Structured Knowledge Accumulation (SKA) learning of a real double pendulum. The learner reads one
input per camera frame and builds, without any equation of motion, the probability cube
(z, ż, P) and the entropy cube (z, ż, H) of the motion.

A classical trajectory is obtained by solving the differential equations of the pendulum; the entropy
trajectory is obtained by SKA learning of the data alone.

## Data

[Double Pendulum Chaotic Dataset](https://ibm.github.io/double-pendulum-chaotic-dataset/), IBM Research
(Asseman, Kornuta, Ozcan, 2018): 21 runs of a real double pendulum filmed by a high-speed camera,
17,284 to 18,337 frames each, 400 frames per second (about 44 s per run). For each frame, the pixel
positions of three markers: red = pivot, green = end of arm 1 (91 mm), blue = end of arm 2 (70 mm).

IBM's Data Asset eXchange is closed; the original CSV files are kept in
[erwincoumans/tiny-differentiable-simulator](https://github.com/erwincoumans/tiny-differentiable-simulator/tree/master/data/ibm-double-pendulum).
Data license: Community Data License Agreement – Sharing 1.0 (`LICENSE.pdf` in that folder).

## Input

From the markers, the angle of each arm from the downward vertical, θ1 and θ2. One input per frame:

```
v_n = cos(θ2_n − θ1_n)                    the angle between the two arms
r_n = (v_n − v_{n−1}) / v_{n−1}           its simple return
x_n = 1 / (1 + exp(−4 · r_n))             scale 4
```

Δt = 1/400 s per step. Fresh learner for each run, buffer 3,500 steps. The cubes show steps 3 to
3,500 (8.75 s), the learning phase; after step 3,500 the buffer is full and slides.

## Results

The 21 runs start from different positions and follow different paths (22 to 99 passages of the
arms through 90°), yet the learner builds the same cube in every run:

- P = 0.45 one step after each passage of the arms through 90° (0.4487 to 0.4507 over the 21 runs);
- P near 1 on the other steps (median 0.976 to 0.995);
- the same entropy trajectory: minimum H = −1.57 to −1.60, reached at step 887 to 1,033.

One row per run: [`results/summary_scale4.csv`](results/summary_scale4.csv).

## Cubes

For each run N (0 to 20), in `vr/`:

| file | view |
|---|---|
| `ska_runN_scale4_steps3500_vr.html` | (z, ż, P) |
| `ska_runN_scale4_steps3500_entropy_vr.html` | (z, ż, H) |
| `..._vr_replay.html` | the same cube with a replay, step by step (400 steps/s = real time) |

z = ‖Z‖, ż = Δz/Δt, P = exp(−|ΔH/H|). Colours from the input v: v rising, v falling, v crossing 0
(the arms at 90°). Each page is a standalone HTML file (desktop, phone and VR headset).

## Files

- `scripts/angles.py`: θ1, θ2 from the marker pixels (`results/angles_run0.csv`, `.png`)
- `scripts/plot_run.py`: v, x, H and P along a run; the (z, ż, P) cube of the whole run
- `scripts/build_cube.py`: the VR cube of a run (`H` for the entropy cube), on `scripts/template_vr.html`
- `scripts/add_replay.py`: the replay
- `scripts/summary.py`: one line per run in `results/summary_scale4.csv`
- `results/ska_runN_scale4.csv`: the learning output of each run (one row per step: t, θ1, θ2, v, r,
  x, z, H, P), with `_series.png` and `_cube.png`

## Run

```bash
git clone https://github.com/quantiota/SKA-Double-Pendulum.git
cd SKA-Double-Pendulum
mkdir -p data/ibm/original
B=https://raw.githubusercontent.com/erwincoumans/tiny-differentiable-simulator/master/data/ibm-double-pendulum
for i in $(seq 0 20); do wget -q -O data/ibm/original/$i.csv $B/original/dpc_dataset_csv/$i.csv; done
pip install numpy pandas matplotlib

python scripts/angles.py 0
python scripts/plot_run.py results/ska_run0_scale4.csv
python scripts/build_cube.py results/ska_run0_scale4.csv 3500
python scripts/build_cube.py results/ska_run0_scale4.csv 3500 H
python scripts/add_replay.py vr/ska_run0_scale4_steps3500_vr.html results/ska_run0_scale4.csv vr/ska_run0_scale4_steps3500_vr_replay.html
```

## Reference

A. Asseman, T. Kornuta, A. Ozcan, "Learning beyond simulated physics," NeurIPS 2018 Workshop on
Modeling and Decision-making in the Spatiotemporal Domain,
[openreview.net/pdf?id=HylajWsRF7](https://openreview.net/pdf?id=HylajWsRF7).

## License

MIT (code). The data and the results derived from them: CDLA-Sharing 1.0.
