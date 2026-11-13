# NEX M06 · Bottleneck Atlas

**Status:** `EVIDENCE_DERIVED_ATLAS / SINGLE_SESSION / NO_NEW_MEASUREMENT / ADMIN_SOLO_NOT_INDEPENDENT`

Este diretório transforma as 15 capturas S05 já publicadas do Lighting Matrix em um atlas de gargalos reproduzível, alinhado ao vocabulário de `contracts/m06/performance.v1.schema.json`.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `atlas.v1.json` | Atlas legível por máquina: 15 runs, células, referências baseline, deltas, classificação, limitações. |
| `ATLAS.md` | Relatório humano com tabelas e observações. |
| `tools/build_atlas.py` | Builder stdlib determinístico; verifica hashes, recomputa agregados e reescreve os dois artefatos. |

## Metodologia

1. Verifica os 32 arquivos de `SHA256SUMS.txt` contra os blobs LF do Git. Capturas de medição exigem hash estrito; documentação/validação aceitam a variante CRLF original.
2. Lê a tabela publicada em `ANALYSIS.md` para mapear cada `run_id` ao cenário e à contagem.
3. Recarrega cada captura bruta (`nex_gpu_render_profile.v2`), exige `run_status=COMPLETE`, `source_sha` válido e todas as séries `MEASURED`.
4. Confere o JSON de validação S05 contra os agregados recomputados (p50/p95/p99/mean, 1% low, duração).
5. Classifica o gargalo: `pacing` quando há vsync ou pacing p50 ≥ 15 ms; caso contrário `gpu`/`cpu` por participação no frame. `render_pressure` compara GPU e CPU dentro do trabalho de render.
6. Calcula deltas vs a mediana baseline da mesma contagem (3 runs em 25; 1 run em 100/200).
7. Falha em qualquer hash, run ausente, status não-COMPLETE ou divergência de validação.

## Uso

```powershell
python docs/benchmarks/m06/tools/build_atlas.py
python docs/benchmarks/m06/tools/build_atlas.py --check
```

`--check` não escreve: confirma que `atlas.v1.json` e `ATLAS.md` correspondem ao builder.

## Limitações

- Sessão sintética única; 1 repetição por célula, exceto baseline-25 ×3.
- VSync 60 Hz: todas as runs são pacing-bound; isso não mede um cenário GPU-bound.
- Timings de GPU podem descrever trabalho anterior ao frame atual.
- `RENDERER_ALLOCATION_BYTES` é histórico da sessão, não VRAM do dispositivo; não é comparado entre runs.
- `one_percent_low_fps` é pacing de callbacks, não apresentação/input-to-photon.
- Nenhuma captura nova, nenhum benchmark, nenhuma generalização entre cena/driver/hardware/sessão.
