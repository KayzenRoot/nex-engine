# Checkpoint Delta · NEX-M04-KIT-BUDGET-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `873f4a7d05d3b70912a5112089e3ebfbf068703c`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **Orçamento do kit M04 medido pelo planner integrado:** `FIT` para 4 materiais e 12 texturas únicas.
2. **Métricas:** 0 duplicatas; 1.048.572 bytes decodificados/deduplicados; atlas 12/256 tiles; pressão 0.047; nenhum finding.
3. **Builder:** `build_kit_budget.py --check` reproduz JSON/Markdown; enforcement no Fast Lane (28 arquivos / 31 checks).
4. **Sem mudança de contrato, planner, kit, cena, preset, renderer, shader, ruleset ou permissão de CI.**
5. **Sem rendering, decodificação, compressão, atlas packing ou claim de FPS/qualidade.**

## O que NÃO muda

- Todos os parents M01–M12 seguem bounded admitted; nenhum parent muda de status.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.
- Nenhum runtime, hub, engine, `project.godot` principal ou cena de produção é admitido.

## Evidência de apoio

- `.engineering/evidence/NEX-M04-KIT-BUDGET-WO-001-EVIDENCE.md`
- `nex_modules/materials/texturebudget/evidence/kit-budget-2026-11-15.json`
- `docs/benchmarks/m04/kit-budget.v1.json`
- `docs/benchmarks/m04/KIT-BUDGET.md`
- `tests/ci/test_kit_budget.py` (6 testes)
