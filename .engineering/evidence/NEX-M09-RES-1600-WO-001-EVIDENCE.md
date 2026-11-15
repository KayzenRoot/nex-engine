# Evidence Bundle · NEX-M09-RES-1600-WO-001

**Status:** `MEASURED_EVIDENCE / SINGLE_SESSION / ADMIN_SOLO_NOT_INDEPENDENT`
**Parents:** M09 #14 · M06 #11 · **Base:** `b9fd2ed1cbde0625200b104fbd2c34796258dad3`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- Sessão de **6 capturas** em `arena_combat`, 100 proxies, 1600×900, A/B/A, 2 s warmup e 30 s observação.
- Evidence bundle `windows-rtx5050-2026-11-14-res-scaling-1600/`: 6 capturas, 6 validações PASS, manifesto, fatos, análise e SHA-256 (15 arquivos).
- Builder `build_res_scaling_1600.py`; relatório `res-scaling-1600.v1.json` + `RES-SCALING-1600-REPORT.md`.
- M06 atualizado para **162 observações / 10 bundles**; atlas e advisories regenerados.
- Atlas M09: **15 bundles, 162 capturas, 114 imagens, 483 arquivos, 15 source SHAs**.
- `tests/ci/test_res_scaling_1600.py` (6 testes); **27 comandos `--check` / 24 arquivos**.
- WO/lock/evidência/delta correspondentes.

## Resultado

- GPU p95 mediano: **0.133 ms** (`ab-low`) e **0.632 ms** (`ab-high`); high/low **+375.2%**.
- Deltas: 1280→1600 **+25.5%/+37.4%**; 1600→1920 **+17.3%/+30.7%**.
- Modelo M03: `ab-high` −27.2% (entre o match de 1280 e o erro de 1920); `ab-low` +185.0%.
- M06: 162/162 `pacing`; GPU p95 0.068–1.55 ms; pacing 4.199–4.312 ms; GPU share 36.29%.

## Verificação

- 6/6 capturas COMPLETE/PASS, proxy 100 e viewport 1600×900.
- `--check` do novo builder PASS; 27/27 builders PASS em worktree LF limpo.
- Suítes: CI **546**, contratos **203**, telemetria **31** — OK.
- Nenhum harness, cena, preset, contrato, modelo, renderer, shader ou `project.godot` alterado.

## O que não foi feito / não é alegado

- Nenhuma medição visual em 1600; apenas performance.
- Nenhuma generalização cross-device/cross-sessão; uma sessão em RTX 5050.
- Nenhum parent novo admitido; M07–M08 e M10–M12 seguem `NOT_ADMITTED`.
- Nenhuma aprovação independente; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Rollback

Remover o evidence bundle, builder/relatórios, refresh M06, atualização do atlas, testes, workflow, WO/lock/evidência/delta e a entrada de checkpoint correspondente.
