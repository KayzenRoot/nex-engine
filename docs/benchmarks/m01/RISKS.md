# NEX M01 · Riscos e limitações do baseline

**Status:** `FROZEN_PROPOSED` · Nenhum risco abaixo é resolvido por documentação; cada um tem owner e estado.

| ID | Risco | Impacto | Estado / mitigação |
|---|---|---|---|
| R-01 | S04 Run9 (`invalid_monotonic_tick`) sem causa determinada | uma captura inválida; causalidade desconhecida | Documentado; diagnóstico único `NO_DEFECT_REPRODUCED`; captura original preservada. Não alegar causa. |
| R-02 | Negativo de resize não exercitável sob `canvas_items` | controle negativo físico ausente | Limitação aceita pelo Owner; validação de viewport coberta por teste; denial/cancel físicos passaram. |
| R-03 | Pacing não comparável entre sessões (~75 vs ~60 callbacks/s) | comparações cruzadas inválidas | Proibido comparar sessões; usar a mesma sessão/procedimento. |
| R-04 | `RENDERER_ALLOCATION_BYTES` é histórico da sessão e não VRAM | orçamento de memória não confiável | Não usar como VRAM; orçamento de VRAM exige fonte de dispositivo. |
| R-05 | S05 em sessão única, 1 repetição por célula | variabilidade subestimada | Baseline-25 ×3 (spread 0,002 ms); declarar `SINGLE_SESSION`. |
| R-06 | Validador S04 restrito ao Density Ladder; S05 delega | risco de interpretação incorreta | Fronteira documentada; teste prova que o v2 rejeita a cena; S05 delega agregados ao canônico. |
| R-07 | QA-FINDING-001 (RecursionError) | falha não controlada em JSON profundo | **Corrigido** (PR #122, `871fd1b`); teste exige `FramePulseError`. |
| R-08 | Metas 1080p60/120 não medidas | risco de alegação indevida | Marcadas `ASPIRATIONAL_NOT_MEASURED`; nenhum claim. |
| R-09 | Crash histórico M00 `0xC0000005` de causa desconhecida | estabilidade futura | Risco residual aceito pelo Owner; 10/10 starts sem reprodução. |
| R-10 | Memória de GPU via WDDM é device-wide | atribuição ao processo impossível | Documentado; não atribuir VRAM ao processo. |
| R-11 | CI headless/Linux não é benchmark GPU | falsa equivalência | CI usado só como smoke; dados de GPU apenas Windows nativo. |
| R-12 | Evidências históricas e `core.autocrlf` | hashes divergentes em checkout errado | Export byte-exato e validação 18/18; nunca confiar em checkout CRLF. |

## Regra de bloqueio

Qualquer defeito `HIGH`/`CRITICAL` novo, hash divergente, perda de comparabilidade ou alegação de performance sem medição **bloqueia** a aceitação do delta de checkpoint.

## Próximas ações de risco

1. Se M02–M06 forem admitidos, repetir baseline em 1080p antes de qualquer meta de 60 FPS.
2. Se VRAM for gate, adicionar medição de dispositivo atribuível e declarar incerteza.
3. Manter o harness QA em CI; qualquer novo finding exige Correction WO.
