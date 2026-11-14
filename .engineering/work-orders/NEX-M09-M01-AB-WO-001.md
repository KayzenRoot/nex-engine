# NEX-M09-M01-AB-WO-001 | A/B/A nas cenas M01

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** NEX-ADR-0005 (autonomia contínua) sobre o harness M09 existente.
**Base:** `main` `51587de8cc8f713d3573a0bb6a52e7f19bb783a6`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD (medição isolada).
**Lock:** `.engineering/context-locks/NEX-M09-M01-AB-WO-001-EXECUTION.json` (22 fingerprints).

## Objetivo

Estender o harness A/B/A para instanciar as três cenas base M01 (`corridor_static`, `arena_combat`, `dense_city`), adicionar fillers determinísticos até 100 meshes totais em cada cena e medir 3 repetições por preset em cada cena (18 capturas reais na RTX 5050). O layout do workload passa a ser registrado no documento de perfil com validação estrita.

## Escopo

- `nex_bench/scenes/preset_ab/**`: suporte a cena M01, contagem/realocação de meshes, validador e README.
- `nex_bench/gpu_profile/session.gd`: layout de workload opcional e restrito; default inalterado.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-ab/**`: 18 capturas, 18 validações, manifesto, fatos, análise e SHA-256.
- `docs/benchmarks/m09/**`: relatório M01 A/B/A e builder.
- `tests/ci/test_m01_ab.py`, `tests/ci/_preset_ab_support.py`, ajustes em testes do harness.
- Evidência, delta e este WO/lock.

## Fora de escopo

- Alterar as cenas base, `project.godot`, hub, renderer, shaders, engine ou CI.
- Claims de FPS de jogo, qualidade visual, ganho universal ou generalização.
- M09 parent admission.

## DoD

- 18 capturas COMPLETE/validadas com contagem de meshes declarada e fillers documentados.
- Cada cena tem exatamente 100 meshes no documento de perfil; o layout é validado contra a cena.
- Relatório reproduzível, testes verdes, suítes completas verdes em worktree LF limpo.
- PR protegida com checks verdes e checkpoint pós-merge.

## STOP

- Cena não carregar, contagem de meshes divergir, captura inválida ou validador rejeitar → parar e registrar.
