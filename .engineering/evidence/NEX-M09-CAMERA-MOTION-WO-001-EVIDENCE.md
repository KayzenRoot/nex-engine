# Evidence Bundle · NEX-M09-CAMERA-MOTION-WO-001

**Status:** `CAMERA_MOTION_EVIDENCE / SINGLE_SESSION / ADMIN_SOLO_NOT_INDEPENDENT`
**Parent:** M09 #14 · **Base:** `a6ce04bf74e7dee5712738a213704aab8068132b`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- Harness `preset_ab.gd` com flag aditiva `NEX_PRESET_AB_CAMERA_MOTION` e órbita determinística de 3° por frame capturado.
- Evidence bundle `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-camera-motion/`: 30 PNGs (3 cenas × 2 presets × 5 frames), manifesto, fatos, análise e SHA-256 (33 arquivos).
- Builder `build_camera_motion.py`; relatório `camera-motion.v1.json` + `CAMERA-MOTION-REPORT.md`.
- Atlas M09 atualizado para **14 bundles, 114 imagens, 468 arquivos e 14 source SHAs**.
- `tests/ci/test_camera_motion.py` (6 testes); **26 comandos `--check` / 23 arquivos**.
- WO/lock/evidência/delta correspondentes.

## Resultado

- 30/30 frames 1280×720, hashes do manifesto conferidos; todos os pares consecutivos diferem.
- Changed pixels: **3.132–19.766%** entre pares; mean abs médio por célula: corridor 5.09/5.16, arena 2.18/2.23, city 1.80/1.84.
- A diferença cresce com o índice do frame conforme a órbita acumula rotação.
- Flag desligada mantém o comportamento estático existente; a estabilidade temporal estática continua em bundle separado.

## Verificação

- `--check` do novo builder PASS; 26/26 builders PASS em worktree LF limpo.
- Suítes: CI **540**, contratos **203**, telemetria **31** — OK.
- Nenhuma cena base, preset, contrato, renderer, shader ou `project.godot` alterado.

## O que não foi feito / não é alegado

- Nenhuma animação contínua, VFX, física ou gameplay.
- Nenhum claim de FPS, qualidade, estabilidade ou generalização cross-device/sessão.
- Nenhum parent novo admitido; M07–M08 e M10–M12 seguem `NOT_ADMITTED`.
- Nenhuma aprovação independente; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Rollback

Reverter a flag/harness, o evidence bundle, builder/relatórios, atualização do atlas, testes, workflow, WO/lock/evidência/delta e a entrada de checkpoint correspondente.
