# Evidence Bundle · NEX-GOV-AUTONOMY-WO-001 (Autonomia contínua)

**Status:** `GOVERNANCE_RULE / OWNER_DIRECTIVE / ADMIN_SOLO_NOT_INDEPENDENT`
**Issue:** #108 · **Base:** `1ac35a91a38dd91f5fe3fad6855627823f68e573`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `.engineering/decisions/NEX-ADR-0005-AUTONOMOUS-BUILD.md`: decisão de construção contínua, ciclos longos, escolha autônoma de incrementos e condições de parada.
- `.engineering/DECISIONS-LEDGER.md`: NEX-D-015, coerente com NEX-ADR-0004 / NEX-D-014.
- `AGENTS.md`: seção resumida NEX-ADR-0005.
- WO e Context Lock correspondentes.

## Invariantes preservados

- Autonomia não admite automaticamente issues PLANNING_ONLY ou parents M01–M12.
- CI, segurança, testes, locks, ruleset e branch protection permanecem inalterados.
- Force-push, reset destrutivo, escrita concorrente e operações irreversíveis sem autorização continuam proibidos.
- Auditoria permanece `ADMIN_SOLO / NOT_INDEPENDENT`; nenhuma revisão independente é simulada.
- Parada obrigatória em bloqueio técnico, dependência não admitida, risco grave, CI vermelha/pendente, Context Lock STALE, base/HEAD divergente, defeito HIGH/CRITICAL ou conflito de escrita.

## Verificação

- Diff limitado a `AGENTS.md`, ADR-0005, ledger, WO, lock e este bundle.
- Nenhum arquivo de engine, contrato, CI, `project.godot` ou teste alterado.
- PR protegida e checks obrigatórios verificados antes do squash; checkpoint após merge.

## Rollback

Reverter os arquivos de governança deste incremento restaura a redação anterior; nenhum estado técnico é afetado.
