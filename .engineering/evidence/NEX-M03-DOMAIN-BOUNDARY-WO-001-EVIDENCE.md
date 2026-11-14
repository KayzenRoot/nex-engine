# Evidence Bundle · NEX-M03-DOMAIN-BOUNDARY-WO-001

**Status:** `ANALYSIS_EVIDENCE / CALIBRATION_RESOLUTION_MATCH_ONLY / ADMIN_SOLO_NOT_INDEPENDENT`
**Parent:** M03 #8 · **Base:** `3a3b0f19d8e9e61e9eed4121391f0bc5a698e580`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `build_budget_validation.py` com `--domain` e `--check-domain`; saída curada inalterada.
- `budget-domain-boundary.v1.json` e `BUDGET-DOMAIN-BOUNDARY.md`: 6 células da arena (2 presets × 3 resoluções).
- `tests/ci/test_m03_domain_boundary.py`: 6 testes.
- Enforcement de `--check-domain` no job requerido: **21 comandos / 18 arquivos**.
- WO/lock/evidência/delta correspondentes.

## Resultado

- Previsto invariante à resolução: 0.379 ms (ab-low) e 0.460 ms (ab-high) nas três resoluções.
- Medido: ab-low 0.096/0.106/0.156 ms; ab-high 0.317/0.460/0.826 ms (960/1280/1920).
- Único acerto em 2%: **ab-high / 1280×720** (erro 0.0%); ab-high 960×540 +45.1%, 1920×1080 −44.3%.
- Deltas medidos 960→1920: **+0.060 ms (+62.5%)** ab-low e **+0.509 ms (+160.6%)** ab-high; previsto **0.0 ms**.
- Veredito **`CALIBRATION_RESOLUTION_MATCH_ONLY`**: o acerto de 2% é específico da resolução de calibração, não validade geral.

## Verificação

- `--check` e `--check-domain` PASS em worktree LF limpo sobre `3a3b0f19`.
- Suítes: CI **502**, contratos **203**, telemetria **31** — OK.
- Nenhum coeficiente, snapshot, GDScript, bundle M09, cena, harness, ruleset ou medição alterado.

## O que não foi feito / não é alegado

- Nenhuma nova medição, captura ou renderização real.
- Nenhum parent novo admitido; M04–M05, M07–M08 e M10–M12 seguem `NOT_ADMITTED`.
- Sem generalização cross-device/cross-sessão; uma cena, 100 proxies, uma sessão em RTX 5050.
- Nenhuma aprovação independente; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Rollback

Reverter builder, artefatos domain, README, testes, workflow, WO/lock/evidência/delta e a entrada de checkpoint correspondente.
