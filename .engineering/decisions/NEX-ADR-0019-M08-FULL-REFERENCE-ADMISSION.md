# NEX-ADR-0019 · Admissão full reference do M08 e laboratório 2.5D

**Status:** `OWNER_DIRECTIVE / APPROVED_ON_GOVERNANCE_MERGE`
**Data:** 2026-11-16
**Owner:** KayzenRoot
**Auditoria:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Base de admissão:** `2c7dd515e307086cdd7180577b0c78ad7fb5cf1c`

## Contexto

O Owner autorizou construir a NEX Engine de forma contínua e autônoma, finalizando os módulos base com rendering/runtime real. O M08 já tinha contrato `composition.v1`, o `CompositionPlanner` com 69 checks headless e um relatório derivado de M02, mas não tinha cena híbrida nativa, câmera ortográfica/perspectiva, sprites 3D, sorting, sombras, overlay 2D nem evidência de performance.

## Decisão

Admitir, de forma **full reference e bounded ao M08**:

- **CompositionPlanner:** manter o protótipo determinístico de camadas, roles, alpha guard, depth policy e overlay safety com 69 checks.
- **Câmera híbrida:** câmera ortográfica inclinada e variante perspectiva.
- **Sprite3D billboards:** 40 sprites em espaço 3D com alpha transparente.
- **Depth sorting:** `render_priority` comparado ao sorting nativo; sem ganho visual → NO_GO.
- **Sombras 3D:** `DirectionalLight3D` com shadow casting de sprites e caixas.
- **Overlay 2D:** `CanvasLayer` com barras e marcadores sobre a cena 3D.
- **Hybrid:** composição completa de sprites, sombras e overlay.
- **Quality profiles:** low/high variando sprites, sombras e overlay.
- **Evidência:** 9 runs nativos, 9 capturas 1920×1080, validação canônica e relatório/gate.
- **R&D/QA:** matriz GO/NO_GO e fechamento de #13 após squash protegido.

## Escopo de arquivos admitido

- `nex_bench/scenes/m08_2_5d/**` (lab, captura e validador).
- `nex_bench/gpu_profile/session.gd` (layout 2.5D permitido).
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-16-m08/**`.
- `docs/benchmarks/m08/**`, `docs/benchmarks/tools/runtime_report.py` e `tests/ci/test_m08_final.py`.
- Enforcement de builders e workflow CI.

## Exclusões explícitas

- Nenhum renderer 2.5D de produção, viewport stacking, art-directed layer stack ou shader customizado.
- Nenhum M09–M12, gameplay, rede, cloud ou asset de terceiros.
- Nenhum input-to-photon, VRAM, cross-device ou claim generalizado de FPS/qualidade.
- Nenhum asset, shader, cena ou paridade com PoE2.
- Nenhum relaxamento de CI, segurança, testes, locks, ruleset ou auditoria solo.

## Condições e gates

1. WO/Context Lock, evidência e todos os checks no HEAD exato.
2. `build_m08_runtime.py --check` reproduz o relatório; `validate_m08_lab.py` valida 9/9 runs.
3. CompositionPlanner smoke `69 checks` PASS; 9 capturas e 9 runs.
4. Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; auditoria permanece `ADMIN_SOLO / NOT_INDEPENDENT`.
5. M09–M12 continuam bounded e exigem WO própria.
6. O fechamento de issue só ocorre após squash protegido e checks pós-merge verdes.

## Consequências

- M08 passa a ser o oitavo módulo base concluído como **composição 2.5D de referência**, não como jogo.
- M09/M10 podem consumir a composição híbrida; M11 pode auditar as limitações.
- O sorting customizado é rejeitado; o sorting nativo de transparência do Godot é suficiente no lab.
