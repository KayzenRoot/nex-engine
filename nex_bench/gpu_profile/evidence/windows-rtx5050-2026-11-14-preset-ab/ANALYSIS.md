# NEX M09 · Preset A/B/A — análise das capturas

**Status:** `EVIDENCE_BUNDLE / SINGLE_SESSION / MEASURED_COST_OBSERVED / ADMIN_SOLO_NOT_INDEPENDENT`

Fonte: cena isolada `nex_bench/scenes/preset_ab`, presets `ab-low` e `ab-high`, profiler canônico com validador dedicado. As seis capturas foram validadas (`PASS`) e os agregados são recomputados pelo builder `docs/benchmarks/m09/tools/build_ab.py`.

## Sessão

- Data: 2026-11-14 · Windows · RTX 5050 · Vulkan 1.4.351 · Godot 4.7.2-stable.
- Código medido: `baf818ef934c418d111091af755e0a19ddd6ac9e` (cena/presets byte-idênticos na main atual).
- Viewport 1280×720 · vsync 0 · max_fps 240 · 200 proxies · effect_mode lights.
- Sequência L/H/L/H/L/H, 30 s de observação por run.

## Resultados

| Run | Preset | GPU p50 | GPU p95 | CPU p95 | Pacing p95 | 1% low | Alloc MiB |
|---|---|---:|---:|---:|---:|---:|---:|
| 1794650136-34991024 | ab-low | 0.145 | 0.147 | 0.357 | 4.199 | 228.54 | 22.2 |
| 1794650182-34960454 | ab-high | 0.740 | 0.746 | 0.467 | 4.222 | 228.34 | 173.2 |
| 1794650224-33725612 | ab-low | 0.145 | 0.147 | 0.366 | 4.204 | 229.75 | 22.2 |
| 1794653881-34012975 | ab-high | 0.740 | 0.881 | 0.472 | 4.229 | 226.87 | 173.2 |
| 1794653926-33742838 | ab-low | 0.146 | 0.152 | 0.346 | 4.216 | 228.73 | 22.2 |
| 1794653968-33563891 | ab-high | 0.740 | 0.887 | 0.529 | 4.214 | 225.94 | 173.2 |

Medianas `ab-high` vs `ab-low`:
- GPU p95: **+499.3%** (0.147 → 0.881 ms).
- GPU p50: +410.3%.
- CPU p95: +32.2%.
- Pacing p95: +0.4%.
- 1% low: −0.8%.

Estabilidade A/A nas 3 runs `ab-low`: GPU p95 spread 3.4%, CPU p95 5.6%, pacing p95 0.4%, 1% low 0.5%.

## Leitura

O preset alto custa ~6× mais GPU p95 no workload sintético de 200 proxies, mas o frame pacing permanece no cap de 240 fps e o 1% low muda pouco. Isto é **custo medido**, não ganho de FPS, recomendação universal ou prova de qualidade visual.

## Limitações

- Sessão única; 3 runs baixos e 3 altos.
- Cena sintética 1280×720; sem generalização entre cenas/hardware/drivers.
- `max_fps 240` limita o pacing; vsync desligado.
- `RENDERER_ALLOCATION_BYTES` é histórico da sessão, não VRAM do dispositivo.
- Timing de GPU pode descrever trabalho anterior e não é alinhado ao frame.
- O harness aplica um subconjunto de `preset_pack.v1`.
