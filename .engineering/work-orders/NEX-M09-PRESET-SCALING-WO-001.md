# NEX-M09-PRESET-SCALING-WO-001 | Matriz de escala de presets 25/100/200

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** NEX-ADR-0005 (autonomia contínua) sobre o harness M09 existente.
**Base:** `main` `9babd8cb4f88c6cb5ac473c5ff77c82852293eb8`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD (medição isolada).
**Lock:** `.engineering/context-locks/NEX-M09-PRESET-SCALING-WO-001-EXECUTION.json` (22 fingerprints).

## Objetivo

Parametrizar o harness A/B/A por contagem de proxies (25/100/200) e medir 3 repetições por preset em cada contagem (18 capturas reais na RTX 5050), produzindo relatório de escala reproduzível.

## Escopo

- `nex_bench/scenes/preset_ab/preset_ab.gd`, `validate_preset_ab.py`, `README.md`: proxy count 25/50/100/200.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-preset-scaling/**`: 18 capturas, 18 validações, manifesto, fatos, análise e SHA-256.
- `docs/benchmarks/m09/**`: `scaling.v1.json`, `SCALING-REPORT.md`, builder e README.
- `tests/ci/test_preset_scaling.py`.
- Evidência, delta e este WO/lock.

## Fora de escopo

- Alterar `project.godot`, hub, renderer, shaders, engine ou CI.
- Claims de FPS de jogo, ganho universal ou generalização entre cenas/hardware.
- M09 parent admission.

## DoD

- 18 capturas COMPLETE/validadas; hashes; relatório reproduzível; testes verdes.
- Suítes completas verdes em worktree LF limpo; PR protegida e checkpoint.

## STOP

- Captura inválida, viewport mudando, validador rejeitando ou generalização indevida → parar e registrar.
