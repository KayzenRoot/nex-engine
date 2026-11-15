# Evidence Bundle · NEX-M04-FINAL-REFERENCE-WO-001

**Status:** `M04_MATERIALS_REFERENCE_EVIDENCE / NATIVE_GALLERY / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`
**Parent:** M04 #9 · **Base:** `e09cce2f4332e00a0f51eacb346f5763fe228db9`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- **PBR Atlas:** 8 materiais originais, 24 texturas 256×256, 8 `.tres` e `atlas.v1.json`.
- **Galeria nativa:** `gallery.png`, `triplanar_on/off.png`, `decal_on/off.png` a 1920×1080.
- **ShaderForge/SurfaceBlend:** `triplanar_wet.gdshader` com albedo/ORM triplanar e wetness.
- **DecalSurface:** `decal_surface.gd` + `decal-smoke-2026-11-15.json` (12/12 checks).
- **TextureBudget:** `texture-scaling.v1.json` com 1K/2K/4K em memória.
- **Builders:** `build_pbr_atlas.py`, `build_texture_scaling.py`, `build_materials_runtime.py`.
- **Gate:** `M04-FINAL-GATE.md`; issues #44–#51 e #9 fechadas após integração.
- **Governança:** `NEX-ADR-0015`, `NEX-D-026`, WO/lock/evidência/delta.

## Resultado

- **Atlas:** 8 materiais / 24 texturas; galeria 1920×1080.
- **Triplanar:** 3.102% de pixels alterados; mean abs 0.7365; PSNR 33.618 dB.
- **Decal:** 4.286% de pixels alterados; 12/12 request checks.
- **Scaling:** 1K albedo **4.2 MB PNG / 5.6 MB decoded**; 2K **16.8/22.4 MB**; 4K albedo **67.1/89.5 MB**.
- Nenhum asset de terceiros; materiais e texturas originais.

## Verificação

- `build_pbr_atlas.py --check`: `M04_PBR_ATLAS_CHECK_PASS: 8 materials / 24 textures`.
- `build_texture_scaling.py --check`: `M04_TEXTURE_SCALING_CHECK_PASS: 3 sizes`.
- `build_materials_runtime.py --check`: `M04_MATERIALS_RUNTIME_CHECK_PASS: 5 runs`.
- Decal smoke: `M04_DECAL_SMOKE_PASS 12 checks`.
- Suíte CI completa e builders/validadores verdes antes da PR.

## O que não foi feito / não é alegado

- Nenhum asset, shader, cena ou paridade com PoE2.
- Nenhuma arte de produção, cabelo, folhagem alpha ou detail masks.
- Nenhum BC/BPTC, VRAM, atlas packing ou import/cook.
- Nenhum renderer/runtime M05–M12, jogo, gameplay ou rede.
- Nenhum claim generalizado de FPS/qualidade ou cross-device.
- Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; sem revisor independente.

## Rollback

Reverter o atlas, a galeria, os builders/relatórios, o DecalSurface, o teste, o workflow, ADR/ledger/WO/lock/evidência/delta, atualizações de AGENTS/SCOPE/CHECKPOINT e o fechamento das issues.
