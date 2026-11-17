# NEX-ADR-0021 · Admissão full reference do M10 e animação de combate

**Status:** `OWNER_DIRECTIVE / APPROVED_ON_GOVERNANCE_MERGE`
**Data:** 2026-11-17
**Owner:** KayzenRoot
**Auditoria:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Base de admissão:** `de81ee67b1c469636678df5a437cfc6fd77f06b8`

## Contexto

O Owner autorizou construir a NEX Engine de forma contínua e autônoma, finalizando os módulos base. O M10 já tinha contrato `feedback.v1`, o `FeedbackPlanner` com 66 checks headless e o relatório de arquétipos, mas não tinha animação nativa, blending, hit reaction, hit-stop visual, câmera suave nem sincronização com VFX M05.

## Decisão

Admitir, de forma **full reference e bounded ao M10**:

- **FeedbackPlanner:** manter o planejador determinístico de fases, hits, canais e budgets com 66 checks.
- **AnimationTree blending:** rig proxy de dois ossos com `AnimationPlayer` e `AnimationTree`/`AnimationNodeBlend2`; blend 0.5 e attack.
- **Hit reaction:** animação de recuo no rig, sem autoridade de dano.
- **Visual hit-stop:** pausa visual de 80 ms no `AnimationPlayer`, sem alterar física/gameplay.
- **Smooth camera:** follow suave em `_process` com captura nativa.
- **M05 VFX sync:** impacto M05 disparado via contrato SpellFX no ataque.
- **Quality profiles:** low/high variando proxies animados.
- **Evidência:** 9 runs nativos, 9 capturas 1920×1080, validação canônica e relatório/gate.
- **R&D/QA:** matriz GO/GO_WITH_LIMITATIONS e fechamento de #15 após squash protegido.

## Escopo de arquivos admitido

- `nex_bench/scenes/m10_animation/**` (lab, captura e validador).
- `nex_bench/gpu_profile/session.gd` (layout M10 permitido).
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-17-m10/**`.
- `docs/benchmarks/m10/**` e `tests/ci/test_m10_final.py`.
- Enforcement de builders e workflow CI.

## Exclusões explícitas

- Nenhum dano, hitbox, física, netcode ou lógica de gameplay.
- Nenhum personagem de produção, skin, rig completo ou asset de terceiros.
- Nenhum M11/M12, renderer core, shader customizado ou cena de produção.
- Nenhum input-to-photon, VRAM, cross-device ou claim generalizado de FPS/qualidade.
- Nenhum asset, shader, cena ou paridade com PoE2.
- Nenhum relaxamento de CI, segurança, testes, locks, ruleset ou auditoria solo.

## Condições e gates

1. WO/Context Lock, evidência e todos os checks no HEAD exato.
2. `build_m10_runtime.py --check` reproduz o relatório; `validate_m10_lab.py` valida 9/9 runs.
3. FeedbackPlanner smoke `66 checks` PASS; 9 capturas e 9 runs.
4. Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; auditoria permanece `ADMIN_SOLO / NOT_INDEPENDENT`.
5. M11–M12 continuam bounded e exigem WO própria.
6. O fechamento de issue só ocorre após squash protegido e checks pós-merge verdes.

## Consequências

- M10 passa a ser o décimo módulo base concluído como **animação e feedback de referência**, não como jogo.
- M11/M12 podem consumir as capturas e a recipe de feedback; o hit-stop permanece visual.
- O rig proxy não é um personagem de produção; nenhuma paridade com PoE2 é alegada.
