# NEX M08 · Final 2.5D composition gate

**Status:** `M08_RENDER25D_REFERENCE_COMPLETE / OWNER_AUTHORIZED / ADMIN_SOLO_NOT_INDEPENDENT`
**Data:** 2026-11-16 · **Base:** `2c7dd515e307086cdd7180577b0c78ad7fb5cf1c`
**Parent:** #13.

## O que foi concluído

| Área | Entrega | Evidência |
|---|---|---|
| CompositionPlanner | Camadas, roles, alpha guard e overlay safety | `nex_modules/render2_5d/composition/`; 69 checks |
| Câmera híbrida | Ortográfica inclinada + perspectiva | `m08_baseline.png`; `m08_perspective.png` |
| Sprite3D billboards | 40 sprites em espaço 3D | `m08_sprites.png`; 0.400 ms |
| Depth sorting | render_priority vs nativo | `m08_sorted.png`; 0.000% de diff |
| Sombras 3D | DirectionalLight3D + shadow casting | `m08_shadows.png`; 0.498 ms |
| Overlay 2D | CanvasLayer com barras/marcadores | `m08_overlay.png`; 0.411 ms |
| Hybrid | Sprites + sombras + overlay | `m08_hybrid.png`; 0.508 ms |
| Quality profiles | low/high | 0.397/0.497 ms |
| QA | 9 runs, 9 imagens, validador e relatório | `m08-runtime.v1.json`; este gate |

## Resultado

- **CompositionPlanner:** 69 checks headless; nenhum rendering.
- **Baseline:** GPU p95 **0.390 ms**, CPU p95 **0.247 ms**, 1% low **225.69 FPS**.
- **Sprites:** **0.400 ms** (+2.56%); **6.463%** de pixels.
- **Sorted:** **0.401 ms** (+2.82%); **6.463%** de pixels; sorted vs sprites **0.000%** → **NO_GO** para sorter customizado.
- **Shadows:** **0.498 ms** (+27.69%); **15.477%** de pixels.
- **Overlay:** **0.411 ms** (+5.38%); **22.789%** de pixels.
- **Hybrid:** **0.508 ms** (+30.26%); **31.714%** de pixels.
- **Perspective:** **0.332 ms** (-14.87% vs ortho); **34.442%** de pixels.
- **Quality:** low **0.397 ms**, high **0.497 ms**.
- **Decisões:** CompositionPlanner/ortho/sprites/shadows/overlay/hybrid/perspective/quality `GO_WITH_LIMITATIONS`; sorting customizado **NO_GO**.

## Limitações

- Sessão única, RTX 5050, driver NVIDIA 617.14; lab 2.5D estático 1920×1080.
- Sem renderer 2.5D de produção, viewport stacking ou art-directed layer stack.
- Sorting é o sorting nativo de transparência do Godot, não um sorter customizado.
- Sem input-to-photon, VRAM, cross-device ou claim generalizado de FPS/qualidade.
- **Nenhum asset de terceiros. Nenhuma paridade com PoE2 é alegada.**
- Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; sem revisor independente.

## Fechamento

Com este gate, a issue **#13** pode ser fechada como `COMPLETED` após o merge protegido e os checks pós-merge. O próximo módulo base é **M09** (ferramentas editor, presets e asset import); M10–M12 continuam bounded.
