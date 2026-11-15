# NEX-M04-FINAL-REFERENCE-WO-001 | Fechamento dos materiais de referência M04

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** `NEX-ADR-0015` / `NEX-D-026`; instrução do Owner de 2026-11-15 para finalizar o M04 com qualidade cinematográfica, sem paridade com PoE2.
**Base:** `main` `e09cce2f4332e00a0f51eacb346f5763fe228db9`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** STANDARD (galeria nativa e assets procedurais).
**Lock:** `.engineering/context-locks/NEX-M04-FINAL-REFERENCE-WO-001-EXECUTION.json`.

## Objetivo

Finalizar o M04 como materiais de referência: atlas PBR de 8 materiais originais, galeria nativa, shader triplanar/wet, Decal3D com API de requests e escala 1K/2K/4K; produzir R&D/QA e fechar #44–#51 e #9 após integração protegida.

## Escopo

- `nex_modules/materials/atlas/**`: 24 texturas 256×256, 8 `.tres`, `atlas.v1.json`, `triplanar_wet.gdshader`, `gallery.gd`, `decal_surface.gd`, `decal_smoke.gd`, `project.godot`, `main.tscn`.
- Evidence `windows-rtx5050-2026-11-15-m04-gallery/`: gallery, triplanar on/off, decal on/off, decal smoke.
- Builders `build_pbr_atlas.py`, `build_texture_scaling.py`, `build_materials_runtime.py`.
- `docs/benchmarks/m04/PBR-ATLAS.md`, `TEXTURE-SCALING.md`, `MATERIALS-RUNTIME.md`, `M04-FINAL-GATE.md`.
- `tests/ci/test_m04_final.py`; enforcement no workflow.
- ADR/ledger/WO/lock/evidência/delta, AGENTS/SCOPE/CHECKPOINT e fechamento de issues.

## Fora de escopo

- Assets, shaders, cenas ou paridade com PoE2.
- Arte de produção, cabelo, folhagem alpha, detail masks.
- BC/BPTC, VRAM, atlas packing, import/cook.
- Renderer/runtime M05–M12, jogo, gameplay, rede, cloud.
- Claims generalizados de FPS/qualidade ou cross-device.

## DoD

- Atlas com 8 materiais / 24 texturas 256×256; galeria nativa 1920×1080.
- Triplanar on/off: 3.102% de pixels, mean abs 0.7365, PSNR 33.618 dB.
- Decal3D: 4.286% de pixels; API com 12/12 checks.
- Texture scaling: 1K 4.2 MB PNG / 5.6 MB decoded; 2K 16.8/22.4 MB; 4K albedo 67.1/89.5 MB.
- Builders `--check`; suíte CI verde; PR protegida e checkpoint pós-merge.
- Issues #44–#51 e #9 fechadas com comentário de evidência.

## STOP

- Base/HEAD divergente, galeria não determinística, shader falhando, smoke falhando, check vermelho, claim de paridade com PoE2 ou generalização → parar e registrar.
