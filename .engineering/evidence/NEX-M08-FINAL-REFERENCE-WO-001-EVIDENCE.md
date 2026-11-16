# Evidence Bundle · NEX-M08-FINAL-REFERENCE-WO-001

**Status:** `M08_RENDER25D_REFERENCE_EVIDENCE / NATIVE_2.5D_LAB / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`
**Parent:** M08 #13 · **Base:** `2c7dd515e307086cdd7180577b0c78ad7fb5cf1c`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- **CompositionPlanner:** 69 checks headless; camadas, roles, alpha guard, depth policy e overlay safety.
- **Câmera híbrida:** ortográfica inclinada e variante perspectiva.
- **Sprite3D billboards:** 40 sprites em espaço 3D.
- **Depth sorting:** `render_priority` comparado ao sorting nativo.
- **Sombras 3D:** `DirectionalLight3D` com shadow casting de sprites e caixas.
- **Overlay 2D:** `CanvasLayer` com barras e marcadores.
- **Hybrid:** sprites + sombras + overlay.
- **Quality profiles:** low/high.
- **Evidência:** 9 runs nativos validados, 9 capturas 1920×1080, manifest e SHA256SUMS.
- **Builder/Gate:** `build_m08_runtime.py`, `M08-RUNTIME.md`, `m08-runtime.v1.json`, `M08-FINAL-GATE.md`.
- **Governança:** `NEX-ADR-0019`, `NEX-D-030`, WO/lock/evidência/delta.

## Resultado

- **S01:** CompositionPlanner 69 checks.
- **S02:** baseline **0.390 ms**; sprites **0.400 ms** (+2.56%); sorted **0.401 ms** (+2.82%); sprites/sorted **6.463%** de pixels.
- **S03:** shadows **0.498 ms** (+27.69%); **15.477%** de pixels.
- **S04:** overlay **0.411 ms** (+5.38%); **22.789%** de pixels.
- **S05:** hybrid **0.508 ms** (+30.26%); **31.714%** de pixels.
- **S06:** perspective **0.332 ms** (-14.87% vs ortho); **34.442%** de pixels.
- **S07:** quality low/high **0.397 / 0.497 ms**.
- **S08:** 9 runs, 9 imagens, 69 checks, 0 assets de terceiros.
- Sorting customizado: **0.000%** de diferença vs sprites → **NO_GO**.

## Verificação

- `m08_lab.gd`: `NEX_M08_LAB` em 9 modos; `NEX_M08_CAPTURE` em 9 runs.
- `validate_m08_lab.py`: 9/9 runs `PASS`.
- `build_m08_runtime.py --check`: `M08_RENDER25D_RUNTIME_CHECK_PASS: 9 runs`.
- CompositionPlanner: `NEX_M08_COMPOSITION_SMOKE_PASS: 69 checks`.
- Suíte CI completa e builders/validadores verdes antes da PR.

## O que não foi feito / não é alegado

- Nenhum renderer 2.5D de produção, viewport stacking, art-directed layer stack ou shader customizado.
- Nenhum M09–M12, gameplay, rede, cloud ou asset de terceiros.
- Nenhum input-to-photon, VRAM, cross-device ou claim generalizado de FPS/qualidade.
- Nenhum asset, shader, cena ou paridade com PoE2.
- Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; sem revisor independente.

## Rollback

Reverter o laboratório M08, o layout no `session.gd`, as evidências, o builder/relatórios, o teste, o workflow, ADR/ledger/WO/lock/evidência/delta, atualizações de AGENTS/SCOPE/CHECKPOINT e o fechamento da issue.
