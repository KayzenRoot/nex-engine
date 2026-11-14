# NEX-M09-VISUAL-2560-WO-001 | Verdade visual em 2560×1440

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** continuação autônoma autorizada (NEX-ADR-0005); M09 é `BOUNDED_ADMITTED_EVIDENCE_PIPELINE` desde NEX-ADR-0006; M01 é `BOUNDED_ADMITTED_REFERENCE_PIPELINE`.
**Base:** `main` `4f739cd6808677cd7e3780a8bedb295da55e046d`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014 / NEX-ADR-0005. **Risco:** STANDARD (nova captura visual).
**Lock:** `.engineering/context-locks/NEX-M09-VISUAL-2560-WO-001-EXECUTION.json`.

## Objetivo

Fechar a última lacuna de verdade visual documentada: **2560×1440** nas três cenas M01, 2 presets × 3 repetições (18 PNGs). O relatório prova A/A byte-idêntico por SHA, mede a diferença A/B e compara com 1920×1080. Sem nova medição de performance e sem claim de qualidade.

## Escopo

- Nova sessão visual de 18 PNGs em `corridor_static`, `arena_combat` e `dense_city`, 2560×1440, viewport nativo.
- Evidence bundle `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-visual-2560/`: 18 PNGs + manifesto/fatos/análise/SHA-256.
- Núcleo compartilhado `docs/benchmarks/m09/tools/visual_truth.py`; refactor de `build_m01_visual_1920.py` com saída byte-idêntica.
- Builder `build_m01_visual_2560.py`; relatório `m01-visual-2560.v1.json` + Markdown.
- Atlas M09 atualizado para 13 bundles (84 imagens, 435 arquivos).
- `tests/ci/test_m01_visual_2560.py` e ajustes no atlas/enforcement.
- Enforcement de `--check` no job requerido (24 comandos / 21 arquivos).
- Evidência, delta e este WO/lock.
- Promoção de checkpoint em PR documental separado.

## Fora de escopo

- Alterar harness, cenas base, presets, contrato `preset_pack.v1`, renderer, shaders ou `project.godot`.
- Nova medição de performance, animação, câmera dinâmica ou efeitos temporais.
- Resoluções acima de 2560×1440 ou aspect ratios ultrawide.
- Novos parents, runtime, hub, engine, renderização de produção.
- Claims de FPS, qualidade, ganho universal ou generalização cross-device/sessão.

## DoD

- 18 PNGs 2560×1440, 3 canais, todos A/A byte-idênticos por SHA dentro de cada cena/preset.
- A/B changed pixels: 2.996% (corridor), 3.074% (arena), 1.031% (city); mean abs 0.3694/0.3863/0.1524.
- Comparação com 1920: Δ mean abs −11.4%/−8.4%/−14.6%.
- Saída de `build_m01_visual_1920.py` byte-idêntica após o refactor.
- Suítes CI/contratos/telemetria verdes em worktree LF limpo; 24/24 builders `--check`.
- PR protegida com checks verdes e checkpoint pós-merge verificado.

## STOP

- Base/HEAD divergente, PNG com dimensão/hash divergente, A/A não determinístico, divergência na saída do relatório 1920, necessidade de alterar harness/cena ou check vermelho → parar e registrar.
