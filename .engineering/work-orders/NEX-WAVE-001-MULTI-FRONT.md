# NEX-WAVE-001-MULTI-FRONT | Onda paralela de seis frentes independentes

**Status:** `OWNER_ADMITTED_IN_SESSION / EXECUTABLE_ON_BOUND_BASE`
**Admissão:** Owner selecionou "Onda máxima — 6 frentes" em 2026-11-13, após análise de dependências do backlog.
**Base:** `main` `9282ee4027af79bf7e6afddb557445d0d57c57d3` (18 fingerprints em `NEX-WAVE-001-EXECUTION.json`).
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014.
**Lock:** `.engineering/context-locks/NEX-WAVE-001-EXECUTION.json`.

## Por que estas seis frentes

São as únicas combinações de escopo já delimitadas no backlog cujos caminhos de escrita são disjuntos e cujas dependências técnicas estão satisfeitas (M00, contratos v1, S01–S04 integrados). As demais 60 issues permanecem bloqueadas por parent/contrato não admitidos (M02–M12 além dos contratos, S07 após S05/S06, FLOW e #35 após módulos).

## Incrementos (PRs independentes)

| # | Incremento | Issue | Branch | Escrita permitida | GPU |
|---|---|---|---|---|---|
| 1 | NEX-M01-S05-WO-001 — Matriz cinematográfica | #25 | `feat/nex-m01-s05-cinematic-matrix` | `nex_bench/scenes/lighting_matrix/**`, `nex_bench/presets/lighting_matrix/**`, `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-13-s05/**`, `tests/ci/test_lighting_matrix.py` | sim (serial) |
| 2 | NEX-M01-S06-WO-001 — Radar R&D | #26 | `feat/nex-m01-s06-rd-radar` | `docs/research/nex-m01/**`, `tests/ci/test_research_notes.py` | não |
| 3 | NEX-QA-AUDIT-WO-001 — Bug Hunter | #20 | `qa/nex-qa-audit-wo-001` | `qa/bug-reports/NEX-QA-AUDIT-WO-001/**`, `tests/ci/test_qa_audit_regressions.py` | não |
| 4 | NEX-M12-S01-WO-001 — Brand master | #17 | `feat/nex-m12-s01-brand-master` | `assets/brand/**`, `docs/brand/**`, `tests/ci/test_brand_assets.py` | não |
| 5 | NEX-M02-CONTRACT-WO-001 — Contrato render core | #7 | `contracts/nex-m02-render-core` | `contracts/m02/**`, `docs/contracts/m02.md`, `tests/contracts/test_m02_render_contract.py` | não |
| 6 | NEX-M07-CONTRACT-WO-001 — Contrato interface 2D | #12 | `contracts/nex-m07-render2d-interface` | `contracts/m07/**`, `docs/contracts/m07.md`, `tests/contracts/test_m07_render2d_contract.py` | não |

## Regras de execução

- Um PR por incremento; branches e worktrees isolados; nenhum arquivo compartilhado entre frentes.
- GPU exclusiva: apenas S05 usa RTX 5050; nenhuma captura concorrente.
- Cada PR: Evidence Bundle próprio, testes da suíte aplicável, seis checks obrigatórios e squash protegido ADMIN_SOLO.
- Nenhum incremento admite módulo M02–M12 completo; contratos e brand são habilitadores, não implementação de módulo.
- `contracts/m01/**`, `.engineering/**` (exceto este WO/lock), `tooling/**` e `tests/m00/**` são read-only.

## STOP

- `STALE` se a main ou os fingerprints canônicos mudarem antes de um incremento começar → renovar lock.
- Falha de check obrigatório, defeito HIGH/CRITICAL ou conflito de path → parar aquela frente e reportar.
- Necessidade de alterar contrato existente (`contracts/m01/**`), ruleset ou quality gate → parar e escalar.
- S07 (#27) **não** pertence a esta onda: depende de S05 e S06 concluídas.
