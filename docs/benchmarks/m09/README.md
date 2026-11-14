# NEX M09 · Preset benchmark pack

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

Este diretório versiona os relatórios A/B/A e de escala dos presets `ab-low` e `ab-high` na cena isolada `nex_bench/scenes/preset_ab` e nas três cenas base M01.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `ab.v1.json` / `AB-REPORT.md` | A/B/A com 6 runs (3 por preset), medianas, deltas, spread A/A e limitações. |
| `scaling.v1.json` / `SCALING-REPORT.md` | Matriz 25/100/200 proxies × 2 presets × 3 runs, medianas por célula e escala. |
| `m01-ab.v1.json` / `M01-AB-REPORT.md` | A/B/A nas cenas `corridor_static`, `arena_combat` e `dense_city`, 3 runs por preset por cena, 100 meshes por cena. |
| `tools/build_ab.py` | Builder determinístico do A/B/A. |
| `tools/build_scaling.py` | Builder determinístico da matriz de escala. |
| `tools/build_m01_ab.py` | Builder determinístico do A/B/A nas cenas M01. |
| `tools/preset_report.py` | Loaders e estatística compartilhados pelos builders. |

## Fontes

- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-preset-ab/`: 6 capturas + 6 validações + manifesto/fatos/análise/SHA-256.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-preset-scaling/`: 18 capturas + 18 validações + manifesto/fatos/análise/SHA-256.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-ab/`: 18 capturas + 18 validações + manifesto/fatos/análise/SHA-256.

## Uso

```powershell
python docs/benchmarks/m09/tools/build_ab.py
python docs/benchmarks/m09/tools/build_ab.py --check
python docs/benchmarks/m09/tools/build_scaling.py
python docs/benchmarks/m09/tools/build_scaling.py --check
python docs/benchmarks/m09/tools/build_m01_ab.py
python docs/benchmarks/m09/tools/build_m01_ab.py --check
```

## Limitações

- Sessão única; 3 runs por preset no A/B/A e 3 por célula na escala e nas cenas M01.
- Workload sintético em 1280×720; no modo M01 os fillers podem sobrepor props das cenas.
- Sem generalização entre cenas/hardware/drivers.
- `max_fps 240`, vsync desligado; pacing é limitado pelo cap.
- Alocação do renderer é histórico da sessão, não VRAM.
- O harness aplica um subconjunto de `preset_pack.v1`.
- Nenhum claim de FPS de jogo, ganho universal ou qualidade visual.
