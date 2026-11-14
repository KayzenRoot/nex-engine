# NEX-M09-M01-VISUAL-WO-001 | Visual truth das cenas M01

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** NEX-ADR-0005 (autonomia contínua) sobre o harness M09 existente.
**Base:** `main` `647670eecf051849970e659e5ef5b98da4413367`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD (medição isolada).
**Lock:** `.engineering/context-locks/NEX-M09-M01-VISUAL-WO-001-EXECUTION.json`.

## Objetivo

Capturar imagens determinísticas das três cenas base M01 sob `ab-low` e `ab-high`, comparar pixels A/A e A/B e publicar um relatório de diferença visual. Isto complementa o A/B/A de performance com evidência de que os presets alteram a imagem renderizada, sem claim de qualidade.

## Escopo

- `nex_bench/scenes/preset_ab/**`: modo `NEX_PRESET_AB_VISUAL`, captura de viewport em frame fixo, PNG e metadados.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-visual/**`: 18 PNGs, manifesto, fatos, análise e SHA-256.
- `docs/benchmarks/m09/**`: decoder PNG determinístico, builder, relatório `m01-visual.v1.json` / `M01-VISUAL-REPORT.md`.
- `tests/ci/test_m01_visual.py`: estrutura, determinismo A/A, diferença A/B e reprodutibilidade.
- Evidência, delta e este WO/lock.

## Fora de escopo

- Alterar cenas base, `project.godot`, hub, renderer, shaders, engine ou CI.
- Claims de qualidade visual, superioridade de preset, FPS ou generalização.
- M09 parent admission.

## DoD

- 18 PNGs 1280×720 com SHA-256, manifesto e comparador de pixels reproduzível.
- A/A dentro da tolerância documentada; A/B acima do limiar documentado.
- Relatório reproduzível, testes verdes, suítes completas verdes em worktree LF limpo.
- PR protegida com checks verdes e checkpoint pós-merge.

## STOP

- Captura de viewport indisponível, dimensões divergentes, A/A não determinístico acima da tolerância ou validador rejeitar → parar e registrar.
