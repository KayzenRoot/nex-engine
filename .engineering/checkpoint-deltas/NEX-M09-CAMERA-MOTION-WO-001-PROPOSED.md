# Checkpoint Delta · NEX-M09-CAMERA-MOTION-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `a6ce04bf74e7dee5712738a213704aab8068132b`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M09-CAMERA-MOTION integrado:** flag aditiva `NEX_PRESET_AB_CAMERA_MOTION`, órbita de 3° por frame, 30 PNGs.
2. **Resultado:** todos os pares consecutivos diferem; changed pixels 3.132–19.766%; mean abs médio 1.80–5.16 por célula.
3. **Atlas:** 14 bundles, 114 imagens, 468 arquivos, 14 source SHAs.
4. **Enforcement:** 26 comandos / 23 arquivos.
5. **Sem mudança de cena base, preset, contrato, renderer, shader ou ruleset.**
6. **Sem claim de FPS, qualidade, estabilidade ou generalização.**

## O que NÃO muda

- M01/M02/M03/M04/M05/M06/M09 seguem bounded admitted; M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.

## Evidência de apoio

- `.engineering/evidence/NEX-M09-CAMERA-MOTION-WO-001-EVIDENCE.md`
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-camera-motion/`
- `docs/benchmarks/m09/camera-motion.v1.json`
- `tests/ci/test_camera_motion.py` (6 testes)
