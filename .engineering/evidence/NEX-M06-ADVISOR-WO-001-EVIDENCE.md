# Evidence Bundle · NEX-M06-ADVISOR-WO-001 (advisórios de performance)

**Status:** `EVIDENCE_SYNTHESIS / SINGLE_SESSION / NO_NEW_MEASUREMENT / ADMIN_SOLO_NOT_INDEPENDENT`
**Issue:** #59 · **Base:** `622037479c9aa56171612cffacbd8225f1de2215`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `docs/benchmarks/m06/advisories.v1.json`: 12 advisórios com headroom, shares GPU/CPU, frame alvo, recomendação e limitações.
- `docs/benchmarks/m06/ADVISORIES.md`: relatório humano.
- `docs/benchmarks/m06/tools/build_advisories.py`: builder determinístico com `--check`.
- `tests/ci/test_m06_advisories.py`: 5 testes.

## Resultados

- Bottlenecks: `pacing` em 12/12 observações.
- Headroom de render: **3.402–3.914 ms**; frame alvo a 240 fps: **4.167 ms**.
- Maior participação GPU no frame: **19.92%** (`m09-i200-1920-high`).
- Todas as recomendações exigem nova medição e explicitam que headroom não prova capacidade em cap menor.
- Nenhum claim de FPS, qualidade ou ganho universal.

## Semântica

- `render_headroom_ms = max(0, frame_pacing_ms - max(gpu_render_ms, cpu_render_ms))`.
- `gpu_share_of_frame_pct = gpu_render_ms / frame_pacing_ms * 100`.
- `cpu_share_of_frame_pct = cpu_render_ms / frame_pacing_ms * 100`.
- `render_headroom_vs_target_ms = max(0, 1000/max_fps - max(gpu, cpu))`.
- Recomendação `pacing`: re-medir com cap maior ou workload mais pesado antes de otimizar.

## Verificação

- 12/12 advisórios com IDs únicos; builder reproduz JSON e Markdown.
- Testes verificam valores, recomendação segura, ausência de claims proibidos e reprodutibilidade.
- Suítes completas em worktree LF limpo verificadas antes do squash.
- PR protegida e checkpoint pós-merge verificados separadamente.

## O que não foi feito / não é alegado

- Nenhuma captura nova, mudança de contrato, engine, cenas, `project.godot`, hub ou CI.
- Nenhum claim de FPS de jogo, qualidade visual, ganho universal ou generalização.
- M06 parent (#59) permanece `NOT_ADMITTED`.

## Rollback

Remover `advisories.v1.json`, `ADVISORIES.md`, o builder, o teste novo e o delta/WO/lock correspondentes.

## Próximos passos

- Medir em cap maior, coletar draw calls/VRAM ou admitir o parent M06 exige WO própria e, no caso de admissão, decisão do Owner.
