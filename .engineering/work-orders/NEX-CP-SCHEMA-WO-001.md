# NEX-CP-SCHEMA-WO-001 | Validador de schema e coerência do checkpoint

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** continuação autônoma autorizada (NEX-ADR-0005); enabler de auditoria, sem nova medição.
**Base:** `main` `35b6b25ce317f8a6a8b53784dfaa70613de7c6b2`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** LOW.
**Lock:** `.engineering/context-locks/NEX-CP-SCHEMA-WO-001-EXECUTION.json`.

## Objetivo

Adicionar um validador determinístico do `CHECKPOINT.json` que falha em SHA inválido, `pr` sem merge SHA, aprovação independente falsa, bloco de admissão ausente, merge SHAs duplicados e contagem de proveniência incoerente. O validador roda no job requerido e complementa o índice de proveniência.

## Escopo

- `docs/benchmarks/tools/validate_checkpoint.py` com `--check`.
- `tests/ci/test_checkpoint_schema.py` (7 testes).
- `tests/ci/test_builder_check_enforcement.py` e workflow: enforcement do validador cross-module.
- WO/lock/evidência/delta.
- Promoção de checkpoint em PR documental separado.

## Fora de escopo

- Alterar o checkpoint, blocos de admissão, medições, harness, contratos, modelo ou ruleset.
- Nova medição, captura ou renderização.
- Commitar qualquer claim de revisão independente.
- Novos parents ou issues `PLANNING_ONLY`.

## DoD

- Checkpoint commitado passa com 61 blocos de proveniência.
- Casos negativos (SHA inválido, merge ausente, aprovação falsa, bloco ausente, contagem errada) falham.
- `--check` no job requerido; suítes CI/contratos/telemetria verdes.
- PR protegida com checks verdes e checkpoint pós-merge verificado.

## STOP

- Base/HEAD divergente, checkpoint com defeito real, divergência do índice ou check vermelho → parar e registrar.
