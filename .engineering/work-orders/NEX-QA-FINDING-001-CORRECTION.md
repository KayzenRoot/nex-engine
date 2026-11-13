# NEX-QA-FINDING-001-CORRECTION | Correção controlada do achado QA

**Status:** `OWNER_ADMITTED_IN_SESSION / EXECUTABLE`
**Origem:** achado `QA-FINDING-001` do NEX-QA-AUDIT-WO-001 (Issue #20, PR #117).
**Admissão:** Owner instruiu "siga para os próximos passos" em 2026-11-13, após o relatório da onda listar esta correção como próximo passo legal.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014.
**Base:** `main` `797ed5b8154514f227cbdbefa6e104e1cc1bd900`.

## Escopo exato

- `nex_bench/telemetry/framepulse.py` — incluir `RecursionError` no tratamento de JSON inválido e converter em `FramePulseError`.
- `tests/ci/test_qa_audit_regressions.py` — exigir `FramePulseError` no caso de aninhamento profundo.
- `qa/bug-reports/NEX-QA-AUDIT-WO-001/REPORT.md` — atualizar o status do achado para `FIXED`.
- Este WO.

## Risco e comportamento

- **Risco:** LOW. Nenhuma mudança para entradas válidas; apenas a classe da exceção controlada para JSON excessivamente aninhado.
- **Antes:** `RecursionError` não capturado.
- **Depois:** `FramePulseError("invalid JSON telemetry: ...")`.
- Nenhuma constante, métrica, formato de saída ou regra de negócio alterada.

## DoD

- Teste de regressão exige `FramePulseError` para `"[" * 10000`.
- Suítes `tests/ci`, `tests/contracts`, `tests/telemetry` e `tests/m00` verdes.
- Seis checks obrigatórios verdes no HEAD exato; squash protegido ADMIN_SOLO.
- RELATÓRIO de QA atualizado; issue #20 permanece aberta (papel Bug Hunter não admitido), apenas o achado é fechado.

## STOP

- Qualquer regressão em entradas válidas ou falha de suíte → parar e reverter o commit.
- Necessidade de alterar contrato/schema ou outras partes do produto → fora de escopo; escalar.
