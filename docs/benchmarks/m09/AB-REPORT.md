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

## Deltas (ab-high vs ab-low median)

- GPU p95: **+407.5%**
- GPU p50: +410.3%
- CPU p95: +29.2%
- Pacing p95: +0.5%
- 1% low: -0.4%

## A/A stability (ab-low run 2 vs run 1)

- GPU p95: +0.0%
- CPU p95: +2.5%
- Pacing p95: +0.1%
- 1% low: +0.5%

## Observações

- ab-high GPU p95: 0.746 ms vs ab-low median 0.147 ms (+407.5%).
- ab-high CPU p95: 0.467 ms vs ab-low median 0.361 ms (+29.2%).
- Pacing p95: 4.222 ms vs 4.201 ms (+0.5%); both runs are capped at 240 fps.
- A/A stability: GPU p95 +0.0%, CPU p95 +2.5%, 1% low +0.5% between the two ab-low runs.
- The measured difference is a GPU cost of the high preset on this synthetic workload, not a game FPS or quality claim.

## Limitações

- single session; one ab-high run and two ab-low runs
- synthetic 200-proxy workload at 1280x720; no cross-scene generalization
- max_fps 240 and vsync disabled; frame pacing is capped
- renderer allocation bytes are session history, not device VRAM
- GPU render timing can describe earlier work and is not frame-aligned
- the harness applies a subset of preset_pack.v1 settings
- no FPS gain, quality or universal recommendation is claimed

Relatório gerado por `docs/benchmarks/m09/tools/build_ab.py`; não é benchmark nem claim de ganho.
