# Evidence Bundle · NEX-M03-DOMAIN-CONSOLIDATION-WO-001

**Status:** `ANALYSIS_EVIDENCE / CALIBRATION_RESOLUTION_MATCH_ONLY / ADMIN_SOLO_NOT_INDEPENDENT`
**Parent:** M03 #8 · **Base:** `0683631df4e047bfff2bf8a0c45dd6b0df9853dd`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `build_budget_validation.py`: helpers `_load_model`, `_domain_cell`, `_evidence_cells`, `_cell_table_lines`; blocos `proxy_robustness` (200/1280) e `high_resolution` (2560×1440).
- `budget-domain-boundary.v1.json` e `BUDGET-DOMAIN-BOUNDARY.md` regenerados.
- `README.md` atualizado; `test_m03_domain_boundary.py` com 7 testes.
- WO/lock/evidência/delta correspondentes.

## Resultado

- Grid de resolução: 6 células; 1 acerto em 2% (`ab-high`/1280×720, 0.0%).
- 200/1280: 2 células; `ab-high` −1.7% (dentro de 2%), `ab-low` +241.4%.
- 2560×1440: 2 células; `ab-high` −70.3%, `ab-low` +84.0%; nenhum acerto.
- `within_2pct_total = 2` (a mesma célula de calibração em 100 e 200 proxies).
- Veredito **`CALIBRATION_RESOLUTION_MATCH_ONLY`**: o acerto é específico de 1280×720, robusto a proxies e não sobrevive a 2560×1440.

## Verificação

- `--check` e `--check-domain` PASS em worktree LF limpo sobre `0683631d`.
- Suítes: CI **515**, contratos **203**, telemetria **31** — OK; 23/23 builders PASS.
- Nenhum coeficiente, snapshot, GDScript, bundle M09, contrato, cena, harness, ruleset ou medição alterado.

## O que não foi feito / não é alegado

- Nenhuma nova medição, captura ou renderização real.
- Nenhum parent novo admitido; M04–M05, M07–M08 e M10–M12 seguem `NOT_ADMITTED`.
- Sem generalização cross-device/cross-sessão; os recortes de 200/1280 e 2560×1440 vêm de sessões separadas.
- Nenhuma aprovação independente; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Rollback

Reverter builder, artefatos domain, README, teste, WO/lock/evidência/delta e a entrada de checkpoint correspondente.
