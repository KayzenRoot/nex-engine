# Checkpoint Delta · NEX-M06-FULL-ADVISORIES-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `8ca0e0f42b92e929bc87628436c893bd341f3ba7`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M06-FULL-ADVISORIES integrado:** 144 advisórios derivados do dataset completo `performance.v1`.
2. **Resultado:** 144/144 `pacing`; headroom 3.327–4.009 ms; maior GPU share 21.05%; frame alvo 4.167 ms.
3. **Enforcement:** `--check-full` adicionado ao job requerido; 20 comandos / 18 arquivos.
4. **Sem nova medição, captura, renderização ou mudança de contrato/observação/atlas.**
5. **Sem generalização:** sessão única em uma RTX 5050.

## O que NÃO muda

- M01/M02/M03/M06/M09 seguem bounded admitted; M04–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.

## Evidência de apoio

- `.engineering/evidence/NEX-M06-FULL-ADVISORIES-WO-001-EVIDENCE.md`
- `docs/benchmarks/m06/advisories-full.v1.json`
- `docs/benchmarks/m06/ADVISORIES-FULL.md`
- `tests/ci/test_m06_full_advisories.py` (6 testes)
