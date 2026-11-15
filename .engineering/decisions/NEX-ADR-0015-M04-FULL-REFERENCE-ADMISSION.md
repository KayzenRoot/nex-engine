# NEX-ADR-0015 · Admissão full reference do M04 e atlas de materiais

**Status:** `OWNER_DIRECTIVE / APPROVED_ON_GOVERNANCE_MERGE`
**Data:** 2026-11-15
**Owner:** KayzenRoot
**Auditoria:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Base de admissão:** `e09cce2f4332e00a0f51eacb346f5763fe228db9`

## Contexto

O Owner autorizou finalizar os módulos base com rendering/runtime real. M04 já tinha contrato `material.v1`, TextureBudget e um kit procedural de 4 materiais; faltava a biblioteca PBR de referência, o shader triplanar/wet, o teste de Decal3D e a escala de texturas. A admissão bounded anterior (`NEX-ADR-0009`/`NEX-ADR-0011`) cobria o kit não-rendering, não a galeria renderizada.

## Decisão

Admitir, de forma **full reference e bounded ao M04**:

- **PBR Reference Atlas:** 8 materiais originais (`stone_wet`, `brushed_metal`, `oak_wood`, `cloth_crimson`, `skin_pale`, `terrain_earth`, `foliage_deep`, `water_clear`), 24 texturas 256×256 e observação `material.v1`.
- **Galeria nativa:** 8 esferas, piso, key/fill/rim, skin com subsurface e água com alpha, capturada a 1920×1080 na RTX 5050.
- **ShaderForge/SurfaceBlend:** `triplanar_wet.gdshader` com albedo/ORM triplanar e wetness, comparado ao `StandardMaterial3D`.
- **DecalSurface:** Decal3D visual e API `DecalSurfaceRequest` com 12 checks e dois consumidores mock.
- **TextureBudget:** escala 1K/2K/4K em memória, bytes PNG/decodificados e hashes; 4K limitado a albedo.
- **R&D/QA:** matriz GO/NO_GO e gate; fechamento de #44–#51 e #9 após squash protegido.

## Escopo de arquivos admitido

- `nex_modules/materials/atlas/**` (texturas, materiais, shader, galeria, DecalSurface).
- `docs/benchmarks/m04/**` e `tests/ci/test_m04_final.py`.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m04-gallery/**`.

## Exclusões explícitas

- Nenhum asset, shader ou cena de PoE2; **nenhuma paridade com PoE2 é alegada**.
- Nenhuma arte de produção, personagem, cabelo, folhagem alpha ou detail mask.
- Nenhum BC/BPTC, compressão de textura, atlas packing, VRAM ou pipeline de import/cook.
- Nenhum renderer/runtime de M05–M12, jogo, gameplay, rede ou cloud.
- Nenhum claim generalizado de FPS/qualidade, cross-device ou input-to-photon.
- Nenhum relaxamento de CI, segurança, testes, locks, ruleset ou auditoria solo.

## Condições e gates

1. WO/Context Lock, evidência e todos os checks no HEAD exato.
2. Builders `build_pbr_atlas.py --check`, `build_texture_scaling.py --check` e `build_materials_runtime.py --check` reproduzem os artefatos.
3. Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; auditoria permanece `ADMIN_SOLO / NOT_INDEPENDENT`.
4. M05–M12 continuam bounded e exigem WO própria.
5. O fechamento de issues só ocorre após squash protegido e checks pós-merge verdes.

## Consequências

- M04 passa a ser o quarto módulo base concluído como **materiais de referência**, não como jogo.
- M05 herda o atlas, o shader e o LightBridge M03; M11 pode auditar as licenças do atlas (originais).
- 2K/4K permanecem provas de escala, não detalhe nativo; compressão/VRAM ficam para M11.
