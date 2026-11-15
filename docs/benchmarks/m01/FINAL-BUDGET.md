# NEX M01 · Orçamento de performance 1080p (aprovado)

**Status:** `OWNER_APPROVED / MEASURED_ON_REFERENCE_LAB / NO_GENERAL_FPS_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m01-perf-1080` · **Source SHA:** `900d2b2d031a87048702625a1e98bc50905bc663`
**Hardware:** NVIDIA GeForce RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · 4.7.2-stable
**Viewport:** 1920×1080 · VSync 0 · max_fps 240

| Cena | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low | Alloc MiB | Checks |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| corridor_static | 0.128 | 0.139 | 0.249 | 0.395 | 4.273 | 223.26 | 34.5 | PASS |
| arena_combat | 0.140 | 0.151 | 0.267 | 0.382 | 4.291 | 224.27 | 34.6 | PASS |
| dense_city | 0.110 | 0.122 | 0.151 | 0.363 | 4.255 | 223.76 | 34.5 | PASS |

## Orçamento aprovado

| Métrica | Teto |
|---|---:|
| GPU p95 | 1.00 ms |
| CPU p95 | 2.00 ms |
| Pacing p95 (60 FPS) | 16.67 ms |
| 1% low (60 FPS) | 60 FPS |
| Pacing p95 (120 FPS experimental) | 8.33 ms |
| 1% low (120 FPS experimental) | 120 FPS |

## Observações

- all 9 runs are 1920x1080 native Forward+/Vulkan on the RTX 5050
- GPU p95 medians are 0.121-0.151 ms and CPU p95 medians are 0.361-0.476 ms
- pacing p95 medians are 4.246-4.296 ms and 1% low medians are 223.26-225.98 FPS
- the 60 FPS and experimental 120 FPS pacing budgets are met on this light workload
- the 240 FPS cap and VSync-off settings mean this is not a display-presentation claim

## Limitações

- single session, one GPU and driver
- 100-mesh light workload; no dense-game or cross-device generalization
- callback pacing is not input-to-photon or display presentation
- allocation is renderer-side and session-history, not device VRAM

**Decisão do Owner:** `OWNER_APPROVED` em 2026-11-15 — Owner authorized finalizing the base modules starting with M01 and explicitly approved closing the M01 budget decision.

Gerado por `docs/benchmarks/m01/tools/build_performance_budget.py`; não é benchmark de jogo ou de hardware arbitrário.
