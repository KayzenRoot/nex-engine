# NEX-M09-VISUAL-1920-WO-001 | Verdade visual M01 em 1920×1080

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** NEX-ADR-0005 (autonomia contínua) sobre o harness M09 existente.
**Base:** `main` `06eb6d92da50bdb8105bbc8f7b6bed98faebb329`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014. **Risco:** STANDARD (medição isolada).
**Lock:** `.engineering/context-locks/NEX-M09-VISUAL-1920-WO-001-EXECUTION.json`.

## Objetivo

Capturar as três cenas M01 sob `ab-low`/`ab-high` em 1920×1080 (3 repetições por célula, 18 PNGs), verificar determinismo A/A e medir a diferença A/B de pixels, comparando com o relatório visual de 1280×720. Atualizar o atlas M09 para incluir o novo bundle.

## Escopo

- `nex_bench/scenes/preset_ab/**`: uso do modo visual existente; sem mudança de engine.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-visual-1920/**`: 18 PNGs, manifesto, fatos, análise e SHA-256.
- `docs/benchmarks/m09/**`: relatório `m01-visual-1920.v1.json`, builder, README e atualização do atlas.
- `tests/ci/test_m01_visual_1920.py` e ajuste de `test_measurement_atlas.py`.
- Evidência, delta e este WO/lock.

## Fora de escopo

- Alterar cenas base, `project.godot`, hub, renderer, shaders, engine ou CI.
- 2560×1440, animação/temporal ou outros hardwares.
- Claims de qualidade visual, FPS ou generalização.
- M09 parent admission.

## DoD

- 18 PNGs 1920×1080 com A/A byte-idêntico e A/B acima do limiar documentado.
- Relatório reproduzível e comparação com 1280×720.
- Atlas M09 atualizado para 9 bundles, 36 imagens e 351 arquivos.
- Suítes completas verdes em worktree LF limpo; PR protegida e checkpoint pós-merge.

## STOP

- Captura de viewport indisponível, dimensões divergentes, A/A não determinístico ou validador rejeitar → parar e registrar.
