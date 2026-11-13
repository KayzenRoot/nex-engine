# NEX M06 · Bottleneck Atlas — S05 Lighting Matrix

**Status:** `EVIDENCE_DERIVED_ATLAS / SINGLE_SESSION / NO_NEW_MEASUREMENT / ADMIN_SOLO_NOT_INDEPENDENT`

**Fonte:** `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-13-s05` · **Code SHA medido:** `0b8388faba69358027780a2cc0ea73d3449eab6d`
**Hardware:** NVIDIA GeForce RTX 5050 · driver vulkan · 4.7.2-stable (official) · vsync 1
**Capturas:** 15 · **Hashes:** PASS (32 arquivos)

## Resumo

- Classificação dominante: **pacing** (15/15 runs).
- Maior GPU p95: **1.194 ms** em `1794590348-461870426`.
- Spread de GPU p50 nas 3 repetições baseline-25: **0.002 ms**.

## Runs

| Cenário | Count | Run | GPU p50 | GPU p95 | CPU p50 | CPU p95 | Pacing p95 | 1% low | Classe | Pressão | Δ GPU p95 |
|---|---:|---|---:|---:|---:|---:|---:|---:|---|---|---:|
| baseline-25 | 25 | 1794589928-41466374 | 0.180 | 0.183 | 0.247 | 0.341 | 17.055 | 54.42 | pacing | cpu | — |
| baseline-25-rep2 | 25 | 1794590383-496606065 | 0.178 | 0.181 | 0.248 | 0.324 | 16.993 | 53.58 | pacing | cpu | — |
| baseline-25-rep3 | 25 | 1794590418-531333619 | 0.178 | 0.181 | 0.245 | 0.329 | 17.014 | 53.80 | pacing | cpu | — |
| baseline-100 | 100 | 1794589963-76452097 | 0.194 | 0.206 | 0.254 | 0.344 | 17.014 | 53.46 | pacing | cpu | — |
| baseline-200 | 200 | 1794589998-111361033 | 0.215 | 0.218 | 0.276 | 0.380 | 17.030 | 53.44 | pacing | cpu | — |
| lights-25 | 25 | 1794590033-146315067 | 0.276 | 0.279 | 0.265 | 0.363 | 16.998 | 54.97 | pacing | cpu | +54.1% |
| lights-100 | 100 | 1794590067-181008316 | 0.296 | 0.301 | 0.278 | 0.373 | 17.007 | 53.61 | pacing | cpu | +46.1% |
| lights-200 | 200 | 1794590102-215966673 | 0.317 | 0.321 | 0.298 | 0.400 | 17.020 | 53.70 | pacing | cpu | +47.2% |
| shadows-25 | 25 | 1794590137-250647244 | 0.456 | 0.460 | 0.352 | 0.475 | 17.167 | 53.09 | pacing | balanced | +154.1% |
| shadows-100 | 100 | 1794590172-285680381 | 0.492 | 0.499 | 0.388 | 0.545 | 17.190 | 52.66 | pacing | balanced | +142.2% |
| shadows-200 | 200 | 1794590207-320548567 | 0.525 | 0.547 | 0.427 | 0.586 | 17.167 | 55.08 | pacing | balanced | +150.9% |
| vfx-25 | 25 | 1794590243-357129786 | 0.226 | 0.236 | 0.260 | 0.351 | 16.990 | 53.14 | pacing | cpu | +30.4% |
| vfx-100 | 100 | 1794590278-392105864 | 0.237 | 0.247 | 0.283 | 0.444 | 17.048 | 53.74 | pacing | cpu | +19.9% |
| vfx-200 | 200 | 1794590313-426899019 | 0.251 | 0.261 | 0.298 | 0.415 | 17.022 | 53.37 | pacing | cpu | +19.7% |
| combined-25 | 25 | 1794590348-461870426 | 1.080 | 1.194 | 0.709 | 0.969 | 17.251 | 54.41 | pacing | gpu | +559.7% |

## Referências baseline

| Count | Runs | GPU p95 mediana | CPU p95 mediana | Pacing p95 mediana |
|---:|---:|---:|---:|---:|
| 25 | 3 | 0.181 | 0.329 | 17.014 |
| 100 | 1 | 0.206 | 0.344 | 17.014 |
| 200 | 1 | 0.218 | 0.380 | 17.030 |

## Observações

- lights-25: +54.1% de GPU p95 vs baseline-25, mantendo o frame limitado por pacing.
- shadows-25: +154.1% de GPU p95 vs baseline-25, mantendo o frame limitado por pacing.
- vfx-25: +30.4% de GPU p95 vs baseline-25, mantendo o frame limitado por pacing.
- combined-25: +559.7% de GPU p95 vs baseline-25; maior custo absoluto da matriz.
- maior GPU p95 absoluto: 1.194 ms em 1794590348-461870426, ainda 16.057 ms abaixo do pacing p95.
- spread de GPU p50 nas 3 repetições baseline-25: 0.002 ms.
- Todas as 15 runs permanecem pacing-bound; nenhuma célula satura o orçamento de GPU no cenário sintético.

## Limitações

- single synthetic session; one repetition per cell except baseline-25 x3
- vsync-limited 60 Hz: pacing classification reflects vsync, not a GPU-bound scene
- GPU render timing can describe earlier work and is not guaranteed to align one-to-one with the current frame
- renderer allocation bytes are session history, not device VRAM, and are not compared across runs
- one_percent_low_fps is callback pacing, not display presentation or input-to-photon latency
- no cross-scene, cross-driver, cross-hardware or cross-session generalization
- no new measurement is performed by this atlas

Atlas gerado por `docs/benchmarks/m06/tools/build_atlas.py`; não é benchmark, não é claim de FPS e não generaliza.
