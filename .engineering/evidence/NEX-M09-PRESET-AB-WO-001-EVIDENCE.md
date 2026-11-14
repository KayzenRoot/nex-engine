# Evidence Bundle · NEX-M09-PRESET-AB-WO-001 (A/B/A real de presets)

**Status:** `MEASUREMENT_EVIDENCE / SINGLE_SESSION / MEASURED_COST_OBSERVED / NO_GENERALIZATION`
**Issue:** #14 · **Base:** `0cb02ec87fe950bc63f23b707120098993b71007` · **Measured source SHA:** `baf818ef934c418d111091af755e0a19ddd6ac9e` · **Evidence commit:** `94dbf71f19396f5dd3e01454271e1d5bf0078aac`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_bench/scenes/preset_ab/`: cena isolada que aplica `preset_pack.v1` em runtime, desliga vsync, limita a 240 fps e captura pelo `gpu_profile/session.gd` existente; validador dedicado delega ao canônico.
- `nex_bench/presets/preset_ab/presets.v1.json`: presets `ab-low` (0.5 scale, MSAA off, shadows low, atlas 1024, glow off) e `ab-high` (1.0, 4x, ultra, 4096, glow on), ambos target 240.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-preset-ab/`: 3 capturas COMPLETE, 3 validações PASS, manifesto de runs, fatos da sessão, análise e SHA-256.
- `docs/benchmarks/m09/`: `ab.v1.json`, `AB-REPORT.md`, builder determinístico e README.
- `tests/ci/test_preset_ab_harness.py`: 10 testes estruturais/reprodutibilidade.

## Sessão medida

- Windows · NVIDIA RTX 5050 · Vulkan 1.4.351 · Godot 4.7.2-stable.
- 1280×720 · vsync 0 · max_fps 240 · 200 proxies · `effect_mode: lights`.
- Sequência A/B/A: `ab-low` → `ab-high` → `ab-low`; 30 s por run.
- Source SHA medido: `baf818ef934c418d111091af755e0a19ddd6ac9e`.

## Resultados

| Run | Preset | GPU p95 | CPU p95 | Pacing p95 | 1% low |
|---|---|---:|---:|---:|---:|
| 1794650136-34991024 | ab-low | 0.147 ms | 0.357 ms | 4.199 ms | 228.54 |
| 1794650182-34960454 | ab-high | 0.746 ms | 0.467 ms | 4.222 ms | 228.34 |
| 1794650224-33725612 | ab-low | 0.147 ms | 0.366 ms | 4.204 ms | 229.75 |

Deltas `ab-high` vs mediana `ab-low`:
- GPU p95 **+407.5%** (0.147 → 0.746 ms).
- CPU p95 +29.2%.
- Pacing p95 +0.5%.
- 1% low −0.4%.
- A/A: GPU p95 +0.0%, CPU p95 +2.5%, pacing +0.1%, 1% low +0.5%.

## Verificação executada

- Três capturas `COMPLETE`, três validações `PASS`; 9 arquivos cobertos por `SHA256SUMS.txt`.
- Builder reproduz `ab.v1.json`/`AB-REPORT.md`; `--check` passa.
- Worktree LF limpo: **600 testes OK** — ci 343, contracts 203, telemetry 31, m00 23.
- PR e checks obrigatórios serão executados; squash protegido somente após todos verdes; checkpoint pós-merge verificado separadamente.

## O que não foi feito / não é alegado

- Nenhuma mudança em `nex_bench/project.godot`, `hub.gd`, renderer, shaders, engine ou CI.
- Sessão única; 1 run alto e 2 baixos; cena sintética 1280×720.
- Pacing limitado por `max_fps 240`; alocação do renderer é histórico da sessão, não VRAM.
- Nenhum claim de FPS de jogo, ganho universal, qualidade visual ou generalização entre cenas/hardware/drivers.
- M09 parent (#14) permanece `NOT_ADMITTED`.

## Rollback

Remover `nex_bench/scenes/preset_ab/**`, `nex_bench/presets/preset_ab/**`, o bundle de evidência, `docs/benchmarks/m09/**`, o teste novo, o delta e a WO/lock correspondentes.

## Próximos passos

- Repetir A/B/A em cenas M01 e com múltiplas repetições exige WO própria.
- Aplicação real de presets no engine continua fora de escopo.
