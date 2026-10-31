# Chaos Test

Two simulated runs of an ideal double pendulum that start 0.001° apart. Their trajectories separate
exponentially; the cubes SKA learns from them stay the same.

## Simulation

Ideal double pendulum: equal point masses, arms 91 mm and 70 mm (as the IBM pendulum), g = 9.81 m/s²,
no friction, released at rest. Standard equations of motion, integrated with scipy `solve_ivp` (DOP853,
tolerance 10⁻¹²), sampled at 400 Hz.

- run A: θ1 = θ2 = 150°
- run B: θ1 = 150°, θ2 = 150.001°

The start has enough energy for the arms to flip over (arm 1 turns about 9 times in 8.75 s).

## Trajectories: Lyapunov exponent

Gap between the two runs in (θ1, θ2), in radians; the starting gap is 0.001° = 1.745 × 10⁻⁵ rad.

| t | gap, rad | ln(gap / 1.745×10⁻⁵ rad) |
|---|---|---|
| 0 | 1.745 × 10⁻⁵ | 0 |
| 0.25 s | 4.48 × 10⁻⁵ | 0.94 |
| 0.50 s | 2.09 × 10⁻⁴ | 2.48 |
| 0.75 s | 1.28 × 10⁻³ | 4.30 |
| 1.00 s | 9.24 × 10⁻³ | 6.27 |
| 1.25 s | 0.0332 | 7.55 |
| 1.40 s | 0.175 | 9.21 |

The gap grows exponentially until it reaches the size of the system (about π rad, near 2 s); from then on
the two runs are unrelated motions.

- From runs A and B (slope of ln(gap / starting gap) up to 1.4 s): **λ = 6.6 s⁻¹**, the gap doubles every 0.105 s.
- Benettin method (separation 10⁻⁸, renormalised every 0.01 s, 44 s): **λ = 4.37 s⁻¹**, doubling every 0.16 s.

## SKA

Each run learned as the IBM runs: input the simple return of v = cos(θ2 − θ1), x = sigmoid(4 · r),
Δt = 1/400 s, fresh learner, steps 3 to 3,500 (8.75 s).

| steps 1–3,500 | run A | run B |
|---|---|---|
| arms through 90° | 54 | 58 |
| P one step after a crossing | 0.4508 | 0.4510 |
| P on the other steps (median) | 0.99 | 0.99 |
| entropy minimum | −1.575 at step 1,043 | −1.584 at step 922 |

The gaps |z_A − z_B| (knowledge) and |H_A − H_B| (entropy) grow during the first 2 s, then stay small:
about 0.2 in z (z ≈ 510) and 0.03 in H, while the trajectories keep separating.

## Cubes

Run A on the left, run B on the right, each in its own area (own rotation, zoom, legend, VR button):

| page | view |
|---|---|
| [`sim_ab_P_vr.html`](https://quantiota.github.io/SKA-Double-Pendulum/chaos-test/sim_ab_P_vr.html) | (z, ż, P) |
| [`sim_ab_entropy_vr.html`](https://quantiota.github.io/SKA-Double-Pendulum/chaos-test/sim_ab_entropy_vr.html) | (z, ż, H) |

Colours from the input v: v rising, v falling, v crossing 0 (the arms at 90°).

## Files

In `../scripts/`:

- `simulate.py`: the two runs (`data/sim/sim_a.csv`, `sim_b.csv`) and `results/sim_divergence.png`
- `lyapunov.py`: the Benettin exponent and the SKA gaps (`results/lyapunov.png`)
- `build_cube.py`, `build_side_by_side.py`: the two pages

Learning output: `../results/ska_runsim_a_scale4.csv`, `../results/ska_runsim_b_scale4.csv`.
