# Evidence Bundle · NEX-M09-PRESET-AB-WO-001 (A/B/A real de presets)

**Status:** `MEASUREMENT_EVIDENCE / SINGLE_SESSION / MEASURED_COST_OBSERVED / NO_GENERALIZATION`
**Issue:** #14 · **Base:** `0cb02ec87fe950bc63f23b707120098993b71007` · **Measured source SHA:** `baf818ef934c418d111091af755e0a19ddd6ac9e` · **Evidence commit:** `94dbf71f19396f5dd3e01454271e1d5bf0078aac`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_bench/scenes/preset_ab/`: cena isolada que aplica `preset_pack.v1` em runtime, desliga vsync, limita a 240 fps e captura pelo `gpu_profile/session.gd` existente; validador dedicado delega ao canônico.
- `nex_bench/presets/preset_ab/presets.v1.json`: presets `ab-low` (0.5 scale, MSAA off, shadows low, atlas 1024, glow off) e `ab-high` (1.0, 4x, ultra, 4096, glow on), ambos target 240.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-preset-ab/`: 6 capturas COMPLETE, 6 validações PASS, manifesto de runs, fatos da sessão, análise e SHA-256.
- `docs/benchmarks/m09/`: `ab.v1.json`, `AB-REPORT.md`, builder determinístico e README.
- `tests/ci/test_preset_ab_harness.py`: 10 testes estruturais/reprodutibilidade.

## Sessão medida

- Windows · NVIDIA RTX 5050 · Vulkan 1.4.351 · Godot 4.7.2-stable.
- 1280×720 · vsync 0 · max_fps 240 · 200 proxies · `effect_mode: lights`.
- Sequência L/H/L/H/L/H: `ab-low` → `ab-high` → `ab-low` → `ab-high` → `ab-low` → `ab-high`; 30 s por run.
- Source SHA medido: `baf818ef934c418d111091af755e0a19ddd6ac9e`.

## Resultados

| Run | Preset | GPU p95 | CPU p95 | Pacing p95 | 1% low |
|---|---|---:|---:|---:|---:|
| 1794650136-34991024 | ab-low | 0.147 ms | 0.357 ms | 4.199 ms | 228.54 |
| 1794650182-34960454 | ab-high | 0.746 ms | 0.467 ms | 4.222 ms | 228.34 |
| 1794650224-33725612 | ab-low | 0.147 ms | 0.366 ms | 4.204 ms | 229.75 |
| 1794653881-34012975 | ab-high | 0.881 ms | 0.472 ms | 4.229 ms | 226.87 |
| 1794653926-33742838 | ab-low | 0.152 ms | 0.346 ms | 4.216 ms | 228.73 |
| 1794653968-33563891 | ab-high | 0.887 ms | 0.529 ms | 4.214 ms | 225.94 |

Deltas `ab-high` vs mediana `ab-low` (3 runs cada):
- GPU p95 **+499.3%** (0.147 → 0.881 ms).
- CPU p95 +32.2%.
- Pacing p95 +0.4%.
- 1% low −0.8%.
- A/A spread nas 3 runs baixas: GPU p95 3.4%, CPU p95 5.6%, pacing 0.4%, 1% low 0.5%.

## Verificação executada

- Seis capturas `COMPLETE`, seis validações `PASS`; 15 arquivos cobertos por `SHA256SUMS.txt`.
- Builder reproduz `ab.v1.json`/`AB-REPORT.md`; `--check` passa.
- Worktree LF limpo: **600 testes OK** — ci 343, contracts 203, telemetry 31, m00 23.
- PR e checks obrigatórios serão executados; squash protegido somente após todos verdes; checkpoint pós-merge verificado separadamente.

## O que não foi feito / não é alegado

- Nenhuma mudança em `nex_bench/project.godot`, `hub.gd`, renderer, shaders, engine ou CI.
- Sessão única; 3 runs baixos e 3 altos; cena sintética 1280×720.
- Pacing limitado por `max_fps 240`; alocação do renderer é histórico da sessão, não VRAM.
- Nenhum claim de FPS de jogo, ganho universal, qualidade visual ou generalização entre cenas/hardware/drivers.
- M09 parent (#14) permanece `NOT_ADMITTED`.

## Rollback

Remover `nex_bench/scenes/preset_ab/**`, `nex_bench/presets/preset_ab/**`, o bundle de evidência, `docs/benchmarks/m09/**`, o teste novo, o delta e a WO/lock correspondentes.

## Próximos passos

- Repetir A/B/A em cenas M01 e com múltiplas repetições exige WO própria.
- Aplicação real de presets no engine continua fora de escopo.
