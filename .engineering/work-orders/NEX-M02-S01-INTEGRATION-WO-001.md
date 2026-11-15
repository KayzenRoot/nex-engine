# NEX-M02-S01-INTEGRATION-WO-001 | Integração de câmera M02 nas cenas M01

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** instrução do Owner de 2026-11-15 ("autorizo que vc faça pode continuar") para destravar a integração M02; M02 é `BOUNDED_ADMITTED_REFERENCE_PIPELINE`.
**Base:** `main` `ad41089a3a37407ce8773ea86ac364873971551d`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** STANDARD (integração de câmera e medição de cena).
**Lock:** `.engineering/context-locks/NEX-M02-S01-INTEGRATION-WO-001-EXECUTION.json`.

## Objetivo

Integrar o protótipo `IsometricCameraRig` (M02-S01) ao harness M01 como modo aditivo `baseline|rig`, provando que ele reproduz o enquadramento congelado e medindo o custo GPU/CPU/pacing em A/B/A nas três cenas M01. Resolver o `INCONCLUSIVE_NOT_RUN` de cena/performance do componente S01 no QA ledger.

## Escopo

- `nex_bench/scenes/m02_camera/camera_rig.gd`: cópia vendorizada do protótipo, com teste de igualdade byte-a-byte com a fonte.
- `nex_bench/scenes/preset_ab/preset_ab.gd`: flag aditiva `NEX_PRESET_AB_CAMERA_MODE=rig`; baseline inalterado.
- Evidence bundles `windows-rtx5050-2026-11-15-m02-camera-visual/` (18 PNGs) e `...-perf/` (18 capturas + validações).
- Builder `docs/benchmarks/m02/tools/build_camera_integration.py`; relatório `camera-integration.v1.json` + Markdown.
- `qa_ledger.py` e `qa-ledger.v1.json`: S01 `scene_comparison=PASS`, `performance=MEASURED`, com `scene_evidence`/`performance_evidence`.
- `tests/ci/test_m02_camera_integration.py`, ajustes no teste do QA ledger e no enforcement.
- README M02; evidência, delta e este WO/lock.
- Promoção de checkpoint em PR documental separado.

## Fora de escopo

- Integrar S02–S05 (protótipos analysis-only) ou S06 (research).
- Alterar cenas base, presets, contratos, renderer, shaders ou `project.godot`.
- Claims de FPS, qualidade, ganho ou generalização.
- Novos parents ou runtime de produção.

## DoD

- Baseline e rig reproduzem o mesmo enquadramento; A/A byte-idêntico por modo.
- A/B visual: mean abs 0.002/0.0003/0.0; changed pixels 0.013%/0.003%/0.0%.
- Performance: GPU p95 delta 0.0%/+0.94%/+1.25%; CPU 0.0%/+13.3%/+12.94%.
- QA ledger S01 PASS/MEASURED com evidência; S02–S05 permanecem `INCONCLUSIVE_NOT_RUN`.
- Suítes CI/contratos/telemetria verdes; 29 comandos de builder/validator.
- PR protegida com checks verdes e checkpoint pós-merge verificado.

## STOP

- Base/HEAD divergente, divergência do rig vendorizado, regressão do baseline, A/A não determinístico, divergência do QA ledger ou check vermelho → parar e registrar.
