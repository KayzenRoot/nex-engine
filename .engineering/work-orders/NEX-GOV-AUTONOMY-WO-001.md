# NEX-GOV-AUTONOMY-WO-001 | Diretiva de construção autônoma contínua

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** Diretiva expressa do Owner em 2026-11-14; registrada como NEX-ADR-0005 / NEX-D-015.
**Base:** `main` `1ac35a91a38dd91f5fe3fad6855627823f68e573`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD.
**Lock:** `.engineering/context-locks/NEX-GOV-AUTONOMY-WO-001-EXECUTION.json` (15 fingerprints).

## Objetivo

Registrar a autorização permanente do Owner para construção autônoma contínua: o executor escolhe e executa o próximo incremento de maior valor, em ciclos longos, sem pedir confirmação, parando somente diante de bloqueio técnico real, dependência não admitida, risco grave, operação irreversível sem autorização específica, CI vermelha/pendente, Context Lock STALE ou defeito HIGH/CRITICAL.

## Escopo

- `AGENTS.md`: seção NEX-ADR-0005.
- `.engineering/decisions/NEX-ADR-0005-AUTONOMOUS-BUILD.md`.
- `.engineering/DECISIONS-LEDGER.md`: NEX-D-015.
- Evidência e este WO/lock.

## Fora de escopo

- Admitir automaticamente parents PLANNING_ONLY ou relaxar CI, testes, locks, segurança ou revisão de risco.
- Alterar código de engine, contratos, CI ou `project.godot` neste incremento.

## DoD

- Regra canônica registrada, coerente com NEX-ADR-0004 e sem remover gates.
- PR protegida com checks verdes; checkpoint após merge.

## STOP

- Conflito com NEX-ADR-0004, check vermelho ou tentativa de usar a autonomia para bypass → parar.
