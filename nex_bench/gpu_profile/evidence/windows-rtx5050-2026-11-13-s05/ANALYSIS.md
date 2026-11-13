# NEX M01-S05 · Lighting Matrix — análise de capturas

**Status:** `EVIDENCE_BUNDLE / SINGLE_SESSION / NOT_A_BENCHMARK_CLAIM` · auditoria ADMIN_SOLO `NOT_INDEPENDENT`

Validador: `nex_bench/scenes/lighting_matrix/validate_lighting_matrix.py` (recomputa todos os agregados). O validador v2 do S04 é intencionalmente restrito à cena Density Ladder e rejeita esta proveniência; a fronteira é documentada, não contornada.

## Matriz (1 repetição por célula; baseline-25 com 3 repetições)

| Cenário | Count | Run | GPU p50 ms | GPU p95 ms | CPU p50 ms | Pacing p95 ms | 1% low | Alloc MiB |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| baseline-25 | 25 | 1794589928-41466374 | 0.180 | 0.183 | 0.247 | 17.05 | 54.42 | 48.2 |
| baseline-100 | 100 | 1794589963-76452097 | 0.194 | 0.206 | 0.254 | 17.01 | 53.46 | 48.2 |
| baseline-200 | 200 | 1794589998-111361033 | 0.215 | 0.218 | 0.276 | 17.03 | 53.44 | 48.2 |
| lights-25 | 25 | 1794590033-146315067 | 0.276 | 0.279 | 0.265 | 17.00 | 54.97 | 48.2 |
| lights-100 | 100 | 1794590067-181008316 | 0.296 | 0.301 | 0.278 | 17.01 | 53.61 | 48.2 |
| lights-200 | 200 | 1794590102-215966673 | 0.317 | 0.321 | 0.298 | 17.02 | 53.70 | 48.2 |
| shadows-25 | 25 | 1794590137-250647244 | 0.456 | 0.460 | 0.352 | 17.17 | 53.09 | 125.2 |
| shadows-100 | 100 | 1794590172-285680381 | 0.492 | 0.499 | 0.388 | 17.19 | 52.66 | 125.2 |
| shadows-200 | 200 | 1794590207-320548567 | 0.525 | 0.547 | 0.427 | 17.17 | 55.08 | 125.2 |
| vfx-25 | 25 | 1794590243-357129786 | 0.226 | 0.236 | 0.260 | 16.99 | 53.14 | 125.6 |
| vfx-100 | 100 | 1794590278-392105864 | 0.237 | 0.247 | 0.283 | 17.05 | 53.74 | 125.6 |
| vfx-200 | 200 | 1794590313-426899019 | 0.251 | 0.261 | 0.298 | 17.02 | 53.37 | 125.6 |
| combined-25 | 25 | 1794590348-461870426 | 1.080 | 1.194 | 0.709 | 17.25 | 54.41 | 125.6 |
| baseline-25-rep2 | 25 | 1794590383-496606065 | 0.178 | 0.181 | 0.248 | 16.99 | 53.58 | 125.2 |
| baseline-25-rep3 | 25 | 1794590418-531333619 | 0.178 | 0.181 | 0.245 | 17.01 | 53.80 | 125.2 |

## Deltas vs baseline no mesmo count (GPU p95; negativo = menos tempo)

| Cenário | Count | Baseline GPU p95 | Cenário GPU p95 | Delta |
|---|---:|---:|---:|---:|
| lights-25 | 25 | 0.181 | 0.279 | +54.1% |
| lights-100 | 100 | 0.206 | 0.301 | +46.1% |
| lights-200 | 200 | 0.218 | 0.321 | +47.2% |
| shadows-25 | 25 | 0.181 | 0.460 | +154.1% |
| shadows-100 | 100 | 0.206 | 0.499 | +142.2% |
| shadows-200 | 200 | 0.218 | 0.547 | +150.9% |
| vfx-25 | 25 | 0.181 | 0.236 | +30.4% |
| vfx-100 | 100 | 0.206 | 0.247 | +19.9% |
| vfx-200 | 200 | 0.218 | 0.261 | +19.7% |
| combined-25 | 25 | 0.181 | 1.194 | +559.7% |

Variabilidade baseline-25 entre 3 runs: GPU p50 0.178–0.180 ms (spread 0.002 ms).

## Limitações

- Sessão única; 1 repetição por célula (exceto baseline-25 ×3). Não é benchmark e não compara sessões.
- Pacing é intervalo de callbacks `_process`, não apresentação/input-to-photon.
- `RENDERER_ALLOCATION_BYTES` é alocação do renderer, não VRAM total do dispositivo.
- Sem conclusão de ganho de performance: a matriz mede custo nativo das opções Godot no cenário sintético.
- Validador S05 independente recalculou todos os agregados a partir dos JSONs brutos; SHA-256 no bundle.
- `RENDERER_ALLOCATION_BYTES` é histórico da sessão (48,2 MiB no início vs 125,2 MiB após presets com sombra/VFX); não é comparável entre runs sequenciais nem representa VRAM total.
