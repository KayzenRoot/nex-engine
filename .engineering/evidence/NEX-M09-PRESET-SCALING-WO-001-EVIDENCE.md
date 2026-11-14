# Evidence Bundle · NEX-M09-PRESET-SCALING-WO-001 (Matriz 25/100/200)

**Status:** `MEASUREMENT_EVIDENCE / SINGLE_SESSION / MEASURED_COST_OBSERVED / NO_GENERALIZATION`
**Issue:** #14 · **Base:** `9babd8cb4f88c6cb5ac473c5ff77c82852293eb8` · **Measured source SHA:** `4e4719ac504ddb0ea7961d5c9d557c745f216990`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- Harness `preset_ab` parametrizado por `NEX_PRESET_AB_PROXY_COUNT` (25/50/100/200) e validador aceitando as quatro contagens.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-preset-scaling/`: 18 capturas COMPLETE, 18 validações PASS, manifesto de 18 runs, fatos, análise e SHA-256 de 39 arquivos.
- `docs/benchmarks/m09/scaling.v1.json`, `SCALING-REPORT.md` e builder determinístico.
- `tests/ci/test_preset_scaling.py`: 8 testes.

## Sessão medida

- Windows · RTX 5050 · Vulkan 1.4.351 · Godot 4.7.2-stable.
- 1280×720 · vsync 0 · max_fps 240 · effect_mode lights.
- 25/100/200 proxies × `ab-low`/`ab-high` × 3 runs (L/H/L/H/L/H por contagem).
- Source SHA medido: `4e4719ac504ddb0ea7961d5c9d557c745f216990`.

## Medianas por célula

| Count | Preset | GPU p95 | CPU p95 | Pacing p95 | 1% low |
|---:|---|---:|---:|---:|---:|
| 25 | ab-low | 0.128 ms | 0.298 ms | 4.249 ms | 224.69 |
| 25 | ab-high | 0.774 ms | 0.382 ms | 4.269 ms | 222.33 |
| 100 | ab-low | 0.139 ms | 0.310 ms | 4.264 ms | 223.63 |
| 100 | ab-high | 0.833 ms | 0.444 ms | 4.274 ms | 221.84 |
| 200 | ab-low | 0.152 ms | 0.374 ms | 4.274 ms | 218.93 |
| 200 | ab-high | 0.879 ms | 0.457 ms | 4.256 ms | 222.93 |

- Deltas high vs low: 25 **+504.7%**, 100 **+499.3%**, 200 **+478.3%** (GPU p95).
- Escala 25→200: `ab-low` **+18.7%**, `ab-high` **+13.6%**.
- Pacing ~4.267 ms em todas as células (cap 240 fps).
- Uma run 200/low tem 1% low outlier (157.39); medianas reportadas.

## Verificação

- 18/18 capturas COMPLETE e validadas; 39 arquivos cobertos por `SHA256SUMS.txt`.
- `build_scaling.py --check` reproduz `scaling.v1.json`/`SCALING-REPORT.md`.
- Suítes completas em worktree LF limpo verificadas antes do squash.
- PR protegida e checkpoint pós-merge verificados separadamente.

## O que não foi feito / não é alegado

- Nenhuma mudança em `project.godot`, hub, renderer, shaders, engine ou CI.
- Sessão única; 3 runs por célula; cena sintética 1280×720.
- Pacing limitado por `max_fps 240`; alocação é histórico da sessão, não VRAM.
- Nenhum claim de FPS de jogo, ganho universal, qualidade visual ou generalização.
- M09 parent (#14) permanece `NOT_ADMITTED`.

## Rollback

Remover a parametrização de proxy count, o bundle de evidência, `scaling.v1.json`/`SCALING-REPORT.md`/builder, o teste novo, o delta e a WO/lock correspondentes.

## Próximos passos

- Repetir a matriz em cenas M01 e/ou com mais repetições exige WO própria.
- Aplicação real de presets no engine continua fora de escopo.
