# NEX M04 · Final materials gate

**Status:** `M04_MATERIALS_REFERENCE_COMPLETE / OWNER_AUTHORIZED / ADMIN_SOLO_NOT_INDEPENDENT`
**Data:** 2026-11-15 · **Base:** `e09cce2f4332e00a0f51eacb346f5763fe228db9`
**Parent:** #9 · **Sub-issues:** #44 S01, #45 S02, #46 S03, #47 S04, #48 S05, #49 S06, #50 S07, #51 S08.

## O que foi concluído

| Sub-issue | Entrega | Evidência |
|---|---|---|
| #44 PBR Atlas | 8 materiais originais, 24 texturas 256×256 | `atlas.v1.json`; `PBR-ATLAS.md`; `...m04-gallery/gallery.png` |
| #45 ShaderForge | Shader triplanar/wet com uniforms | `triplanar_wet.gdshader`; `...m04-gallery/triplanar_on.png` |
| #46 SurfaceBlend | Triplanar + wetness | `triplanar_on/off` (3.102% pixels) |
| #47 Material Fidelity | 8 cards, skin SSS, água alpha | `...m04-gallery/gallery.png` |
| #48 DecalSurface | Decal3D visual + request bridge 12 checks | `decal_on/off`; `decal-smoke-2026-11-15.json` |
| #49 TextureBudget | 1K/2K/4K metadata e bytes | `texture-scaling.v1.json`; `TEXTURE-SCALING.md` |
| #50 R&D | Matriz GO/NO_GO | `materials-runtime.v1.json` S07 |
| #51 QA | Galeria, diffs e gate | `materials-runtime.v1.json`; este gate |

## Resultado

- **PBR Atlas:** 8 materiais / 24 texturas; galeria nativa 1920×1080.
- **ShaderForge/SurfaceBlend:** triplanar on/off **3.102%** de pixels, mean abs 0.7365, PSNR 33.618 dB.
- **DecalSurface:** Decal3D **4.286%** de pixels; request bridge **12/12 checks**.
- **Texture scaling:** 1K albedo **4.2 MB PNG / 5.6 MB decoded**; 2K **16.8 MB / 22.4 MB**; 4K **67.1 MB / 89.5 MB** (2K/4K upscales documentados).
- **Decisões:** PBR Atlas GO; ShaderForge/SurfaceBlend/Material Fidelity/TextureBudget `GO_WITH_LIMITATIONS`; DecalSurface GO.

## Limitações

- Sessão única, RTX 5050, driver NVIDIA 617.14; frame estático.
- 2K/4K são upscales nearest-neighbour, não detalhe nativo.
- Sem BC/BPTC, VRAM, atlas packing ou pipeline de import/cook.
- Sem cabelo, folhagem alpha, normal mapping ou detail masks.
- **Nenhum asset de terceiros. Nenhuma paridade com PoE2 é alegada.**
- Nenhum claim de FPS, qualidade cross-device ou ganho.
- Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; sem revisor independente.

## Fechamento

Com este gate, as issues **#44–#51 e #9** podem ser fechadas como `COMPLETED` após o merge protegido e os checks pós-merge. O próximo módulo base é **M05** (VFX GPU e biblioteca de magias), que deve consumir o atlas, o shader e o LightBridge M03.
