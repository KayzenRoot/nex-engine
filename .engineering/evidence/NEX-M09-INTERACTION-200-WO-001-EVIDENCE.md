# Evidence Bundle · NEX-M09-INTERACTION-200-WO-001 (200 proxies)

**Status:** `MEASUREMENT_EVIDENCE / SINGLE_SESSION / MEASURED_COST_OBSERVED / NO_GENERALIZATION`
**Issue:** #14 · **Base:** `c1b73743c0c95d9fb8867079cb91fb74cfc03d49` · **Measured source SHA:** `c1b73743c0c95d9fb8867079cb91fb74cfc03d49`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-interaction-200/`: 12 capturas COMPLETE, 12 validações PASS, manifesto, fatos, análise e SHA-256 de 27 arquivos.
- `docs/benchmarks/m09/interaction-200.v1.json`, `INTERACTION-200-REPORT.md` e builder determinístico.
- `tests/ci/test_interaction_200.py`: 9 testes.

## Sessão medida

- Windows · RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · Godot 4.7.2-stable.
- Cena `arena_combat`, 200 proxies (34 base + 166 fillers).
- Resoluções 960×540 e 1920×1080, viewport nativo.
- 3 runs por preset por resolução (L/H/L/H/L/H), 30 s por captura.
- Source medido: `c1b73743c0c95d9fb8867079cb91fb74cfc03d49`.

## Resultados (medianas de 3 runs)

| Proxies | Resolução | Preset | GPU p50 | GPU p95 | GPU p99 | CPU p95 | Pacing p95 | 1% low |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 200 | 960×540 | ab-low | 0.095 ms | 0.098 ms | 0.221 ms | 0.357 ms | 4.247 ms | 224.05 |
| 200 | 960×540 | ab-high | 0.315 ms | 0.322 ms | 0.468 ms | 0.503 ms | 4.264 ms | 224.91 |
| 200 | 1920×1080 | ab-low | 0.145 ms | 0.157 ms | 0.160 ms | 0.361 ms | 4.289 ms | 225.70 |
| 200 | 1920×1080 | ab-high | 0.838 ms | 0.845 ms | 1.052 ms | 0.518 ms | 4.294 ms | 225.11 |

- Delta high vs low (GPU p95): **+228.6% (960×540)** e **+438.2% (1920×1080)**.
- Resolução 960→1920: `ab-low` **+60.2%**, `ab-high` **+162.4%**.
- Contexto 100→200 (sessão separada): 960×540 +2.1%/+2.5%; 1920×1080 +9.0%/+2.3% (low/high).
- CPU p95 0.357/0.503 ms (960) e 0.361/0.518 ms (1920); pacing ~4.25–4.29 ms; 1% low −0.3% a +0.4%.

## Leitura

O padrão pixel-bound se mantém em 200 proxies: a resolução domina o custo GPU e o aumento de 100 para 200 proxies tem efeito pequeno (2.1–9.0%). O delta high vs low é maior em 1920×1080 do que em 960×540. A comparação 100→200 é cross-session e está rotulada como tal.

## Verificação

- 12/12 capturas COMPLETE e validadas; proxy count 200 e viewport conferem com o manifesto.
- 27 arquivos cobertos por `SHA256SUMS.txt`.
- `build_interaction_200.py --check` reproduz `interaction-200.v1.json`/`INTERACTION-200-REPORT.md`.
- Os demais builders M09 continuam reproduzindo seus relatórios.
- Suítes completas em worktree LF limpo verificadas antes do squash.
- PR protegida e checkpoint pós-merge verificados separadamente.

## O que não foi feito / não é alegado

- Nenhuma mudança nas cenas base, `project.godot`, hub, renderer, shaders ou engine.
- Sessão única; uma cena; 200 proxies; duas resoluções; 3 runs por célula.
- Contexto 50/100 vem de outra sessão; não é comparação same-session.
- Viewport nativo difere do stretch default do projeto.
- Nenhum claim de FPS de jogo, qualidade visual, ganho universal ou generalização.
- M09 parent (#14) permanece `NOT_ADMITTED`.

## Rollback

Remover o bundle de evidência, `interaction-200.v1.json`/`INTERACTION-200-REPORT.md`/builder, o teste novo e o delta/WO/lock correspondentes.

## Próximos passos

- 2560×1440, múltiplas cenas em 200 proxies ou outros hardwares exigem WO própria.
