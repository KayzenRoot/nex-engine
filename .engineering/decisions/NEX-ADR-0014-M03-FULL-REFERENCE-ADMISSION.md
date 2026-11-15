# NEX-ADR-0014 · Admissão full reference do M03 e iluminação cinematográfica

**Status:** `OWNER_DIRECTIVE / APPROVED_ON_GOVERNANCE_MERGE`
**Data:** 2026-11-15
**Owner:** KayzenRoot
**Auditoria:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Base de admissão:** `6be39d49d8769ff46a98990c6818c8132e9e5a1d`

## Contexto

O Owner autorizou finalizar o M03 com qualidade cinematográfica de dark fantasy, após M01/M02. A admissão bounded anterior (`NEX-ADR-0007`) cobria contrato, light rig, sombras, light budget e validação contra M09 apenas como protótipos/análise. Ela não autorizava a aceitação plena da iluminação renderizada.

## Decisão

Admitir, de forma **full reference e bounded ao M03**, sobre as cenas M01:

- **CineLight:** três looks originais de dark fantasy (`dungeon_torch`, `moonlit_exterior`, `boss_arena`) com key/fill/rim, tonemap ACES, glow e exposição.
- **ShadowStability:** low vs ultra, atlas 1024/4096, quatro tochas com sombra e bias documentado.
- **GI Atlas:** SDFGI on/off com custo medido; LightmapGI/VoxelGI bake permanecem `NOT_EXERCISABLE` no runtime.
- **FogWeave:** volumetric fog vs depth fog vs off, com fallback de depth para Performance.
- **LightBridge:** API versionada de requests com validação, prioridade, budget group, preempção, expiração e fallback, testada com dois consumidores mock.
- **LightBudget:** MVP de slots de sombra por energia (2 vs 4 tochas) e recomendação `RESEARCH_MORE` para distância/visibilidade.
- **R&D/QA:** matriz GO/NO_GO e gate final; fechamento de #36–#43 e #8 após squash protegido.

## Escopo de arquivos admitido

- `nex_bench/scenes/preset_ab/preset_ab.gd` (flags aditivas de look/GI/fog/torch/budget).
- `nex_bench/scenes/m03_lighting/**` (light rig vendorizado, LightBridge e smoke).
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m03-*`.
- `docs/benchmarks/m03/**` e `tests/ci/test_m03_final.py`.

## Exclusões explícitas

- Nenhum asset, shader ou cena de PoE2; **nenhuma paridade com PoE2 é alegada**.
- Nenhum asset de produção, personagem, VFX real ou telegraph de combate.
- Nenhum bake LightmapGI/VoxelGI, GI dinâmica completa ou oclusão dinâmica.
- Nenhum renderer/runtime de M04–M12, jogo, gameplay, rede ou cloud.
- Nenhum claim generalizado de FPS/qualidade, cross-device ou input-to-photon.
- Nenhum relaxamento de CI, segurança, testes, locks, ruleset ou auditoria solo.

## Condições e gates

1. WO/Context Lock, evidência e todos os checks no HEAD exato.
2. Builder `build_lighting_runtime.py --check` reproduz o relatório.
3. Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; auditoria permanece `ADMIN_SOLO / NOT_INDEPENDENT`.
4. M04–M12 continuam bounded e exigem WO própria.
5. O fechamento de issues só ocorre após squash protegido e checks pós-merge verdes.

## Consequências

- M03 passa a ser o terceiro módulo base concluído como **iluminação de referência**, não como jogo.
- O baseline M01/M02 e o budget 1080p são consumidos; M04 herda o kit procedural e os looks M03.
- SDFGI fica restrito a perfis de qualidade; volumetric fog tem fallback depth; LightBudget permanece pesquisa.
