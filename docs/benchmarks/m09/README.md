# NEX M09 · Preset benchmark pack

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

Este diretório versiona os relatórios A/B/A e de escala dos presets `ab-low` e `ab-high` na cena isolada `nex_bench/scenes/preset_ab` e nas três cenas base M01.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `ab.v1.json` / `AB-REPORT.md` | A/B/A com 6 runs (3 por preset), medianas, deltas, spread A/A e limitações. |
| `scaling.v1.json` / `SCALING-REPORT.md` | Matriz 25/100/200 proxies × 2 presets × 3 runs, medianas por célula e escala. |
| `m01-ab.v1.json` / `M01-AB-REPORT.md` | A/B/A nas cenas `corridor_static`, `arena_combat` e `dense_city`, 3 runs por preset por cena, 100 meshes por cena. |
| `m01-visual.v1.json` / `M01-VISUAL-REPORT.md` | Verdade visual das três cenas M01: 18 PNGs, A/A exato por SHA e diferenças A/B de pixels. |
| `res-scaling.v1.json` / `RES-SCALING-REPORT.md` | Escala de resolução 960×540/1280×720/1920×1080 em `arena_combat`, 3 runs por preset por resolução. |
| `interaction.v1.json` / `INTERACTION-REPORT.md` | Interação 50/100 proxies × 960×540/1920×1080 em `arena_combat`, 3 runs por preset por célula. |
| `cross-scene.v1.json` / `CROSS-SCENE-REPORT.md` | Interação 50/100 proxies × 960×540/1920×1080 em `corridor_static` e `dense_city`, 3 runs por preset por célula. |
| `interaction-200.v1.json` / `INTERACTION-200-REPORT.md` | 200 proxies × 960×540/1920×1080 em `arena_combat`, com contexto 100→200 de sessão separada. |
| `measurement-atlas.v1.json` / `MEASUREMENT-ATLAS.md` | Índice verificado dos oito bundles M09, totais, achados cross-experiment e perguntas abertas. |
| `tools/build_ab.py` | Builder determinístico do A/B/A. |
| `tools/build_scaling.py` | Builder determinístico da matriz de escala. |
| `tools/build_m01_ab.py` | Builder determinístico do A/B/A nas cenas M01. |
| `tools/build_m01_visual.py` | Builder determinístico do relatório visual M01. |
| `tools/build_res_scaling.py` | Builder determinístico da escala de resolução. |
| `tools/build_interaction.py` | Builder determinístico da interação proxies × resolução. |
| `tools/build_cross_scene.py` | Builder determinístico da interação em múltiplas cenas. |
| `tools/build_interaction_200.py` | Builder determinístico do check de 200 proxies. |
| `tools/build_measurement_atlas.py` | Builder determinístico do atlas de medições. |
| `tools/png_image.py` | Decoder PNG mínimo e comparador de pixels. |
| `tools/preset_report.py` | Loaders e estatística compartilhados pelos builders. |

## Fontes

- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-preset-ab/`: 6 capturas + 6 validações + manifesto/fatos/análise/SHA-256.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-preset-scaling/`: 18 capturas + 18 validações + manifesto/fatos/análise/SHA-256.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-ab/`: 18 capturas + 18 validações + manifesto/fatos/análise/SHA-256.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-visual/`: 18 PNGs + manifesto/fatos/análise/SHA-256.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-res-scaling/`: 18 capturas + 18 validações + manifesto/fatos/análise/SHA-256.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-interaction/`: 24 capturas + 24 validações + manifesto/fatos/análise/SHA-256.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-cross-scene/`: 48 capturas + 48 validações + manifesto/fatos/análise/SHA-256.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-interaction-200/`: 12 capturas + 12 validações + manifesto/fatos/análise/SHA-256.

## Uso

```powershell
python docs/benchmarks/m09/tools/build_ab.py
python docs/benchmarks/m09/tools/build_ab.py --check
python docs/benchmarks/m09/tools/build_scaling.py
python docs/benchmarks/m09/tools/build_scaling.py --check
python docs/benchmarks/m09/tools/build_m01_ab.py
python docs/benchmarks/m09/tools/build_m01_ab.py --check
python docs/benchmarks/m09/tools/build_m01_visual.py
python docs/benchmarks/m09/tools/build_m01_visual.py --check
python docs/benchmarks/m09/tools/build_res_scaling.py
python docs/benchmarks/m09/tools/build_res_scaling.py --check
python docs/benchmarks/m09/tools/build_interaction.py
python docs/benchmarks/m09/tools/build_interaction.py --check
python docs/benchmarks/m09/tools/build_cross_scene.py
python docs/benchmarks/m09/tools/build_cross_scene.py --check
python docs/benchmarks/m09/tools/build_interaction_200.py
python docs/benchmarks/m09/tools/build_interaction_200.py --check
python docs/benchmarks/m09/tools/build_measurement_atlas.py
python docs/benchmarks/m09/tools/build_measurement_atlas.py --check
```

## Limitações

- Sessão única; 3 runs por preset no A/B/A e 3 por célula na escala e nas cenas M01.
- Workload sintético em 1280×720; no modo M01 os fillers podem sobrepor props das cenas.
- Comparação visual é byte a byte de RGB; não modela percepção humana, color space ou calibração.
- A escala de resolução usa viewport nativo (stretch desabilitado) e vai até 1920×1080; 2560×1440 não é coberto.
- A interação usa 50/100 proxies porque 25 exigiria remover geometria da cena base.
- A interação cross-scene cobre `corridor_static` e `dense_city`; `arena_combat` tem relatório próprio.
- O check de 200 proxies usa contexto 100→200 de uma sessão separada, claramente rotulado.
- O atlas é uma síntese de evidência já integrada; não adiciona capturas nem generalização.
- Sem generalização entre cenas/hardware/drivers.
- `max_fps 240`, vsync desligado; pacing é limitado pelo cap.
- Alocação do renderer é histórico da sessão, não VRAM.
- O harness aplica um subconjunto de `preset_pack.v1`.
- Nenhum claim de FPS de jogo, ganho universal ou qualidade visual.
