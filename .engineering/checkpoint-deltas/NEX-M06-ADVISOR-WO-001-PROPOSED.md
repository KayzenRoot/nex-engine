# Checkpoint Delta · NEX-M06-ADVISOR-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `622037479c9aa56171612cffacbd8225f1de2215`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M06-ADVISOR integrado:** 12 advisórios derivados das observações `performance.v1`, com headroom, shares GPU/CPU, frame alvo e recomendação de baixo risco.
2. **Medição derivada:** todos `pacing` no cap de 240 fps; headroom 3.402–3.914 ms; maior share GPU 19.92%.
3. **Sem nova medição:** síntese determinística de evidência existente; nenhum contrato, engine, cena ou CI alterado.
4. **Parent M06 (#59) permanece NOT_ADMITTED.** Nenhum claim de FPS, qualidade ou ganho.
5. **Sem generalização:** 12 observações de uma sessão única em uma RTX 5050.

## O que NÃO muda

- M01–M05/M07–M12 permanecem como estão; nenhum checkpoint promovido por este delta.

## Evidência de apoio

- `.engineering/evidence/NEX-M06-ADVISOR-WO-001-EVIDENCE.md`
- `docs/benchmarks/m06/advisories.v1.json` e `ADVISORIES.md`
- `tests/ci/test_m06_advisories.py` (5 testes)
