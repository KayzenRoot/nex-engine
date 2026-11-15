# Evidence Bundle · NEX-M04-M05-ASSET-KIT-WO-001

**Status:** `NON_RENDERING_ASSET_EVIDENCE / SINGLE_SESSION / ADMIN_SOLO_NOT_INDEPENDENT`
**Parents:** M04 #9 · M05 #10 · **Base:** `99437b22e94a6494eaef801872bb8fd0c79c0f1a`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_modules/materials/kit/`: 12 PNGs 128×128 (albedo, normal, ORM), quatro `StandardMaterial3D` `.tres`, `kit.v1.json` (`material.v1`), `validate_kit.gd`, `README.md`, `.gitignore` e log headless.
- `docs/benchmarks/m04/tools/build_material_kit.py` e `docs/benchmarks/m04/MATERIAL-KIT.md`.
- `nex_modules/vfx/fxbudget/dataset.gd` e `evidence/fx-budget-dataset-2026-11-15.json`.
- `docs/benchmarks/m05/tools/build_fx_budget_dataset.py`, `fx-budget-dataset.v1.json` e `FX-BUDGET-DATASET.md`.
- `tests/ci/test_material_kit.py` (7), `tests/ci/test_fx_budget_dataset.py` (7) e `tests/ci/test_m04_m05_asset_kit_admission.py` (7).
- CI: 27 arquivos / 30 comandos de builder/validator.

## Resultado

- Kit M04: `KIT_LOAD_OK 28 checks`; os quatro materiais carregam com albedo/normal/ORM 128×128.
- Dataset M05: `skirmish` FIT (484 partículas, 7 emitters); `elite` TIGHT (1047/1100 = 95.2%); `boss` OVER_BUDGET (2753/2000 = 137.7%) com plano de redução de 3 passos e projeção 1834.
- Ambos os builders reproduzem bytes e SHA-256; nenhum shader, renderer, cena, partícula, emissor, luz ou decal foi criado.
- Nenhuma captura de frame, GPU execution ou claim de FPS/qualidade.

## Verificação

- `build_material_kit.py --check`: `M04_MATERIAL_KIT_CHECK_PASS: 4 materials / 12 textures`.
- `build_fx_budget_dataset.py --check`: `M05_FX_BUDGET_DATASET_CHECK_PASS: 3 runs`.
- PNGs decodificados por `png_image.read_png`; `.tres` carregados por `ResourceLoader` headless.
- Suíte CI completa e 30/30 comandos de builder/validator verdes antes da PR.

## O que não foi feito / não é alegado

- Nenhum shader customizado, `ShaderMaterial`, compilação de shader ou renderer.
- Nenhuma integração/aplicação em cena, rendering, runtime, hub, engine ou gameplay.
- Nenhuma partícula/emissor/luz/decal real; nenhuma decodificação/compressão/atlas packing de produção.
- Nenhum claim de FPS, frame-time, VRAM, overdraw, qualidade, game feel ou generalização.
- Nenhuma aprovação independente; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Rollback

Reverter o kit, o dataset e suas evidências, builders/relatórios, testes, workflow, ADR/ledger/WO/lock/evidência/delta, atualizações de AGENTS/SCOPE/CHECKPOINT e a entrada de checkpoint correspondente.
