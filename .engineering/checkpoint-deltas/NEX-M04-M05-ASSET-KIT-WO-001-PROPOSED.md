# Checkpoint Delta · NEX-M04-M05-ASSET-KIT-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `99437b22e94a6494eaef801872bb8fd0c79c0f1a`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M04 kit PBR procedural:** 12 PNGs 128×128, quatro `StandardMaterial3D` `.tres` e observação `material.v1`, validados headless em 28 checks.
2. **M05 dataset de orçamento:** `skirmish` FIT (484 partículas), `elite` TIGHT (1047/1100), `boss` OVER_BUDGET (2753/2000) com plano de redução de 3 passos.
3. **Builders:** `build_material_kit.py --check` e `build_fx_budget_dataset.py --check` reproduzem bytes; enforcement no Fast Lane (27 arquivos / 30 comandos).
4. **Admissão:** `NEX-ADR-0011` / `NEX-D-021` estendem o escopo bounded de M04/M05 sem mudar o status dos parents.
5. **Sem mudança de contrato, planner, cena base, renderer, shader, ruleset ou permissão de CI.**
6. **Sem rendering, runtime, partículas reais ou claim de FPS/qualidade.**

## O que NÃO muda

- Todos os parents M01–M12 seguem bounded admitted; nenhum parent muda de status.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.
- Nenhum runtime, hub, engine, `project.godot` principal ou cena de produção é admitido.

## Evidência de apoio

- `.engineering/evidence/NEX-M04-M05-ASSET-KIT-WO-001-EVIDENCE.md`
- `nex_modules/materials/kit/kit.v1.json`
- `nex_modules/vfx/fxbudget/evidence/fx-budget-dataset-2026-11-15.json`
- `docs/benchmarks/m04/MATERIAL-KIT.md`
- `docs/benchmarks/m05/FX-BUDGET-DATASET.md`
- `tests/ci/test_material_kit.py`, `tests/ci/test_fx_budget_dataset.py`, `tests/ci/test_m04_m05_asset_kit_admission.py`
