# NEX M09 · Preset scaling 25/100/200 — análise

**Status:** `EVIDENCE_BUNDLE / SINGLE_SESSION / MEASURED_COST_OBSERVED / ADMIN_SOLO_NOT_INDEPENDENT`

Fonte: cena `nex_bench/scenes/preset_ab`, presets `ab-low`/`ab-high`, 3 repetições por célula (18 capturas), validador dedicado + canônico. Agregados recomputados por `docs/benchmarks/m09/tools/build_scaling.py`.

## Sessão

- Data 2026-11-14 · Windows · RTX 5050 · Vulkan 1.4.351 · Godot 4.7.2-stable.
- Código medido `4e4719ac504ddb0ea7961d5c9d557c745f216990`.
- 1280×720 · vsync 0 · max_fps 240 · effect_mode lights · proxies 25/100/200.
- Sequência por contagem: L/H/L/H/L/H; 30 s por run.

## Medianas por célula

| Count | Preset | Runs | GPU p95 | CPU p95 | Pacing p95 | 1% low |
|---:|---|---:|---:|---:|---:|---:|
| 25 | ab-low | 3 | 0.128 ms | 0.298 ms | 4.249 ms | 224.69 |
| 25 | ab-high | 3 | 0.774 ms | 0.382 ms | 4.269 ms | 222.33 |
| 100 | ab-low | 3 | 0.139 ms | 0.310 ms | 4.264 ms | 223.63 |
| 100 | ab-high | 3 | 0.833 ms | 0.444 ms | 4.274 ms | 221.84 |
| 200 | ab-low | 3 | 0.152 ms | 0.374 ms | 4.274 ms | 218.93 |
| 200 | ab-high | 3 | 0.879 ms | 0.457 ms | 4.256 ms | 222.93 |

Deltas `ab-high` vs `ab-low` por contagem:
- 25 proxies: GPU p95 **+504.7%**.
- 100 proxies: GPU p95 **+499.3%**.
- 200 proxies: GPU p95 **+478.3%** (CPU p95 +22.2%).

Escala do `ab-low` 25→200: GPU p95 +18.7%. Do `ab-high`: +13.6%. Pacing permanece ~4.25 ms (cap 240 fps).

## Leitura

O custo GPU do preset alto é ~5–6× o do baixo nas três contagens; o crescimento com proxies é modesto neste workload sintético. Isto é **custo medido**, não FPS de jogo, ganho ou generalização.

## Limitações

- Sessão única; 3 runs por célula.
- Cena sintética 1280×720; sem generalização entre cenas/hardware/drivers.
- `max_fps 240` limita o pacing; vsync desligado.
- Uma run 200/low tem 1% low outlier (157.39); medianas reportadas.
- Alocação do renderer é histórico da sessão, não VRAM.
- O harness aplica um subconjunto de `preset_pack.v1`.
