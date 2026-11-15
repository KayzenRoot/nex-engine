# NEX-M10-ARCHETYPE-FEEDBACK-WO-001 | Feedback de combate sobre o dataset M05

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** M10 `BOUNDED_ADMITTED_ANIMATION_PIPELINE` (`NEX-ADR-0010` / `NEX-D-020`); instrução contínua do Owner de 2026-11-15.
**Base:** `main` `91e6c15794662b3502244c2d03879b8dbb9980dd`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** STANDARD (planejamento determinístico, sem animação/câmera/shader/rendering).
**Lock:** `.engineering/context-locks/NEX-M10-ARCHETYPE-FEEDBACK-WO-001-EXECUTION.json`.

## Objetivo

Alimentar o `FeedbackPlanner` integrado com os spells do dataset M05 e produzir planos de feedback de combate por arquétipo (`skirmish`, `elite`, `boss`), com hit-stop, shake, flash, recoil e damage number determinísticos, sem criar animação, câmera, shader, cena ou renderer.

## Escopo

- `nex_modules/vfx/fxbudget/dataset.gd`: campo aditivo `spells` na evidência para consumo downstream; regeneração da evidência e do relatório M05.
- `nex_modules/animation/combat_feedback/archetype_feedback.gd`: SceneTree headless que mapeia cast/travel/impact/linger para anticipation/active/recovery, deriva dano dos emitters de impacto e registra cinco canais por spell.
- `nex_modules/animation/combat_feedback/evidence/archetype-feedback-2026-11-15.json`.
- `docs/benchmarks/m10/tools/build_archetype_feedback.py`, `archetype-feedback.v1.json` e `ARCHETYPE-FEEDBACK.md`.
- `tests/ci/test_archetype_feedback.py`; enforcement no workflow e contagem 30 arquivos / 33 checks.
- WO/lock/evidência/delta e checkpoint.

## Fora de escopo

- Criar animação, `AnimationPlayer`, câmera, shake real, flash, recoil, shader ou partículas.
- Alterar o planner, o contrato `feedback.v1`, cenas, presets, renderer ou shaders.
- Claims de game feel, FPS, frame-time, qualidade ou ganho.
- Novos parents ou mudança de status.

## DoD

- 10 planos de spell (2+3+5) todos `SAFE_CONFIG_HEURISTIC`, 0 conflitos.
- 5 canais por spell; pico de concorrência 5/5; hit-stop total 40/60/100 ms; shake máximo 0.313.
- Dano determinístico: 32/64/128/225/75; críticos em storm-lance e meteor-storm.
- Dataset M05 regenerado com `spells` aditivo e hash atualizado; builder M05 `--check` verde.
- Builder M10 `--check` reproduz JSON/Markdown; CI 30/33; suíte completa verde.
- PR protegida e checkpoint pós-merge verificado.

## STOP

- Base/HEAD divergente, planner/contrato alterado, plano com conflito high, builder divergente ou check vermelho → parar e registrar.
