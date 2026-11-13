# NEX-M06-CONTRACT-WO-001 | Contrato de performance v1

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** Autorização permanente do Owner; fecha a cadeia de interfaces M03–M06.
**Base:** `main` `beab4ac0eab6b57455cde57ff6627b74b46a4cd7`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD.
**Lock:** `.engineering/context-locks/NEX-M06-CONTRACT-WO-001-EXECUTION.json` (26 fingerprints).

## Objetivo

Definir o contrato versionado `performance.v1` para observações de performance: workload, intervalos de frame, timings, recursos, classificação de gargalo com evidência/confiança e proveniência. Sem medição nova, sem benchmark e sem implementação de M06.

## Escopo

- `contracts/m06/performance.v1.schema.json`, `contracts/m06/ownership.v1.json`.
- `docs/contracts/m06.md`.
- `tests/contracts/test_m06_performance_contract.py`.
- Evidência, delta de checkpoint e este WO/lock.

## Fora de escopo

- Executar capturas, alterar `nex_bench`/engine/CI, implementar LOD/culling/batching/streaming.
- M06 parent admission; M08/M12.
- Claims de FPS, ganho ou regressão.

## DoD

- Contrato válido com coerência de gargalo↔métrica e disponibilidade explícita.
- Testes verdes e suítes completas verdes em worktree LF limpo.
- PR com checks verdes, squash protegido e checkpoint proposto.

## STOP

- Divergência de contrato, check vermelho ou necessidade de medição → parar e registrar.
