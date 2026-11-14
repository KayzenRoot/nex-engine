# NEX-M06-ADVISOR-WO-001 | Advisórios de performance a partir das observações M09

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** NEX-ADR-0005 (autonomia contínua) sobre o contrato M06 existente.
**Base:** `main` `622037479c9aa56171612cffacbd8225f1de2215`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD (síntese de evidência).
**Lock:** `.engineering/context-locks/NEX-M06-ADVISOR-WO-001-EXECUTION.json`.

## Objetivo

Consumir as 12 observações `performance.v1` já integradas e produzir advisórios determinísticos com headroom de render, participação GPU/CPU no frame, recomendação segura e limitações explícitas. Nenhuma nova medição, nenhum claim de FPS ou admissão do parent M06.

## Escopo

- `docs/benchmarks/m06/**`: `advisories.v1.json`, `ADVISORIES.md` e builder determinístico.
- `tests/ci/test_m06_advisories.py`: contagens, valores, semântica de não-claim e reprodutibilidade.
- Evidência, delta e este WO/lock.

## Fora de escopo

- Alterar o contrato M06, `nex_modules/**`, `project.godot`, hub, renderer, engine ou CI.
- Nova captura, nova medição, recomendação de hardware ou generalização.
- M06 parent admission.

## DoD

- 12 advisórios com `observation_id`, bottleneck, headroom, shares e recomendação.
- Todos os advisórios explicitam que o run é pacing-bound e que headroom não prova capacidade em cap menor.
- Nenhum claim de FPS, qualidade ou ganho; nenhum campo medido inventado.
- Builder reproduzível, testes verdes, suítes completas verdes em worktree LF limpo.
- PR protegida com checks verdes e checkpoint pós-merge.

## STOP

- Observação ausente/inválida, contagem divergir, recomendação gerar claim proibido ou builder não reproduzir → parar e registrar.
