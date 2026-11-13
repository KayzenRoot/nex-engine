# NEX-M01-S04 | RETOMADA R9 — matriz física completa no código medido inalterado

**Status: `ACCEPTED_DOCUMENTED_LIMITATION / READY_FOR_EXACT_HEAD_REVIEW / NO_MERGE`**

- Código medido: `d59c94da13839ba1c6c2e894d4d1147ff3fddc78` (worktree detached byte-exato, `autocrlf=false`; diff de código zero vs head `280beff0` nos 6 arquivos de implementação).
- PR #107: `280beff0…`, OPEN — **não modificada**; nenhum push.
- Godot oficial `4.7.2.stable.official.ed1daf0bf`, binário SHA-256 `ab1824f8…`; RTX 5050, driver 617.14; Forward+/Vulkan; viewport 1280×720; VSync 1; `NEX_GPU_PROFILE_SOURCE_SHA=d59c94da…`.
- Sessão única serial, leases exclusivos `Local\NEX_M01_S04_GPU_PROFILE_WRITER` + `…_RTX5050`; import exit 0; smoke nativo exit 0 com `NEX_NATIVE_IMPORT_SMOKE_PASS`.

## Matriz R9 (12 runs positivos + controles)

| Cenário | Runs | Estado | Amostras pacing | GPU/CPU | Evidência |
|---|---|---:|---|---|---|
| 25 geometry | 3/3 | COMPLETE | 2250×3 (histórico) | MEASURED | R9 original (verificado 18/18 no B3) |
| 100 geometry | 3/3 | COMPLETE | 2250×3 (histórico) | MEASURED | R9 original |
| 200 geometry | 3/3 | COMPLETE | 2250×2 + **1800 (novo)** | MEASURED | `gpu_profile_1794577762-42755782.json` |
| 25 combined | **3/3** | COMPLETE | **1800×3** | MEASURED | `…1794577798…`, `…1794577830…`, `…1794577863…` |
| Denial Combined50 | 1/1 | **PASS (sem export)** | — | — | `COMBINED50-DENIAL.png` (UI: "Combined GPU profiling is limited to 25 proxies") |
| Resize-negative | 0/1 | **NOT_EXERCISABLE** | — | — | diagnóstico `DIAGNOSTIC-gpu_profile_1794578009-41154911.json` |

- **12/12 COMPLETE** com `requested_observation_window_elapsed`, ~30,003 s, validador v2 **PASS** (exit 0) em todas as 5 capturas novas (4 aceitação + 1 diagnóstico).
- Fonte das capturas novas: `source_sha = d59c94da…`; workloads corretos (200/geometry e 25/combined); viewport 1280×720.

## Achado do controle negativo de resize

Redimensionar a janela (SetWindowPos 960×600, `True`) durante e antes da captura **não altera** o viewport medido: a captura feita com a janela em 960×600 exportou `viewport.resolution_px=[1280,720]`. Causa: `display/window/stretch/mode="canvas_items"` fixa o viewport de projeto; a janela escala o canvas, não o viewport. Portanto o teste "redimensionamento da janela durante F11" **não é fisicamente exercitável** sem alterar configuração do projeto — o que mudaria o ambiente congelado e exigiria novo SHA medido + requalificação integral (fora do escopo S04).

Alternativas de controle negativo já exercitadas fisicamente: cancelamento manual via F11 (sem export), cancelamento por mudança de workload (sem export, observado na sessão) e denial Combined50 (sem export).

## Decisão requerida (Owner)

1. **Aceitar a limitação documentada**: matriz 12/12 + denial + cancel, com o resize classificado `NOT_EXERCISABLE_UNDER_CANVAS_ITEMS_STRETCH`; ou
2. **Autorizar micro-WO** para tornar o negativo exercitável (mudança de stretch/config), com novo SHA medido e requalificação completa; ou
3. **Redefinir o controle negativo** formalmente no WO.

## Decisão registrada (Owner delegou a escolha; executor decidiu)

**Opção 1 — aceitar a limitação documentada.** Justificativa: o controle de resize é inexercitável sob `stretch/mode="canvas_items"` sem alterar configuração do projeto, que é read-only no Context Lock; um micro-WO de configuração exigiria novo SHA medido e requalificação integral (desproporcional ao risco, pois a invalidação por mudança de viewport é coberta por teste unitário e os controles físicos de fail-closed — denial Combined50, cancelamento manual e cancelamento por mudança de workload — passaram, todos sem export). Recomendação para WO futuro, se necessário: negativo via resize de viewport interno ou build dedicado com stretch desabilitado.

Enquanto não houver review independente + squash exact-head autorizado: **PR #107 permanece `NO_MERGE`**.

## Integridade e limites

- Nenhuma alteração em `main`, PR #107, canonical, config global ou nas capturas históricas; commit diagnóstico anterior não publicado; bundle local em `nex-engine.executor-pack/reports/b6-artifacts/`.
- `p50` não é afirmado neste relatório como benchmark; os agregados completos estão nos JSONs e a fórmula é recalculada independentemente pelo validador v2.
- Sem alegação de ganho de desempenho, sem nuvem substituindo a máquina física, sem merge.


## Conteúdo deste bundle

- 4 capturas de aceitação COMPLETE + validações v2 (`gpu_profile_*.json`, `*.validation.json`).
- `SUPPORTING-DIAGNOSTIC-viewport-fixed-1280x720.json` (+ validação): captura que comprova viewport fixo com janela 960×600; **não é aceitação**, é suporte ao achado do controle de resize.
- `COMBINED50-DENIAL.png` — evidência visual do denial.
- `LOCAL-SMOKE.log` — smoke nativo com `NEX_NATIVE_IMPORT_SMOKE_PASS`.
- `SESSION-FACTS.txt` — ambiente, SHA, sequência e tempos.
- `SHA256SUMS.txt` — integridade dos arquivos deste diretório.
