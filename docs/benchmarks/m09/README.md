# NEX M09 · Preset A/B/A benchmark pack

**Status:** `MEASURED_COST_OBSERVED / SINGLE_SESSION / NO_GENERALIZATION / ADMIN_SOLO_NOT_INDEPENDENT`

Este diretório versiona o relatório A/B/A dos presets `ab-low` e `ab-high` na cena isolada `nex_bench/scenes/preset_ab`.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `ab.v1.json` | Relatório legível por máquina: 3 runs, baseline low, deltas, estabilidade A/A e limitações. |
| `AB-REPORT.md` | Relatório humano com tabelas e observações. |
| `tools/build_ab.py` | Builder determinístico; lê as capturas e o manifesto, recomputa agregados e escreve os dois artefatos. |

## Fonte

`nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-preset-ab/` contém as 3 capturas brutas, os 3 JSONs de validação, o manifesto de runs, os fatos da sessão, a análise e `SHA256SUMS.txt`.

## Uso

```powershell
python docs/benchmarks/m09/tools/build_ab.py
python docs/benchmarks/m09/tools/build_ab.py --check
```

`--check` confirma que `ab.v1.json` e `AB-REPORT.md` correspondem às capturas e ao manifesto.

## Limitações

- Sessão única; 1 run `ab-high` e 2 runs `ab-low`.
- Workload sintético de 200 proxies em 1280×720; sem generalização entre cenas/hardware/drivers.
- `max_fps 240`, vsync desligado; pacing é limitado pelo cap.
- Alocação do renderer é histórico da sessão, não VRAM.
- O harness aplica um subconjunto de `preset_pack.v1`.
- Nenhum claim de FPS de jogo, ganho universal ou qualidade visual.
