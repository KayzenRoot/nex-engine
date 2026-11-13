# Evidence Bundle · NEX-M02-S07-WO-001 (QA and integration pack)

**Status:** `QA_PACK_EVIDENCE / STRUCTURAL_PASS / SCENE_AND_PERFORMANCE_INCONCLUSIVE / NO_MEASURED_GAIN`
**Issue:** #34 · **Base:** `9b40dac928d568cb7783b9e8ae830f35fa2acc21` · **Code SHA:** `e9d4000b80b6fd3cbfe00ce93ebe7a743053f8ea`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `docs/benchmarks/m02/qa-contract.v1.json`: statuses, regras, 3 cenas, procedimento de medição e interface M03–M06.
- `docs/benchmarks/m02/qa-ledger.v1.json`: 6 componentes (S01–S06) com evidência + SHA-256, status estrutural, comparação de cena e performance.
- `docs/benchmarks/m02/tools/qa_ledger.py`: `--write`/`--check`; rejeita PASS sem evidência, claim medido, defeito HIGH/CRITICAL e integração não serial.
- `REGRESSION-REPORT.md`, `QUALITY-LEDGER.md`, `INTERFACE-M03-M06.md`, `README.md`.
- `tests/ci/test_m02_qa_ledger.py`: 13 testes.

## Verificação executada

```powershell
python docs/benchmarks/m02/tools/qa_ledger.py --check
python -m unittest tests/ci/test_m02_qa_ledger.py -v
```

- `QA_LEDGER_OK`; ledger reprodutível (`build() == arquivo`), hashes de evidência conferidos.
- Testes: **13/13 PASS**.
- Suítes completas no worktree LF: ci, contracts, telemetry e m00 (registradas no PR).

## Estado do QA

| Componente | Estrutural | Cena (3 cenas) | Performance |
|---|---|---|---|
| S01–S05 | PASS | `INCONCLUSIVE_NOT_RUN` | `INCONCLUSIVE_NOT_RUN` |
| S06 | PASS | `NOT_APPLICABLE_RESEARCH` | `NOT_APPLICABLE_RESEARCH` |

- **Nenhum PASS de cena/performance** foi emitido: as 3 cenas M01 não foram executadas com as melhorias.
- Metas 1080p60/120 permanecem `ASPIRATIONAL_NOT_MEASURED`/`EXPERIMENTAL_NOT_MEASURED`.
- Defeitos HIGH/CRITICAL: 0; integração `SERIAL_STEWARD`, conflitos 0.
- Claims medidos: todos falsos.

## Limites

- Sem rendering, GPU, screenshots, frame-time ou VRAM; structural PASS é teste de lógica determinística.
- Sem alteração de engine, módulos, contratos, CI ou `project.godot`.
- O ledger detecta claims sem evidência; não substitui A/B/A real.

## Rollback

Remover `docs/benchmarks/m02/**`, `tests/ci/test_m02_qa_ledger.py`, este bundle e o delta. Nada de M01/S01–S06/contratos/CI/checkpoint é alterado.

## Próximos passos

1. Owner decide as hipóteses do atlas após evidência A/B/A real.
2. Para mover cena/performance de INCONCLUSIVE, executar as 3 cenas no RTX 5050 com o procedimento congelado.
3. M03–M06 consomem a interface com suas próprias WOs e evidências.
