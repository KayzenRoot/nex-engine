# Checkpoint Delta · NEX-M03-SHADOWSTAB-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `346c6dd6bd85c12e3aad1250d8cae95b195bd605` · **Code SHA:** `6db0a5ee32b695cef9892267301be7157b95c2cc`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M03-SHADOWSTAB concluído como protótipo isolado:** analisador determinístico de riscos de sombra sobre `lighting.plan.v1`/`lighting.v1`, com splits de cascata, pressão de atlas, bias/softness, orçamento e coerência de casters.
2. **Parent M03 (#8) permanece NOT_ADMITTED.** Nenhuma sombra, filtro, shader, cena, engine, CI ou `project.godot`.
3. **Contrato `lighting.v1` consumido:** vocabulário e limites espelhados; nenhum contrato alterado.
4. **Qualidade visual/performance:** `INCONCLUSIVE_NOT_RUN`; achados são heurísticos, não medições.
5. **Próximos incrementos:** GI/fog/LightBridge e validação visual exigem WO própria.

## O que NÃO muda

- M01/M02/M07 e M03-LIGHTRIG permanecem como estão; nenhum checkpoint promovido por este delta.
- Nenhum claim visual/performance.

## Evidência de apoio

- `.engineering/evidence/NEX-M03-SHADOWSTAB-WO-001-EVIDENCE.md`
- `nex_modules/lighting/shadows/evidence/headless-smoke-2026-11-13.log` (`NEX_M03_SHADOWSTAB_SMOKE_PASS: 51 checks`)
- `tests/ci/test_shadow_stability_analyzer.py` (9 testes)
