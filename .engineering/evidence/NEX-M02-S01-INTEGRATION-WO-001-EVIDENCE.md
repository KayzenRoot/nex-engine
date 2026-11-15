# Evidence Bundle · NEX-M02-S01-INTEGRATION-WO-001

**Status:** `SCENE_AND_PERFORMANCE_EVIDENCE / SINGLE_SESSION / ADMIN_SOLO_NOT_INDEPENDENT`
**Parents:** M02 #7 · S01 #28 · **Base:** `ad41089a3a37407ce8773ea86ac364873971551d`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_bench/scenes/m02_camera/camera_rig.gd`: cópia vendorizada do `IsometricCameraRig`, com teste de igualdade byte-a-byte com a fonte.
- `preset_ab.gd`: modo aditivo `NEX_PRESET_AB_CAMERA_MODE=rig`; baseline inalterado.
- Evidence visual: 18 PNGs (3 cenas × 2 modos × 3 repetições), A/A byte-idêntico.
- Evidence performance: 18 capturas (3 cenas × 2 modos × 3 repetições), 2 s warmup e 30 s observação.
- Relatório `camera-integration.v1.json` + `CAMERA-INTEGRATION.md`.
- QA ledger S01: `scene_comparison=PASS`, `performance=MEASURED`, com `scene_evidence`/`performance_evidence`.
- `tests/ci/test_m02_camera_integration.py` (6 testes); 29 comandos de builder/validator.

## Resultado

- A/B visual: mean abs **0.002/0.0003/0.0**; changed pixels **0.013%/0.003%/0.0%**; PSNR 59.66/71.95/106.53 dB.
- Performance: GPU p95 delta **0.0%/+0.94%/+1.25%**; CPU p95 **0.0%/+13.3%/+12.94%**; pacing ~4.21–4.24 ms.
- O rig reproduz o enquadramento baseline com diferença desprezível; o custo GPU é nulo a 1.25%.
- S02–S05 permanecem `INCONCLUSIVE_NOT_RUN` (protótipos analysis-only); S06 é research-only.

## Verificação

- A/A determinístico por modo; hashes do manifesto conferidos; 18/18 capturas PASS.
- `build_camera_integration.py --check` e `qa_ledger.py --check` PASS; 29/29 comandos verdes.
- Suítes: CI **559**, contratos **203**, telemetria **31** — OK.
- Nenhuma cena base, preset, contrato, renderer, shader ou `project.godot` alterado.

## O que não foi feito / não é alegado

- Nenhuma integração de S02–S06, animação, gameplay ou cena de produção.
- Nenhum claim de FPS, qualidade, ganho ou generalização cross-device/sessão.
- Nenhuma aprovação independente; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Rollback

Reverter o modo de câmera/harness, o rig vendorizado, os evidence bundles, builder/relatórios, QA ledger, testes, workflow, WO/lock/evidência/delta e a entrada de checkpoint correspondente.
