# NEX-M06-OBS-WO-001 | Observações performance.v1 a partir das capturas M09

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** NEX-ADR-0005 (autonomia contínua) sobre o contrato M06 existente.
**Base:** `main` `3aa83afaabbe3a0b65afb3d9250158b66da6dde6`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD (conversão de evidência).
**Lock:** `.engineering/context-locks/NEX-M06-OBS-WO-001-EXECUTION.json`.

## Objetivo

Converter 12 capturas M09 já integradas em observações válidas de `performance.v1`, com campos indisponíveis explícitos, classificação de bottleneck e proveniência, e publicar um bundle verificado. Isto exercita o contrato M06 sobre dados medidos sem nova captura e sem admitir o parent M06.

## Escopo

- `docs/benchmarks/m06/**`: conversor determinístico e bundle `observations/m09-observations.v1.json`.
- `tests/ci/test_m06_observations.py`: validação de schema/coerência, valores e reprodutibilidade.
- Evidência, delta e este WO/lock.

## Fora de escopo

- Alterar o contrato M06, `project.godot`, hub, renderer, engine ou CI.
- Nova captura, nova medição ou generalização.
- M06 parent admission.

## DoD

- 12 observações `performance.v1` válidas, com IDs únicos, `evidence_uri` e proveniência.
- Campos não medidos marcados `UNAVAILABLE` com razão; nenhum valor fabricado.
- Classificação de bottleneck coerente com as métricas medidas.
- Conversor reproduzível, testes verdes, suítes completas verdes em worktree LF limpo.
- PR protegida com checks verdes e checkpoint pós-merge.

## STOP

- Captura ausente, schema/coerência falhar, contagem divergir ou conversor não reproduzir → parar e registrar.
