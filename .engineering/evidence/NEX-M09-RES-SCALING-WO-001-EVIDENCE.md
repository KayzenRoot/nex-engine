# Evidence Bundle · NEX-M09-RES-SCALING-WO-001 (escala de resolução)

**Status:** `MEASUREMENT_EVIDENCE / SINGLE_SESSION / MEASURED_COST_OBSERVED / NO_GENERALIZATION`
**Issue:** #14 · **Base:** `f796de1445ff3147b87d8e7a3afe08e83a9284a5` · **Measured source SHA:** `6ebb98e8c7c9c6a9a0aa3faae5af7e8d4290b7f5`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `NEX_PRESET_AB_NATIVE_RESOLUTION=1` no harness: desabilita o stretch `canvas_items` do projeto para que o viewport medido corresponda à janela solicitada.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-res-scaling/`: 18 capturas COMPLETE, 18 validações PASS, manifesto, fatos, análise e SHA-256 de 39 arquivos.
- `docs/benchmarks/m09/res-scaling.v1.json`, `RES-SCALING-REPORT.md` e builder determinístico.
- `tests/ci/test_res_scaling.py`: 10 testes, incluindo viewport por célula e reprodutibilidade.

## Sessão medida

- Windows · RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · Godot 4.7.2-stable.
- Cena `arena_combat`, 100 meshes; resoluções 960×540, 1280×720 e 1920×1080 (viewport nativo).
- 3 runs por preset por resolução (L/H/L/H/L/H), 30 s por captura.
- Source medido: `6ebb98e8c7c9c6a9a0aa3faae5af7e8d4290b7f5`.

## Resultados (medianas de 3 runs)

| Resolução | Preset | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low |
|---|---|---:|---:|---:|---:|---:|---:|
| 960×540 | ab-low | 0.093 ms | 0.096 ms | 0.222 ms | 0.322 ms | 4.202 ms | 227.25 |
| 960×540 | ab-high | 0.308 ms | 0.317 ms | 0.454 ms | 0.443 ms | 4.203 ms | 228.82 |
| 1280×720 | ab-low | 0.103 ms | 0.106 ms | 0.108 ms | 0.328 ms | 4.250 ms | 227.70 |
| 1280×720 | ab-high | 0.454 ms | 0.460 ms | 0.604 ms | 0.438 ms | 4.255 ms | 226.90 |
| 1920×1080 | ab-low | 0.142 ms | 0.156 ms | 0.159 ms | 0.329 ms | 4.242 ms | 226.27 |
| 1920×1080 | ab-high | 0.820 ms | 0.826 ms | 1.032 ms | 0.454 ms | 4.273 ms | 226.35 |

- Delta high vs low (GPU p95): **+230.2% (960×540)**, **+334.0% (1280×720)**, **+429.5% (1920×1080)**.
- Escala 960×540→1920×1080 (GPU p95): `ab-low` **+62.5%**, `ab-high` **+160.6%**.
- A/A spread de GPU p95: 0.0% / 0.9% / 0.6%; pacing ~4.2 ms; 1% low entre −0.4% e +0.7%.

## Nota de proveniência

A primeira tentativa, sem `NEX_PRESET_AB_NATIVE_RESOLUTION=1`, registrou viewport lógico 1280×720 em todas as capturas porque o projeto usa `window/stretch/mode="canvas_items"`. Essas capturas foram descartadas antes da montagem da evidência; as 18 capturas finais registram 960×540, 1280×720 e 1920×1080 no documento e no manifesto.

## Verificação

- 18/18 capturas COMPLETE e validadas; viewport do documento confere com o manifesto em cada run.
- 39 arquivos cobertos por `SHA256SUMS.txt`.
- `build_res_scaling.py --check` reproduz `res-scaling.v1.json`/`RES-SCALING-REPORT.md`.
- `build_ab.py`, `build_scaling.py`, `build_m01_ab.py` e `build_m01_visual.py` continuam reproduzindo os relatórios anteriores.
- Suítes completas em worktree LF limpo verificadas antes do squash.
- PR protegida e checkpoint pós-merge verificados separadamente.

## O que não foi feito / não é alegado

- Nenhuma mudança nas cenas base, `project.godot`, hub, renderer, shaders ou engine.
- Sessão única; uma cena; 3 runs por célula; 1920×1080 é o maior 16:9 testado.
- Viewport nativo difere do stretch default do projeto.
- Pacing limitado por `max_fps 240`; alocação não medida.
- Nenhum claim de FPS de jogo, qualidade visual, ganho universal ou generalização.
- M09 parent (#14) permanece `NOT_ADMITTED`.

## Rollback

Remover o flag de viewport nativo do harness, o bundle de evidência, `res-scaling.v1.json`/`RES-SCALING-REPORT.md`/builder, o teste novo e o delta/WO/lock correspondentes.

## Próximos passos

- 2560×1440, múltiplas cenas ou outros hardwares exigem WO própria.
