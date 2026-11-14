# Evidence Bundle · NEX-M09-INTERACTION-WO-001 (proxies × resolução)

**Status:** `MEASUREMENT_EVIDENCE / SINGLE_SESSION / MEASURED_COST_OBSERVED / NO_GENERALIZATION`
**Issue:** #14 · **Base:** `3af467648b0b8b7831fb99003a9a16e583553fe7` · **Measured source SHA:** `2ef072c70189d5d013a62b7efc821f81078ef6d1`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- Override de `NEX_PRESET_AB_PROXY_COUNT` em cenas M01, com contagem fixa em 100 preservada como default e falha se a cena base exceder o alvo.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-interaction/`: 24 capturas COMPLETE, 24 validações PASS, manifesto, fatos, análise e SHA-256 de 51 arquivos.
- `docs/benchmarks/m09/interaction.v1.json`, `INTERACTION-REPORT.md` e builder determinístico.
- `tests/ci/test_interaction.py`: 10 testes.

## Sessão medida

- Windows · RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · Godot 4.7.2-stable.
- Cena `arena_combat`: 50 proxies (34 base + 16 fillers) e 100 proxies (34 base + 66 fillers).
- Resoluções 960×540 e 1920×1080, viewport nativo.
- 3 runs por preset por célula (L/H/L/H/L/H), 30 s por captura.
- Source medido: `2ef072c70189d5d013a62b7efc821f81078ef6d1`.
- 25 proxies não foi usado porque a cena base já tem 34 meshes; remover geometria está fora de escopo.

## Resultados (medianas de 3 runs)

| Proxies | Resolução | Preset | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 50 | 960×540 | ab-low | 0.092 ms | 0.096 ms | 0.097 ms | 0.233 ms | 4.240 ms | 230.10 |
| 50 | 960×540 | ab-high | 0.302 ms | 0.307 ms | 0.309 ms | 0.304 ms | 4.242 ms | 229.92 |
| 50 | 1920×1080 | ab-low | 0.139 ms | 0.144 ms | 0.147 ms | 0.236 ms | 4.241 ms | 231.41 |
| 50 | 1920×1080 | ab-high | 0.812 ms | 0.820 ms | 1.043 ms | 0.306 ms | 4.240 ms | 230.18 |
| 100 | 960×540 | ab-low | 0.092 ms | 0.096 ms | 0.097 ms | 0.247 ms | 4.240 ms | 230.21 |
| 100 | 960×540 | ab-high | 0.309 ms | 0.314 ms | 0.316 ms | 0.320 ms | 4.240 ms | 228.85 |
| 100 | 1920×1080 | ab-low | 0.139 ms | 0.144 ms | 0.149 ms | 0.246 ms | 4.243 ms | 230.94 |
| 100 | 1920×1080 | ab-high | 0.820 ms | 0.826 ms | 1.013 ms | 0.330 ms | 4.243 ms | 229.02 |

- Delta high vs low (GPU p95): **+219.8% (50/960×540)**, **+469.4% (50/1920×1080)**, **+227.1% (100/960×540)**, **+473.6% (100/1920×1080)**.
- Resolução 960→1920 (GPU p95): `ab-low` +50.0% (50 e 100 proxies); `ab-high` +167.1% (50) e +163.1% (100).
- Proxies 50→100 (GPU p95): 0.0% no `ab-low`; +2.3% (960×540) e +0.7% (1920×1080) no `ab-high`.
- CPU p95 sobe 4.2–7.8% de 50 para 100 proxies; GPU p95 fica praticamente plano.
- Pacing ~4.24 ms; 1% low entre −0.8% e −0.1%.

## Verificação

- 24/24 capturas COMPLETE e validadas; proxies e viewport conferem com o manifesto.
- 51 arquivos cobertos por `SHA256SUMS.txt`.
- `build_interaction.py --check` reproduz `interaction.v1.json`/`INTERACTION-REPORT.md`.
- Os demais builders M09 continuam reproduzindo seus relatórios.
- Suítes completas em worktree LF limpo verificadas antes do squash.
- PR protegida e checkpoint pós-merge verificados separadamente.

## O que não foi feito / não é alegado

- Nenhuma mudança nas cenas base, `project.godot`, hub, renderer, shaders ou engine.
- Sessão única; uma cena; duas contagens; duas resoluções; 3 runs por célula.
- Viewport nativo difere do stretch default do projeto.
- Nenhum claim de FPS de jogo, qualidade visual, ganho universal ou generalização.
- M09 parent (#14) permanece `NOT_ADMITTED`.

## Rollback

Remover o override de proxy em M01, o bundle de evidência, `interaction.v1.json`/`INTERACTION-REPORT.md`/builder, o teste novo e o delta/WO/lock correspondentes.

## Próximos passos

- 200 proxies, 2560×1440, múltiplas cenas ou outros hardwares exigem WO própria.
