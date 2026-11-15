# Checkpoint Delta · NEX-EVIDENCE-VALIDATOR-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `2215b2f9615230a3f5e1b477427410ae71fbf9e4`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **Validador global de evidência:** `validate_evidence.py --check` cobre 27 bundles / 803 entradas.
2. **Correção histórica transparente:** `GPU-DEVICE-SNAPSHOT.txt` (`ad93615…` → `f3488105…`) com `CORRECTION.md`; bytes da evidência inalterados.
3. **Enforcement:** terceiro validador cross-module no Fast Lane.
4. **Sem mudança de medição, relatório, imagem, contrato, builder, ruleset ou permissão.**
5. **Sem supressão de erro, claim de performance, qualidade ou aprovação independente.**

## O que NÃO muda

- Todos os parents M01–M12 seguem bounded admitted; nenhum parent muda de status.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.
- Nenhum runtime, hub, engine, `project.godot` principal ou cena de produção é admitido.

## Evidência de apoio

- `.engineering/evidence/NEX-EVIDENCE-VALIDATOR-WO-001-EVIDENCE.md`
- `docs/benchmarks/tools/validate_evidence.py`
- `tests/ci/test_evidence_validator.py` (7 testes)
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-10-12-final-head/CORRECTION.md`
