# Evidence Bundle · NEX-M09-M01-AB-WO-001 (A/B/A nas três cenas M01)

**Status:** `MEASUREMENT_EVIDENCE / SINGLE_SESSION / MEASURED_COST_OBSERVED / NO_GENERALIZATION`
**Issue:** #14 · **Base:** `51587de8cc8f713d3573a0bb6a52e7f19bb783a6` · **Measured source SHA:** `617db53d6752f30584b296f133e6990ca6602549`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- Harness `preset_ab` com `NEX_PRESET_AB_SCENE` para `corridor_static`, `arena_combat` e `dense_city`; cada cena reutiliza câmera/luzes e recebe fillers determinísticos até 100 meshes totais.
- `nex_bench/gpu_profile/session.gd`: layout de workload opcional e restrito; o default `built-in deterministic grid` permanece inalterado.
- Validador dedicado aceitando os três pares cena/layout M01 com contagem fixa de 100 e delegando os agregados ao validador canônico.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-ab/`: 18 capturas COMPLETE, 18 validações PASS, manifesto, fatos, análise e SHA-256 de 39 arquivos.
- `docs/benchmarks/m09/m01-ab.v1.json`, `M01-AB-REPORT.md`, builder determinístico e helpers compartilhados (`preset_report.py`) reutilizados pelos builders A/B/A e scaling.
- `tests/ci/test_m01_ab.py`: 16 testes, incluindo rejeição de layout/contagem/cena inválidos.

## Sessão medida

- Windows · RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · Godot 4.7.2-stable.
- 1280×720 · vsync 0 · max_fps 240 · effect_mode lights.
- 3 cenas × `ab-low`/`ab-high` × 3 runs (L/H/L/H/L/H por cena), 30 s por captura.
- Source SHA medido: `617db53d6752f30584b296f133e6990ca6602549`.

## Medianas por cena

| Cena | Preset | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low |
|---|---|---:|---:|---:|---:|---:|---:|
| corridor_static | ab-low | 0.083 ms | 0.088 ms | 0.215 ms | 0.347 ms | 4.208 ms | 229.24 |
| corridor_static | ab-high | 0.416 ms | 0.423 ms | 0.571 ms | 0.452 ms | 4.218 ms | 226.99 |
| arena_combat | ab-low | 0.103 ms | 0.109 ms | 0.246 ms | 0.345 ms | 4.218 ms | 228.03 |
| arena_combat | ab-high | 0.455 ms | 0.462 ms | 0.614 ms | 0.435 ms | 4.231 ms | 225.66 |
| dense_city | ab-low | 0.079 ms | 0.084 ms | 0.213 ms | 0.325 ms | 4.284 ms | 222.32 |
| dense_city | ab-high | 0.358 ms | 0.362 ms | 0.505 ms | 0.432 ms | 4.270 ms | 223.25 |

- Deltas high vs low (GPU p95): corridor **+380.7%**, arena **+323.9%**, city **+331.0%**.
- A/A stability (GPU p95 spread, 3 runs ab-low): corridor 3.4%, arena 7.3%, city 1.2%.
- Corridor ab-high tem outlier de primeira run (0.542 ms vs 0.421/0.423 ms); a mediana é reportada e o outlier documentado.
- Pacing ~4.2 ms em todas as células (cap 240 fps); 1% low entre −1.0% e +0.4%.

## Verificação

- 18/18 capturas COMPLETE e validadas; 39 arquivos cobertos por `SHA256SUMS.txt`.
- `build_m01_ab.py --check` reproduz `m01-ab.v1.json`/`M01-AB-REPORT.md`.
- `build_ab.py --check` e `build_scaling.py --check` continuam reproduzindo os relatórios anteriores após a extração de `preset_report.py`.
- Suítes completas em worktree LF limpo verificadas antes do squash.
- PR protegida e checkpoint pós-merge verificados separadamente.

## O que não foi feito / não é alegado

- Nenhuma mudança nas cenas base, `project.godot`, hub, renderer, shaders ou engine.
- Sessão única; 3 runs por célula; fillers podem sobrepor props das cenas.
- Pacing limitado por `max_fps 240`; alocação é histórico da sessão, não VRAM.
- Nenhum claim de FPS de jogo, ganho universal, qualidade visual ou generalização.
- M09 parent (#14) permanece `NOT_ADMITTED`.

## Rollback

Remover o modo M01 do harness, o layout opcional do `session.gd`, o validador M01, o bundle de evidência, `m01-ab.v1.json`/`M01-AB-REPORT.md`/builder, os testes novos, `preset_report.py` e o delta/WO/lock correspondentes; reverter os builders A/B/A e scaling ao código anterior.

## Próximos passos

- Mais repetições, golden images ou integração de presets no hub exigem WO própria.
- Aplicação real de presets no engine continua fora de escopo.
