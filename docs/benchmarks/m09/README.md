# NEX M09 · Preset benchmark pack

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

Este diretório versiona os relatórios A/B/A e de escala dos presets `ab-low` e `ab-high` na cena isolada `nex_bench/scenes/preset_ab`.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `ab.v1.json` / `AB-REPORT.md` | A/B/A com 6 runs (3 por preset), medianas, deltas, spread A/A e limitações. |
| `scaling.v1.json` / `SCALING-REPORT.md` | Matriz 25/100/200 proxies × 2 presets × 3 runs, medianas por célula e escala. |
| `tools/build_ab.py` | Builder determinístico do A/B/A. |
| `tools/build_scaling.py` | Builder determinístico da matriz de escala. |

## Fontes

- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-preset-ab/`: 6 capturas + 6 validações + manifesto/fatos/análise/SHA-256.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-preset-scaling/`: 18 capturas + 18 validações + manifesto/fatos/análise/SHA-256.

## Uso

```powershell
python docs/benchmarks/m09/tools/build_ab.py
python docs/benchmarks/m09/tools/build_ab.py --check
python docs/benchmarks/m09/tools/build_scaling.py
python docs/benchmarks/m09/tools/build_scaling.py --check
```

## Limitações

- Sessão única; 3 runs por preset no A/B/A e 3 por célula na escala.
- Workload sintético em 1280×720; sem generalização entre cenas/hardware/drivers.
- `max_fps 240`, vsync desligado; pacing é limitado pelo cap.
- Alocação do renderer é histórico da sessão, não VRAM.
- O harness aplica um subconjunto de `preset_pack.v1`.
- Nenhum claim de FPS de jogo, ganho universal ou qualidade visual.
