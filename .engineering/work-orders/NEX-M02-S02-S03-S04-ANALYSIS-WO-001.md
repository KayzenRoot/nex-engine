# NEX-M02-S02-S03-S04-ANALYSIS-WO-001 | Análises de cena M02 sobre dados M01

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** instrução do Owner de 2026-11-15 ("vamos continuar faça as 3 por favor") para integrar S02/S03/S04 como análises sobre dados reais das cenas M01; M02 é `BOUNDED_ADMITTED_REFERENCE_PIPELINE`.
**Base:** `main` `57f204ef7237243da13af66560f80d4a726c7d56`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** STANDARD (análise headless determinística, sem rendering).
**Lock:** `.engineering/context-locks/NEX-M02-S02-S03-S04-ANALYSIS-WO-001-EXECUTION.json`.

## Objetivo

Integrar os protótipos `SightlineController` (S02), `DepthCompositionSolver` (S03) e `TemporalGuardAnalyzer` (S04) como análises headless sobre geometria real das três cenas M01 e sobre os frames estáticos já integrados, produzindo traces/planos determinísticos com evidência. Atualizar o QA ledger com `scene_analysis=PASS` para S02–S04, mantendo `scene_comparison` e `performance` em `INCONCLUSIVE_NOT_RUN` porque não há rendering A/B/A.

## Escopo

- `nex_bench/scenes/m02_analysis/`: cópias vendorizadas de `sightline_controller.gd`, `depth_composition_solver.gd` e `temporal_guard_analyzer.gd`, com teste de igualdade byte-a-byte, e `run_analysis.gd` (SceneTree headless).
- Evidence bundle `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m02-analysis/`: três JSONs de cena, `runs.v1.json`, `SESSION-FACTS.txt`, `ANALYSIS.md`, `SHA256SUMS.txt`.
- Builder `docs/benchmarks/m02/tools/build_analysis_integration.py`; relatório `analysis-integration.v1.json` + `ANALYSIS-INTEGRATION.md`.
- `qa_ledger.py` e `qa-ledger.v1.json`: campo `scene_analysis`/`scene_analysis_evidence`; S02–S04 `scene_analysis=PASS`.
- `tests/ci/test_m02_analysis_integration.py`, ajustes em `test_m02_qa_ledger.py` e `test_builder_check_enforcement.py`.
- README, REGRESSION-REPORT e QUALITY-LEDGER do M02.
- `.github/workflows/nex-ci-fastlane.yml`: enforcement do novo builder `--check`.
- Evidência, delta e este WO/lock.
- Promoção de checkpoint em PR documental separado.

## Fora de escopo

- Rendering, shaders, TAA, compositor, GPU, FPS ou qualidade visual.
- Integrar S05/S06 ou alterar cenas base, presets, contratos, renderer ou `project.godot`.
- Claims de ganho, generalização ou aprovação independente.
- Novos parents, runtime de produção ou issues PLANNING_ONLY.

## DoD

- As três cenas carregam e produzem análise determinística: 17/34/23 meshes, 8 occluders e 16 primitivas por cena.
- Sightline: 1 reveal e 1 danger alert por cena, sem ator crítico não visto.
- Depth: 0 z-fight risks em corridor, 4 em arena/city; 0 alpha-over-critical e 0 overlay-gameplay conflicts.
- Temporal: `BASELINE_ACCEPTABLE` em 5 frames e 16 regiões por cena.
- QA ledger S02–S04 `scene_analysis=PASS` com evidência; `scene_comparison`/`performance` permanecem `INCONCLUSIVE_NOT_RUN`.
- Suítes CI completas verdes; 30 comandos de builder/validator (28 module + 2 cross-module).
- PR protegida com checks verdes e checkpoint pós-merge verificado.

## STOP

- Base/HEAD divergente, divergência dos protótipos vendorizados, resultado não determinístico, QA ledger divergente, check vermelho ou tentativa de converter análise em claim de rendering → parar e registrar.
