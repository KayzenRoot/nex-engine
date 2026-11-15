# Evidence Bundle · NEX-M02-S02-S03-S04-ANALYSIS-WO-001

**Status:** `SCENE_ANALYSIS_EVIDENCE / HEADLESS / SINGLE_SESSION / ADMIN_SOLO_NOT_INDEPENDENT`
**Parents:** M02 #7 · S02 #29 · S03 #30 · S04 #31 · **Base:** `57f204ef7237243da13af66560f80d4a726c7d56`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_bench/scenes/m02_analysis/`: cópias vendorizadas de `sightline_controller.gd`, `depth_composition_solver.gd` e `temporal_guard_analyzer.gd`, com teste de igualdade byte-a-byte, e `run_analysis.gd`.
- `run_analysis.gd`: SceneTree headless que carrega cada cena M01, calcula AABBs de mundo, executa sightline com 8 occluders, depth com 16 primitivas e temporal sobre 5 frames estáticos.
- Evidence bundle `windows-rtx5050-2026-11-15-m02-analysis/`: `corridor_static.json`, `arena_combat.json`, `dense_city.json`, `runs.v1.json`, `SESSION-FACTS.txt`, `ANALYSIS.md`, `SHA256SUMS.txt`.
- Builder `build_analysis_integration.py`; relatório `analysis-integration.v1.json` + `ANALYSIS-INTEGRATION.md`.
- QA ledger S02–S04: `scene_analysis=PASS` com `scene_analysis_evidence`; `scene_comparison`/`performance` permanecem `INCONCLUSIVE_NOT_RUN`.
- `tests/ci/test_m02_analysis_integration.py` (6 testes); ajustes no QA ledger e no enforcement de builders.
- CI: 30 comandos de builder/validator (28 module + 2 cross-module).

## Resultado

- Cenas: 17 (corridor), 34 (arena) e 23 (city) meshes; 8 occluders e 16 primitivas em cada cena.
- Sightline: 1 reveal ativo e 1 danger alert por cena; nenhum ator crítico não visto; `max_reveal=8`.
- Depth: 0 z-fight risks em corridor e 4 em arena/city; 0 alpha-over-critical e 0 overlay-gameplay conflicts.
- Temporal: `BASELINE_ACCEPTABLE` em 5 frames e 16 regiões por cena; ghosting, flicker e shimmer 0.0; `render_scale=1.0`.
- Harness SHA-256 `b1a1f726c6289059…`; manifesto com `source_sha=57f204ef…` e três runs.

## Verificação

- `build_analysis_integration.py --check` reproduz JSON/Markdown byte-a-byte.
- `qa_ledger.py --check` PASS com os novos digests.
- Suíte CI completa: **573 testes OK**; builder/validator: **30/30 PASS**.
- Nenhuma cena base, preset, contrato, renderer, shader ou `project.godot` alterado.

## O que não foi feito / não é alegado

- Nenhum rendering, GPU, TAA, compositor ou captura de frame novo.
- Nenhum claim de FPS, qualidade visual, ganho ou generalização cross-device/sessão.
- Nenhuma integração de S05/S06, animação, gameplay ou cena de produção.
- Nenhuma aprovação independente; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Rollback

Reverter os scripts vendorizados e o harness, o evidence bundle, builder/relatórios, QA ledger, testes, workflow, WO/lock/evidência/delta e a entrada de checkpoint correspondente.
