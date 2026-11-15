# NEX-M09-CAMERA-MOTION-WO-001 | Sequência determinística de câmera em movimento

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** continuação autônoma autorizada (NEX-ADR-0005); M09 é `BOUNDED_ADMITTED_EVIDENCE_PIPELINE` desde NEX-ADR-0006.
**Base:** `main` `a6ce04bf74e7dee5712738a213704aab8068132b`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** STANDARD (extensão aditiva do harness).
**Lock:** `.engineering/context-locks/NEX-M09-CAMERA-MOTION-WO-001-EXECUTION.json`.

## Objetivo

Adicionar ao harness uma sequência determinística de **câmera em órbita** (3° por frame capturado), cobrindo a lacuna "câmera em movimento não coberta" sem alterar o comportamento existente quando a flag está desligada. Produzir 30 PNGs (3 cenas × 2 presets × 5 frames), um relatório frame-a-frame e evidência verificável.

## Escopo

- `nex_bench/scenes/preset_ab/preset_ab.gd`: flag aditiva `NEX_PRESET_AB_CAMERA_MOTION` e órbita determinística.
- Evidence bundle `windows-rtx5050-2026-11-14-camera-motion/`: 30 PNGs + manifesto/fatos/análise/SHA-256.
- Builder `docs/benchmarks/m09/tools/build_camera_motion.py`; relatório `camera-motion.v1.json` + Markdown.
- Atlas M09 atualizado para 14 bundles (114 imagens, 468 arquivos).
- `tests/ci/test_camera_motion.py` e ajustes no atlas/enforcement.
- Enforcement de `--check` no job requerido (26 comandos / 23 arquivos).
- Evidência, delta e este WO/lock.
- Promoção de checkpoint em PR documental separado.

## Fora de escopo

- Alterar cenas base, presets, contrato, renderer, shaders ou `project.godot`.
- Animação contínua, VFX, física ou gameplay.
- Nova medição de performance; claims de FPS/qualidade/estabilidade.
- Resoluções acima de 2560×1440 ou outros displays.
- Novos parents, runtime, hub, engine, cenas de produção.

## DoD

- Flag desligada mantém o comportamento existente byte-idêntico; flag ligada produz 5 frames distintos por célula.
- 30 PNGs 1280×720, hashes do manifesto conferidos; todos os pares consecutivos diferem.
- Relatório com 6 células e comparações frame-a-frame; veredito `CAMERA_MOTION_OBSERVED`.
- Suítes CI/contratos/telemetria verdes em worktree LF limpo; 26/26 builders `--check`.
- PR protegida com checks verdes e checkpoint pós-merge verificado.

## STOP

- Base/HEAD divergente, frames idênticos, hash divergente, regressão do comportamento estático, necessidade de alterar cena/renderer ou check vermelho → parar e registrar.
