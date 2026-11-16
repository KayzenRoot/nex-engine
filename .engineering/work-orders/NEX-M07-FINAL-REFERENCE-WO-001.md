# NEX-M07-FINAL-REFERENCE-WO-001 | Fechamento do render2d de referência M07

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** `NEX-ADR-0018` / `NEX-D-029`; instrução do Owner de 2026-11-16 para finalizar o M07 com medições reais, sem paridade com PoE2.
**Base:** `main` `aa6256a82f6cd34e347b05ac43375ac4042d2ede`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** STANDARD (9 runs nativos 2D e capturas).
**Lock:** `.engineering/context-locks/NEX-M07-FINAL-REFERENCE-WO-001-EXECUTION.json`.

## Objetivo

Finalizar o M07 como render2d de referência: laboratório 2D nativo com luzes, sombras, normal maps, partículas, parallax e perfis de qualidade; 9 runs, 9 capturas, validador, relatório/gate e fechamento de #12.

## Escopo

- `nex_bench/scenes/m07_2d/m07_lab.gd`, `m07_lab.tscn`, `validate_m07_lab.py`.
- `nex_bench/gpu_profile/session.gd`: layout `M07 layered 2D lab` permitido.
- `nex_bench/gpu_profile/lab_validation.py` e refatoração de `nex_bench/scenes/preset_ab/validate_preset_ab.py` para compartilhar validação e eliminar duplicação Sonar.
- Evidence `windows-rtx5050-2026-11-16-m07/`: 9 runs, 9 imagens, logs, manifest e SHA256SUMS.
- `docs/benchmarks/m07/tools/build_m07_runtime.py`, `M07-RUNTIME.md`, `m07-runtime.v1.json`, `M07-FINAL-GATE.md`.
- `tests/ci/test_m07_final.py`; enforcement no workflow.
- ADR/ledger/WO/lock/evidência/delta, AGENTS/SCOPE/CHECKPOINT e fechamento de #12.

## Fora de escopo

- Renderer 2D de produção, atlas packing, y-sort, transparência rasterizada, shader customizado.
- M08/2.5D, M10 animação, M11 assets, gameplay, rede, cloud.
- Input-to-photon, VRAM, cross-device, PoE2 ou claims generalizados de FPS/qualidade.

## DoD

- 9 runs validados e 9 imagens 1920×1080; CanvasPlanner 46 checks.
- Baseline GPU p95 **0.060 ms**; lighting **0.075 ms**; shadows **0.100 ms**; normal **0.082 ms**; particles **0.071 ms**; parallax **0.070 ms**.
- Quality low/medium/high: **0.065 / 0.081 / 0.153 ms**.
- Diffs: lighting **16.218%**; shadows vs lighting **9.028%**; normal vs lighting **14.542%**; particles **0.979%**; parallax **23.006%**.
- Builders `--check`; suíte CI verde; PR protegida e checkpoint pós-merge.
- Issue #12 fechada com comentário de evidência.

## STOP

- Base/HEAD divergente, smoke falhando, run não validado, imagem ausente, check vermelho, claim de paridade com PoE2 ou generalização → parar e registrar.
