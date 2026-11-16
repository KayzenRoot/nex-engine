# NEX-ADR-0018 · Admissão full reference do M07 e laboratório 2D

**Status:** `OWNER_DIRECTIVE / APPROVED_ON_GOVERNANCE_MERGE`
**Data:** 2026-11-16
**Owner:** KayzenRoot
**Auditoria:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Base de admissão:** `aa6256a82f6cd34e347b05ac43375ac4042d2ede`

## Contexto

O Owner autorizou construir a NEX Engine de forma contínua e autônoma, finalizando os módulos base com rendering/runtime real. O M07 já tinha contrato `render2d.v1` e o protótipo `CanvasPlanner` com 46 checks headless, mas não tinha cenas 2D nativas, luzes, sombras, normal maps, partículas, parallax, perfis de qualidade nem evidência de performance.

## Decisão

Admitir, de forma **full reference e bounded ao M07**:

- **CanvasPlanner:** manter o protótipo determinístico de camadas/materiais/luzes/partículas e batching, com 46 checks headless.
- **2D lighting:** `CanvasModulate` + 4 `PointLight2D` em cena 2D nativa.
- **2D shadows:** `LightOccluder2D` + sombras de luz, comparadas a lighting sem sombras.
- **Normal maps:** `CanvasTexture` com `normal_texture` em sprites iluminados.
- **GPUParticles2D:** 6 emissores, 384 partículas, material procedural.
- **Parallax:** `ParallaxBackground` com 3 camadas e movimento.
- **Quality profiles:** low/medium/high variando luzes, sombras, partículas e parallax.
- **Evidência:** 9 runs nativos, 9 capturas 1920×1080, validação canônica e relatório/gate.
- **R&D/QA:** matriz GO/NO_GO e fechamento de #12 após squash protegido.

## Escopo de arquivos admitido

- `nex_bench/scenes/m07_2d/**` (lab, captura e validador).
- `nex_bench/gpu_profile/session.gd` (uma linha: layout 2D permitido).
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-16-m07/**`.
- `docs/benchmarks/m07/**` e `tests/ci/test_m07_final.py`.
- Enforcement de builders e workflow CI.

## Exclusões explícitas

- Nenhum renderer 2D de produção, atlas packing, y-sort, rasterização de transparência ou shader customizado.
- Nenhum M08/2.5D, animação M10, asset pipeline M11 ou gameplay.
- Nenhum input-to-photon, VRAM, cross-device ou claim generalizado de FPS/qualidade.
- Nenhum asset, shader, cena ou paridade com PoE2.
- Nenhum relaxamento de CI, segurança, testes, locks, ruleset ou auditoria solo.

## Condições e gates

1. WO/Context Lock, evidência e todos os checks no HEAD exato.
2. `build_m07_runtime.py --check` reproduz o relatório; `validate_m07_lab.py` valida 9/9 runs.
3. CanvasPlanner smoke `46 checks` PASS; 9 capturas e 9 runs.
4. Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; auditoria permanece `ADMIN_SOLO / NOT_INDEPENDENT`.
5. M08–M12 continuam bounded e exigem WO própria.
6. O fechamento de issue só ocorre após squash protegido e checks pós-merge verdes.

## Consequências

- M07 passa a ser o sétimo módulo base concluído como **render2d de referência**, não como jogo.
- M08 pode consumir a composição 2D/2.5D; M10 pode reutilizar partículas e feedback.
- O laboratório 2D é evidência nativa; não é um renderer de produção.
