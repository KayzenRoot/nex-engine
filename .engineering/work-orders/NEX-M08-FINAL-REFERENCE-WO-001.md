# NEX-M08-FINAL-REFERENCE-WO-001 | Fechamento da composição 2.5D de referência M08

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** `NEX-ADR-0019` / `NEX-D-030`; instrução do Owner de 2026-11-16 para finalizar o M08 com medições reais, sem paridade com PoE2.
**Base:** `main` `2c7dd515e307086cdd7180577b0c78ad7fb5cf1c`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** STANDARD (9 runs nativos 2.5D e capturas).
**Lock:** `.engineering/context-locks/NEX-M08-FINAL-REFERENCE-WO-001-EXECUTION.json`.

## Objetivo

Finalizar o M08 como composição 2.5D de referência: laboratório híbrido nativo com câmera ortográfica/perspectiva, sprites 3D, sorting, sombras, overlay 2D, hybrid e perfis de qualidade; 9 runs, 9 capturas, validador, relatório/gate e fechamento de #13.

## Escopo

- `nex_bench/scenes/m08_2_5d/m08_lab.gd`, `m08_lab.tscn`, `validate_m08_lab.py`.
- `nex_bench/gpu_profile/session.gd`: layout `M08 hybrid 2.5D lab` permitido.
- Evidence `windows-rtx5050-2026-11-16-m08/`: 9 runs, 9 imagens, logs, manifest e SHA256SUMS.
- `docs/benchmarks/m08/tools/build_m08_runtime.py`, `M08-RUNTIME.md`, `m08-runtime.v1.json`, `M08-FINAL-GATE.md`.
- `docs/benchmarks/tools/runtime_report.py` e refatoração de M06/M07 builders para helpers compartilhados.
- `tests/ci/test_m08_final.py`; enforcement no workflow.
- ADR/ledger/WO/lock/evidência/delta, AGENTS/SCOPE/CHECKPOINT e fechamento de #13.

## Fora de escopo

- Renderer 2.5D de produção, viewport stacking, art-directed layer stack, shader customizado.
- M09–M12, gameplay, rede, cloud, assets de terceiros.
- Input-to-photon, VRAM, cross-device, PoE2 ou claims generalizados de FPS/qualidade.

## DoD

- 9 runs validados e 9 imagens 1920×1080; CompositionPlanner 69 checks.
- Baseline GPU p95 **0.390 ms**; sprites **0.400 ms**; sorted **0.401 ms**; shadows **0.498 ms**; overlay **0.411 ms**; hybrid **0.508 ms**; perspective **0.332 ms**.
- Quality low/high **0.397 / 0.497 ms**.
- Diffs: sprites **6.463%**; shadows **15.477%**; overlay **22.789%**; hybrid **31.714%**; perspective **34.442%**.
- Sorting customizado: **0.000%** de diferença vs sprites → **NO_GO**.
- Builders `--check`; suíte CI verde; PR protegida e checkpoint pós-merge.
- Issue #13 fechada com comentário de evidência.

## STOP

- Base/HEAD divergente, smoke falhando, run não validado, imagem ausente, check vermelho, claim de paridade com PoE2 ou generalização → parar e registrar.
