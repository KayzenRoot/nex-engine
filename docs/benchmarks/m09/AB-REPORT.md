# NEX M09 · Preset A/B/A — RTX 5050

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-preset-ab` · **Source SHA:** `baf818ef934c418d111091af755e0a19ddd6ac9e`
**Hardware:** NVIDIA GeForce RTX 5050 · Vulkan 1.4.351 · 4.7.2-stable
**Viewport:** 1280×720 · vsync 0 · max_fps 240

## Runs

| Seq | Preset | Run | GPU p50 | GPU p95 | CPU p95 | Pacing p95 | 1% low | Alloc MiB |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | ab-low | 1794650136-34991024 | 0.145 | 0.147 | 0.357 | 4.199 | 228.54 | 22.2 |
| 2 | ab-high | 1794650182-34960454 | 0.740 | 0.746 | 0.467 | 4.222 | 228.34 | 173.2 |
| 3 | ab-low | 1794650224-33725612 | 0.145 | 0.147 | 0.366 | 4.204 | 229.75 | 22.2 |
| 4 | ab-high | 1794653881-34012975 | 0.740 | 0.881 | 0.472 | 4.229 | 226.87 | 173.2 |
| 5 | ab-low | 1794653926-33742838 | 0.146 | 0.152 | 0.346 | 4.216 | 228.73 | 22.2 |
| 6 | ab-high | 1794653968-33563891 | 0.740 | 0.887 | 0.529 | 4.214 | 225.94 | 173.2 |

## Deltas (ab-high vs ab-low median)

- GPU p95: **+499.3%**
- GPU p50: +410.3%
- CPU p95: +32.2%
- Pacing p95: +0.4%
- 1% low: -0.8%

## A/A stability (3 ab-low runs)

- GPU p95 spread: 3.4%
- CPU p95 spread: 5.6%
- Pacing p95 spread: 0.4%
- 1% low spread: 0.5%

## Observações

- ab-high median GPU p95: 0.881 ms vs ab-low median 0.147 ms (+499.3%).
- ab-high median CPU p95: 0.472 ms vs ab-low median 0.357 ms (+32.2%).
- Pacing p95: 4.222 ms vs 4.204 ms (+0.4%); all runs are capped at 240 fps.
- A/A stability across 3 ab-low runs: GPU p95 spread 3.4%, CPU p95 5.6%, 1% low 0.5%.
- The measured difference is a GPU cost of the high preset on this synthetic workload, not a game FPS or quality claim.

## Limitações

- single session; three ab-low runs and three ab-high runs
- synthetic 200-proxy workload at 1280x720; no cross-scene generalization
- max_fps 240 and vsync disabled; frame pacing is capped
- renderer allocation bytes are session history, not device VRAM
- GPU render timing can describe earlier work and is not frame-aligned
- the harness applies a subset of preset_pack.v1 settings
- no FPS gain, quality or universal recommendation is claimed

Relatório gerado por `docs/benchmarks/m09/tools/build_ab.py`; não é benchmark nem claim de ganho.
