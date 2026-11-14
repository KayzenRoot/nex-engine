# NEX M09 · 200-proxy interaction — RTX 5050

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-interaction-200` · **Source SHA:** `c1b73743c0c95d9fb8867079cb91fb74cfc03d49`
**Hardware:** NVIDIA GeForce RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · 4.7.2-stable
**Workload:** M01 Arena A/B/A · 200 proxies · native resolution

## Células (medianas de 3 runs)

| Proxies | Resolução | Preset | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 200 | 960×540 | ab-low | 0.095 | 0.098 | 0.221 | 0.357 | 4.247 | 224.05 |
| 200 | 960×540 | ab-high | 0.315 | 0.322 | 0.468 | 0.503 | 4.264 | 224.91 |
| 200 | 1920×1080 | ab-low | 0.145 | 0.157 | 0.160 | 0.361 | 4.289 | 225.70 |
| 200 | 1920×1080 | ab-high | 0.838 | 0.845 | 1.052 | 0.518 | 4.294 | 225.11 |

## Deltas ab-high vs ab-low (GPU p95)

- 200/960x540: **+228.6%** (CPU p95 +40.9%, 1% low +0.4%).
- 200/1920x1080: **+438.2%** (CPU p95 +43.5%, 1% low -0.3%).

## Escala de resolução 960×540 → 1920×1080 (GPU p95)

- ab-low: +60.2%.
- ab-high: +162.4%.

## Contexto 100 → 200 proxies (sessão diferente, GPU p95)

- 960×540: ab-low +2.1%, ab-high +2.5%.
- 1920×1080: ab-low +9.0%, ab-high +2.3%.

## Observações

- At 200 proxies, resolution scaling 960x540 to 1920x1080 raises GPU p95 by +60.2% (ab-low) and +162.4% (ab-high).
- Going from 100 to 200 proxies changes GPU p95 by only +2.1%/+2.5% at 960x540 and +9.0%/+2.3% at 1920x1080.
- High vs low GPU p95: +228.6% at 960x540 and +438.2% at 1920x1080.
- The pixel-bound pattern holds at 200 proxies; the 100-proxy context is from a different session and is not a same-session comparison.
- CPU p95 is 0.357/0.503 ms at 960x540 and 0.361/0.518 ms at 1920x1080, higher than the 50/100 cells.
- Pacing remains near 4.25-4.29 ms and 1% low deltas are within -0.3% to +0.4%; no gain is claimed.

## Limitações

- single session on one RTX 5050; no cross-device or cross-session generalization
- one scene and one proxy count (200); 50/100 context is from a different session
- two resolutions only; 2560x1440 is not covered
- native resolution disables the project's canvas_items stretch mode
- max_fps 240 and vsync disabled; frame pacing is capped
- the harness applies a subset of preset_pack.v1 settings
- no FPS gain, quality or universal recommendation is claimed

Relatório gerado por `docs/benchmarks/m09/tools/build_interaction_200.py`; não é benchmark nem claim de ganho.
