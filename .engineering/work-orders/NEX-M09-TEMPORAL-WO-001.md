# NEX-M09-TEMPORAL-WO-001 | Estabilidade visual temporal M01

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** NEX-ADR-0005 (autonomia contínua) sobre o harness M09 existente.
**Base:** `main` `cefd2a045a410147b96577a547239f75be5215d5`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD (medição isolada).
**Lock:** `.engineering/context-locks/NEX-M09-TEMPORAL-WO-001-EXECUTION.json`.

## Objetivo

Capturar uma sequência de 5 frames por cena/preset nas três cenas M01 (3 × 2 × 5 = 30 PNGs) e medir a diferença frame-a-frame para verificar estabilidade temporal em frame estático. Atualizar o atlas M09 para incluir o bundle.

## Escopo

- `nex_bench/scenes/preset_ab/**`: modo `NEX_PRESET_AB_VISUAL_SEQUENCE`, 5 frames com intervalo fixo, warmup existente.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-temporal/**`: 30 PNGs, manifesto, fatos, análise e SHA-256.
- `docs/benchmarks/m09/**`: relatório `temporal-stability.v1.json`, builder, README e atualização do atlas.
- `tests/ci/test_temporal_stability.py` e ajuste de `test_measurement_atlas.py`.
- Evidência, delta e este WO/lock.

## Fora de escopo

- Alterar cenas base, `project.godot`, hub, renderer, shaders, engine ou CI.
- Animação, movimento de câmera, temporal effects reais ou outros hardwares.
- Claims de qualidade visual, FPS ou generalização.
- M09 parent admission.

## DoD

- 30 PNGs 1280×720, 5 por cena/preset, com hashes determinísticos por frame.
- Relatório com comparações frame-a-frame e veredito de estabilidade/varição.
- Atlas M09 atualizado para 10 bundles, 66 imagens e 384 arquivos.
- Suítes completas verdes em worktree LF limpo; PR protegida e checkpoint pós-merge.

## STOP

- Captura de viewport indisponível, frames com dimensões divergentes, falha de sequência ou builder não reproduzir → parar e registrar.
