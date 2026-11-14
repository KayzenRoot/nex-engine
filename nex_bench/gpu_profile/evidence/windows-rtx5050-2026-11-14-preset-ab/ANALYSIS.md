# NEX M09 · Preset A/B/A — análise das capturas

**Status:** `EVIDENCE_BUNDLE / SINGLE_SESSION / MEASURED_COST_OBSERVED / ADMIN_SOLO_NOT_INDEPENDENT`

Fonte: cena isolada `nex_bench/scenes/preset_ab`, presets `ab-low` e `ab-high`, profiler canônico com validador dedicado. As três capturas foram validadas (`PASS`) e os agregados são recomputados pelo builder `docs/benchmarks/m09/tools/build_ab.py`.

## Sessão

- Data: 2026-11-14 · Windows · RTX 5050 · Vulkan 1.4.351 · Godot 4.7.2-stable.
- Source SHA: `baf818ef934c418d111091af755e0a19ddd6ac9e`.
- Viewport 1280×720 · vsync 0 · max_fps 240 · 200 proxies · effect_mode lights.
- Sequência A/B/A: `ab-low` → `ab-high` → `ab-low`, 30 s de observação por run.

## Resultados

| Run | Preset | GPU p50 | GPU p95 | CPU p95 | Pacing p95 | 1% low | Alloc MiB |
|---|---|---:|---:|---:|---:|---:|---:|
| 1794650136-34991024 | ab-low | 0.145 | 0.147 | 0.357 | 4.199 | 228.54 | 22.2 |
| 1794650182-34960454 | ab-high | 0.740 | 0.746 | 0.467 | 4.222 | 228.34 | 173.2 |
| 1794650224-33725612 | ab-low | 0.145 | 0.147 | 0.366 | 4.204 | 229.75 | 22.2 |

Deltas `ab-high` vs mediana `ab-low`:
- GPU p95: **+407.5%** (0.147 → 0.746 ms).
- GPU p50: +410.3%.
- CPU p95: +29.2%.
- Pacing p95: +0.5%.
- 1% low: −0.4%.

Estabilidade A/A: GPU p95 +0.0%, CPU p95 +2.5%, pacing p95 +0.1%, 1% low +0.5%.

## Leitura

O preset alto custa ~5,1× mais GPU p95 no workload sintético de 200 proxies, mas o frame pacing permanece no cap de 240 fps e o 1% low não muda de forma material. Isto é **custo medido**, não ganho de FPS, recomendação universal ou prova de qualidade visual.

## Limitações

- Sessão única; 1 run alto e 2 runs baixos.
- Cena sintética 1280×720; sem generalização entre cenas/hardware/drivers.
- `max_fps 240` limita o pacing; vsync desligado.
- `RENDERER_ALLOCATION_BYTES` é histórico da sessão, não VRAM do dispositivo.
- Timing de GPU pode descrever trabalho anterior e não é alinhado ao frame.
- O harness aplica um subconjunto de `preset_pack.v1`.
