# Evidence Bundle · NEX-M06-FULL-REFRESH-WO-001

**Status:** `EVIDENCE_DERIVATION / ADMIN_SOLO_NOT_INDEPENDENT`
**Parents:** M06 #11 · M09 #14 · **Base:** `c7d6f7271b1bf4ef5aa2a7f60fd09a08784b78aa`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `convert_m09_observations.py`: dois novos bundles em `FULL_BUNDLES`; dataset completo com **156 observações**.
- `build_m09_atlas.py`: 9 bundles, contagem 156 e nova observação de pacing.
- `build_advisories.py`: `EXPECTED_OBSERVATIONS_FULL = 156`.
- Artefatos regenerados: `m09-observations-full.v1.json`, `m09-performance-atlas.v1.json`, `M09-PERFORMANCE-ATLAS.md`, `advisories-full.v1.json`, `ADVISORIES-FULL.md`.
- `README.md` e 3 testes atualizados; WO/lock/evidência/delta.

## Resultado

- 156 observações/sources, 9 bundles, todas `pacing`.
- Atlas: GPU p95 **0.068–1.55 ms** (mediana 0.226), pacing **4.199–4.311 ms**, maior GPU share **36.29%**.
- Advisories: **156**, headroom **2.716–4.009 ms**, maior GPU share **36.29%**, frame alvo 4.167 ms.
- Top cell: `res-scaling-1440` / `ab-high` / 2560×1440 / 100 proxies / 1.547 ms.
- Saída curada de 12 observações/advisórios inalterada.

## Verificação

- `--check-full`, `--check` e testes PASS em worktree LF limpo sobre `c7d6f727`.
- Suítes: CI **514**, contratos **203**, telemetria **31** — OK.
- Nenhum bundle M09, observação curada, contrato, modelo, cena, harness, ruleset ou medição alterado.

## O que não foi feito / não é alegado

- Nenhuma nova medição, captura ou renderização real.
- Nenhum parent novo admitido; M04–M05, M07–M08 e M10–M12 seguem `NOT_ADMITTED`.
- Sem generalização cross-device/cross-sessão.
- Nenhuma aprovação independente; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Rollback

Reverter os builders, artefatos regenerados, README, testes, WO/lock/evidência/delta e a entrada de checkpoint correspondente.
