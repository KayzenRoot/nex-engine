# Evidence Bundle · NEX-M09-200-720-WO-001

**Status:** `MEASURED_EVIDENCE / SINGLE_SESSION / ADMIN_SOLO_NOT_INDEPENDENT`
**Parent:** M09 #14 · **M03 context:** #8 · **Base:** `99eaad041b84c373da33ec1bb8a5922c31f4dad4`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- Sessão de **6 capturas** em `arena_combat`, 200 proxies, 1280×720, A/B/A (low/high ×3), 2 s warmup e 30 s observação, VSync off, `max_fps 240`.
- Evidence bundle `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-arena-200-720/`: 6 capturas, 6 validações PASS, manifesto `runs.v1.json`, fatos, análise e SHA-256 (15 arquivos).
- Builder `build_interaction_200_720.py`; relatório `interaction-200-720.v1.json` + `INTERACTION-200-720-REPORT.md`.
- Atlas M09 atualizado para **11 bundles, 150 capturas de performance, 66 imagens, 399 arquivos e 11 source SHAs**.
- `tests/ci/test_interaction_200_720.py` (6 testes) e ajustes no atlas/enforcement; **22 comandos `--check` / 19 arquivos**.
- WO/lock/evidência/delta correspondentes.

## Resultado

- GPU p95 mediano: **0.111 ms** (`ab-low`) e **0.468 ms** (`ab-high`); high/low **+321.6%**.
- Contexto 100→200 em 1280×720: GPU p95 **+1.8%/+1.3%**; CPU p95 **+29.0%/+48.7%**; pacing ~4.23 ms.
- Modelo M03: `ab-high` previsto 0.460 ms vs medido 0.468 ms (**−1.7%**, dentro de 2%); `ab-low` previsto 0.379 ms vs 0.111 ms (**+241.4%**, fora).
- Conclusão: o acerto de 2% do `ab-high` em 1280×720 é robusto à mudança de 100→200 proxies; o erro do `ab-low` não é explicado por proxies.

## Verificação

- Todas as 6 capturas `COMPLETE` e `PASS` no validador dedicado, com proxy 200 e viewport 1280×720.
- `--check` do novo builder PASS; 22/22 builders PASS em worktree LF limpo.
- Suítes: CI **508**, contratos **203**, telemetria **31** — OK.
- Nenhum harness, cena, preset, contrato, coeficiente, snapshot, renderer, shader ou `project.godot` alterado.

## O que não foi feito / não é alegado

- Nenhuma generalização cross-device, cross-driver ou cross-sessão; uma sessão em RTX 5050.
- 2560×1440, animação, câmera dinâmica e efeitos temporais não cobertos.
- Nenhum parent novo admitido; M04–M05, M07–M08 e M10–M12 seguem `NOT_ADMITTED`.
- Nenhuma aprovação independente; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Rollback

Remover o evidence bundle, builder, relatórios, atualização do atlas, testes, workflow, WO/lock/evidência/delta e a entrada de checkpoint correspondente.
