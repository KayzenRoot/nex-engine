# NEX-PROVENANCE-INDEX-WO-001 | Índice de proveniência do checkpoint

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** continuação autônoma autorizada (NEX-ADR-0005); enabler de auditoria cross-module, sem nova medição.
**Base:** `main` `ee4e853d1506178d13e4f0c6632c39b1cd9895a1`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014 / NEX-ADR-0005. **Risco:** LOW (documentação/auditoria).
**Lock:** `.engineering/context-locks/NEX-PROVENANCE-INDEX-WO-001-EXECUTION.json`.

## Objetivo

Gerar um índice determinístico de proveniência a partir do `CHECKPOINT.json`: todos os blocos com PR protegida e merge SHA, issues, veredito/status e rótulo de auditoria. O índice é uma **ferramenta de navegação**, não substitui o checkpoint, que permanece a autoridade.

## Escopo

- `docs/benchmarks/tools/build_provenance_index.py` com `--check`.
- `docs/benchmarks/provenance-index.v1.json` e `PROVENANCE-INDEX.md` (57 entradas, PRs 112–241).
- `tests/ci/test_provenance_index.py` (6 testes).
- `tests/ci/test_builder_check_enforcement.py` e workflow: enforcement do builder cross-module.
- Evidência, delta e este WO/lock.
- Promoção de checkpoint em PR documental separado.

## Fora de escopo

- Alterar o checkpoint, qualquer bloco de admissão ou estado de parent.
- Nova medição, captura, renderização ou mudança de harness/cena/contrato/modelo.
- Commitar qualquer claim de revisão independente.
- Runtime, renderer, shaders, hub, `project.godot`.
- Novos parents ou issues `PLANNING_ONLY`.

## DoD

- 57 entradas, PRs 112–241, 57 merge SHAs únicos e 40-hex.
- Todos os rótulos de auditoria são `ADMIN_SOLO_NOT_INDEPENDENT` (ou vazios), nunca `INDEPENDENT_APPROVED`.
- Builder reproduz os artefatos; `--check` no job requerido.
- Suítes CI/contratos/telemetria verdes; 25 builders no workflow.
- PR protegida com checks verdes e checkpoint pós-merge verificado.

## STOP

- Base/HEAD divergente, checkpoint com merge SHA inválido, divergência do índice ou check vermelho → parar e registrar.
