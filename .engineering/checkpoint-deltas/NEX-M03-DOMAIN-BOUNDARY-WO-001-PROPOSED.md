# Checkpoint Delta · NEX-M03-DOMAIN-BOUNDARY-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `3a3b0f19d8e9e61e9eed4121391f0bc5a698e580`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M03-DOMAIN-BOUNDARY integrado:** 6 células da arena em 960×540/1280×720/1920×1080.
2. **Resultado:** previsto invariante (0.379/0.460 ms); único acerto em 2% em ab-high/1280×720; deltas medidos 960→1920 +62.5% (low) e +160.6% (high).
3. **Veredito:** `CALIBRATION_RESOLUTION_MATCH_ONLY` — o acerto é específico da resolução de calibração.
4. **Enforcement:** `--check-domain` adicionado ao job requerido; 21 comandos / 18 arquivos.
5. **Sem nova medição, mudança de modelo, GDScript, bundle M09, contrato ou ruleset.**

## O que NÃO muda

- M01/M02/M03/M06/M09 seguem bounded admitted; M04–M05, M07–M08 e M10–M12 permanecem `NOT_ADMITTED`.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.

## Evidência de apoio

- `.engineering/evidence/NEX-M03-DOMAIN-BOUNDARY-WO-001-EVIDENCE.md`
- `docs/benchmarks/m03/budget-domain-boundary.v1.json`
- `docs/benchmarks/m03/BUDGET-DOMAIN-BOUNDARY.md`
- `tests/ci/test_m03_domain_boundary.py` (6 testes)
