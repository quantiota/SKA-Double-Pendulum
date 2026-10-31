#!/usr/bin/env python3
"""Add a replay (play / pause / speed / position) to the pendulum cube, so the path can be followed
step by step. The cube stays one standalone file. The points appear in frame order; a white head
marks the current step, a trail joins the last steps, and the whole path walked so far stays as
thin, faint segments. Timing: one camera frame per step, 400 steps/s = real time (1x).
Adapted from SKA-Genomics-Human/scripts/add_replay.py.

    python add_replay.py vr/<cube>_vr.html results/<run>.csv vr/<cube>_vr_replay.html
"""
import json
import sys

import numpy as np
import pandas as pd

src, csv, out = sys.argv[1:4]
TRAIL = 12                                    # steps joined by the trail
s = open(src, encoding="utf-8").read()
i = s.find("const D ="); e = s.find("};", i) + 1
D = json.loads(s[i + 9:e])

# chain position of every cube point: the cube's points are matched to the run on z (knowledge)
d = pd.read_csv(csv)
z, cz = d.knowledge.round(2).to_numpy(), np.array(D["z"])
off = next(o for o in range(len(z) - len(cz) + 1) if np.all(np.abs(z[o:o + len(cz)] - cz) < 0.006))
D["ci"] = (d.chain_index if "chain_index" in d else d.step_index).to_numpy()[off:off + len(cz)].astype(int).tolist()
s = s[:i] + "const D = " + json.dumps(D, separators=(",", ":"), ensure_ascii=False) + ";" + s[e + 1:]

css = """  #player { position:absolute; left:50%; transform:translateX(-50%); bottom:72px; display:flex; align-items:center; gap:8px; background:rgba(18,19,23,.9); border:1px solid var(--line); border-radius:10px; padding:8px 12px; font-size:12px; width:min(680px, calc(100% - 32px)); box-sizing:border-box; }
  #player button, #player select { background:#22232a; color:var(--ink); border:1px solid var(--line); border-radius:6px; padding:4px 8px; font-size:12px; cursor:pointer; }
  #player input[type=range] { flex:1; min-width:60px; accent-color:#e87ba4; }
  #player .clock { color:var(--ink2); white-space:nowrap; font-variant-numeric:tabular-nums; min-width:190px; text-align:right; }
  #hint { bottom:128px !important; }
"""
s = s.replace("</style>", css + "</style>", 1)
player = """<div id="player">
  <button id="restart" title="Start again">⏮</button>
  <button id="play" title="Play / pause">▶ Play</button>
  <button id="back" title="One step back">◀</button>
  <button id="fwd" title="One step forward">▶|</button>
  <select id="speed" title="Steps per second"><option value="1">1 step/s</option><option value="2">2 steps/s</option><option value="5" selected>5 steps/s</option><option value="10">10 steps/s</option><option value="25">25 steps/s</option><option value="100">100 steps/s</option><option value="400">400 steps/s (1×, real time)</option></select>
  <input id="pos" type="range" min="1" max="1" value="1" title="Position in the chain">
  <span class="clock" id="clock"></span>
</div>
"""
assert '<div id="hint">' in s
s = s.replace('<div id="hint">', player + '<div id="hint">', 1)
s = s.replace("Desktop: drag to rotate", "Replay: ▶ follows the path step by step (◀ ▶| one step). Desktop: drag to rotate", 1)

js = """
// ---- replay: the points appear in chain order; head = current step, trail = the last steps ----
const TRAIL = __TRAIL__;
let shownN = N, playing = false, acc = 0, last = performance.now();
const head = new THREE.Mesh(new THREE.SphereGeometry(0.02, 16, 12), new THREE.MeshBasicMaterial({ color: 0xffffff }));
head.visible = false; plot.add(head);
const trailGeo = new THREE.BufferGeometry();
trailGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(TRAIL * 3), 3));
const trail = new THREE.Line(trailGeo, new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.7 }));
trail.visible = false; plot.add(trail);
// the whole path walked so far stays as thin, faint segments
const pathPos = new Float32Array(N * 3);
for (let i = 0; i < N; i++) { pathPos[3*i] = pos[3*i]; pathPos[3*i+1] = toY(D.p[i]); pathPos[3*i+2] = pos[3*i+2]; }
const pathGeo = new THREE.BufferGeometry();
pathGeo.setAttribute('position', new THREE.BufferAttribute(pathPos, 3));
const path = new THREE.Line(pathGeo, new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.12 }));
plot.add(path);
const posEl = document.getElementById('pos'), playEl = document.getElementById('play'),
      speedEl = document.getElementById('speed'), clockEl = document.getElementById('clock');
posEl.max = N; posEl.value = N;
function setShown(n) {
  shownN = Math.max(1, Math.min(N, n));
  geo.setDrawRange(0, shownN);
  const j = shownN - 1, a = Math.max(0, shownN - TRAIL), tp = trailGeo.attributes.position.array;
  for (let i = a, c = 0; i < shownN; i++, c++) { tp[3*c] = pos[3*i]; tp[3*c+1] = toY(D.p[i]); tp[3*c+2] = pos[3*i+2]; }
  trailGeo.setDrawRange(0, shownN - a); trailGeo.attributes.position.needsUpdate = true;
  pathGeo.setDrawRange(0, shownN);
  head.position.set(pos[3*j], toY(D.p[j]), pos[3*j+2]);
  head.visible = trail.visible = shownN < N || playing;
  posEl.value = shownN;
  clockEl.innerHTML = `step ${shownN} / ${N} · <b style="color:${D.colors[D.t[j]]}">${D.names[D.t[j]]}</b> · ${D.hmin !== undefined ? 'H' : 'P'} ${D.p[j].toFixed(3)} · t ${(D.ci[j] / 400).toFixed(3)} s`;
}
function setPlaying(v) { playing = v; playEl.textContent = v ? '❚❚ Pause' : '▶ Play'; last = performance.now(); acc = 0; }
playEl.onclick = () => { if (!playing && shownN >= N) setShown(1); setPlaying(!playing); };
document.getElementById('restart').onclick = () => { setShown(1); setPlaying(true); };
document.getElementById('back').onclick = () => { setPlaying(false); setShown(shownN - 1); };
document.getElementById('fwd').onclick = () => { setPlaying(false); setShown(shownN + 1); };
posEl.oninput = () => { setPlaying(false); setShown(+posEl.value); };
function tick() {
  const now = performance.now(), dt = (now - last) / 1000; last = now;
  if (!playing) return;
  acc += dt * +speedEl.value;
  const k = Math.floor(acc);
  if (k > 0) { acc -= k; setShown(shownN + k); }
  if (shownN >= N) setPlaying(false);
}
setShown(N);
""".replace("__TRAIL__", str(TRAIL))
anchor = "recolor();\naddEventListener('resize'"
assert anchor in s
s = s.replace(anchor, js + anchor, 1)
loop = "renderer.setAnimationLoop(() => { controls.update();"
assert loop in s
s = s.replace(loop, "renderer.setAnimationLoop(() => { tick(); controls.update();", 1)
s = s.replace("<title>Transition Probability VR</title>", "<title>Transition Probability Replay</title>", 1)
s = s.replace("<title>Human HBB normal</title>", "<title>Human HBB normal replay</title>", 1)
s = s.replace("<title>Human HBB sickle</title>", "<title>Human HBB sickle replay</title>", 1)
open(out, "w", encoding="utf-8").write(s)
print("saved", out, "| points", len(D["p"]), "| chain", D["ci"][0], "→", D["ci"][-1])
