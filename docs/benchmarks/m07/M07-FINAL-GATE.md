# NEX M07 · Final render2d gate

**Status:** `M07_RENDER2D_REFERENCE_COMPLETE / OWNER_AUTHORIZED / ADMIN_SOLO_NOT_INDEPENDENT`
**Data:** 2026-11-16 · **Base:** `aa6256a82f6cd34e347b05ac43375ac4042d2ede`
**Parent:** #12.

## O que foi concluído

| Área | Entrega | Evidência |
|---|---|---|
| CanvasPlanner | Camadas, materiais, luzes, partículas e batching | `nex_modules/render2d/canvas/`; 46 checks |
| 2D lighting | CanvasModulate + 4 PointLight2D | `m07_lighting.png`; 0.075 ms |
| 2D shadows | LightOccluder2D + sombras | `m07_shadows.png`; 0.100 ms |
| Normal maps | CanvasTexture com normal_texture | `m07_normal.png`; 0.082 ms |
| Particles | 6 emissores, 384 partículas | `m07_particles.png`; 0.071 ms |
| Parallax | 3 camadas com movimento | `m07_parallax.png`; 0.070 ms |
| Quality profiles | low/medium/high | 0.065/0.081/0.153 ms |
| QA | 9 runs, 9 imagens, validador e relatório | `m07-runtime.v1.json`; este gate |

## Resultado

- **CanvasPlanner:** 46 checks headless; nenhum rendering.
- **Baseline:** GPU p95 **0.060 ms**, CPU p95 **0.128 ms**, 1% low **229.82 FPS**.
- **Lighting:** **0.075 ms** (+25.00%); **16.218%** de pixels; PSNR 21.55 dB.
- **Shadows:** **0.100 ms** (+66.67% vs baseline, +33.3% vs lighting); shadows vs lighting **9.028%** de pixels.
- **Normal maps:** **0.082 ms** (+36.67% vs baseline, +9.3% vs lighting); normal vs lighting **14.542%** de pixels.
- **Particles:** **0.071 ms** (+18.33%); **0.979%** de pixels.
- **Parallax:** **0.070 ms** (+16.67%); **23.006%** de pixels.
- **Quality:** low **0.065 ms**, medium **0.081 ms**, high **0.153 ms**.
- **Decisões:** CanvasPlanner/Parallax **GO**; lighting/shadows/normal/particles/quality `GO_WITH_LIMITATIONS`.

## Limitações

- Sessão única, RTX 5050, driver NVIDIA 617.14; lab 2D estático 1920×1080.
- Sem renderer 2D de produção, atlas packing, y-sort ou rasterização de transparência.
- Sem input-to-photon, VRAM, cross-device ou claim generalizado de FPS/qualidade.
- Luzes, sombras e normal maps são recursos nativos do Godot, não um renderer customizado.
- **Nenhum asset de terceiros. Nenhuma paridade com PoE2 é alegada.**
- Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; sem revisor independente.

## Fechamento

Com este gate, a issue **#12** pode ser fechada como `COMPLETED` após o merge protegido e os checks pós-merge. O próximo módulo base é **M08** (composição 2.5D), que deve consumir o laboratório 2D; M09–M12 continuam bounded.
