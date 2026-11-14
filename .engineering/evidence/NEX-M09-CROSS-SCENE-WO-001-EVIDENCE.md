# Evidence Bundle · NEX-M09-CROSS-SCENE-WO-001 (interação em três cenas M01)

**Status:** `MEASUREMENT_EVIDENCE / SINGLE_SESSION / MEASURED_COST_OBSERVED / NO_GENERALIZATION`
**Issue:** #14 · **Base:** `2a03cbb799bd91cb56aa7ed1287a09d45bfaf8ce` · **Measured source SHA:** `2a03cbb799bd91cb56aa7ed1287a09d45bfaf8ce`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-cross-scene/`: 48 capturas COMPLETE, 48 validações PASS, manifesto, fatos, análise e SHA-256 de 99 arquivos.
- `docs/benchmarks/m09/cross-scene.v1.json`, `CROSS-SCENE-REPORT.md` e builder determinístico.
- `tests/ci/test_cross_scene.py`: 9 testes.

## Sessão medida

- Windows · RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · Godot 4.7.2-stable.
- Cenas `corridor_static` (17 base + fillers) e `dense_city` (23 base + fillers).
- 50/100 proxies × 960×540/1920×1080, viewport nativo.
- 3 runs por preset por célula (L/H/L/H/L/H), 30 s por captura.
- Source medido: `2a03cbb799bd91cb56aa7ed1287a09d45bfaf8ce`.

## Resultados (medianas de 3 runs)

### corridor_static

| Proxies | Resolução | Preset | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 50 | 960×540 | ab-low | 0.070 ms | 0.071 ms | 0.075 ms | 0.311 ms | 4.275 ms | 223.56 |
| 50 | 960×540 | ab-high | 0.270 ms | 0.280 ms | 0.416 ms | 0.427 ms | 4.252 ms | 224.80 |
| 50 | 1920×1080 | ab-low | 0.125 ms | 0.136 ms | 0.139 ms | 0.328 ms | 4.284 ms | 225.83 |
| 50 | 1920×1080 | ab-high | 0.778 ms | 0.784 ms | 0.991 ms | 0.425 ms | 4.242 ms | 226.20 |
| 100 | 960×540 | ab-low | 0.070 ms | 0.071 ms | 0.073 ms | 0.337 ms | 4.276 ms | 223.86 |
| 100 | 960×540 | ab-high | 0.270 ms | 0.280 ms | 0.416 ms | 0.442 ms | 4.293 ms | 224.15 |
| 100 | 1920×1080 | ab-low | 0.128 ms | 0.140 ms | 0.143 ms | 0.338 ms | 4.288 ms | 224.33 |
| 100 | 1920×1080 | ab-high | 0.785 ms | 0.790 ms | 0.998 ms | 0.451 ms | 4.259 ms | 225.86 |

### dense_city

| Proxies | Resolução | Preset | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 50 | 960×540 | ab-low | 0.067 ms | 0.068 ms | 0.069 ms | 0.306 ms | 4.261 ms | 223.73 |
| 50 | 960×540 | ab-high | 0.228 ms | 0.235 ms | 0.352 ms | 0.407 ms | 4.250 ms | 225.93 |
| 50 | 1920×1080 | ab-low | 0.109 ms | 0.122 ms | 0.125 ms | 0.320 ms | 4.243 ms | 225.54 |
| 50 | 1920×1080 | ab-high | 0.679 ms | 0.685 ms | 0.883 ms | 0.418 ms | 4.294 ms | 224.71 |
| 100 | 960×540 | ab-low | 0.068 ms | 0.069 ms | 0.071 ms | 0.326 ms | 4.247 ms | 225.84 |
| 100 | 960×540 | ab-high | 0.233 ms | 0.241 ms | 0.366 ms | 0.429 ms | 4.251 ms | 225.41 |
| 100 | 1920×1080 | ab-low | 0.110 ms | 0.124 ms | 0.126 ms | 0.330 ms | 4.281 ms | 223.48 |
| 100 | 1920×1080 | ab-high | 0.685 ms | 0.691 ms | 0.890 ms | 0.444 ms | 4.247 ms | 226.89 |

- Delta high vs low (GPU p95): corridor **+294.4% (960×540)** e **+464.3–476.5% (1920×1080)**; city **+245.6–249.3% (960×540)** e **+457.3–461.5% (1920×1080)**.
- Resolução 960→1920 (GPU p95): corridor `ab-low` +91.5–97.2%, `ab-high` +180.0–182.1%; city `ab-low` +79.4–79.7%, `ab-high` +186.7–191.5%.
- Proxies 50→100 (GPU p95): 0.0–2.9% em ambas as cenas; CPU p95 +29.6–37.3% high vs low.
- Pacing ~4.25 ms; 1% low entre −0.4% e +1.5%.

## Leitura

O padrão de `arena_combat` se repete: a resolução domina o custo GPU e o delta do preset cresce com a resolução; a contagem de proxies tem efeito pequeno no GPU e maior no CPU. Isto é consistente com custo pixel-bound no range de 50–100 meshes nas três cenas M01.

## Verificação

- 48/48 capturas COMPLETE e validadas; cena, proxies e viewport conferem com o manifesto.
- 99 arquivos cobertos por `SHA256SUMS.txt`.
- `build_cross_scene.py --check` reproduz `cross-scene.v1.json`/`CROSS-SCENE-REPORT.md`.
- Os demais builders M09 continuam reproduzindo seus relatórios.
- Suítes completas em worktree LF limpo verificadas antes do squash.
- PR protegida e checkpoint pós-merge verificados separadamente.

## O que não foi feito / não é alegado

- Nenhuma mudança nas cenas base, `project.godot`, hub, renderer, shaders ou engine.
- Sessão única; duas cenas; duas contagens; duas resoluções; 3 runs por célula.
- Viewport nativo difere do stretch default do projeto.
- Nenhum claim de FPS de jogo, qualidade visual, ganho universal ou generalização.
- M09 parent (#14) permanece `NOT_ADMITTED`.

## Rollback

Remover o bundle de evidência, `cross-scene.v1.json`/`CROSS-SCENE-REPORT.md`/builder, o teste novo e o delta/WO/lock correspondentes.

## Próximos passos

- 200 proxies, 2560×1440, outros hardwares ou cenas adicionais exigem WO própria.
