# Evidence Bundle · NEX-EVIDENCE-VALIDATOR-WO-001

**Status:** `EVIDENCE_INTEGRITY_TOOL / NON_RENDERING / ADMIN_SOLO_NOT_INDEPENDENT`
**Base:** `2215b2f9615230a3f5e1b477427410ae71fbf9e4`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** LOW

## Entregue

- `docs/benchmarks/tools/validate_evidence.py`: valida todos os `SHA256SUMS.txt`, aceitando LF/CRLF, resolvendo caminhos relativos ao bundle ou à raiz.
- `tests/ci/test_evidence_validator.py` (7 testes): repositório íntegro, missing, tampered, CRLF, linha malformada e registro da correção.
- Correção da linha 30 do bundle `windows-rtx5050-2026-10-12-final-head` + `CORRECTION.md` transparente.
- Terceiro validador cross-module no Fast Lane.

## Resultado

- **27 bundles / 803 entradas** verificadas.
- **1 divergência histórica real** encontrada e corrigida: `GPU-DEVICE-SNAPSHOT.txt` (`ad93615…` → `f3488105…`), sem alterar os bytes da evidência.
- `EVIDENCE_SUMS_OK` após a correção; nenhuma outra divergência.
- Nenhuma medição, relatório, imagem, contrato, builder ou permissão alterada.

## Verificação

- `validate_evidence.py --check`: `EVIDENCE_SUMS_SCAN: 27 bundles / 803 entries` + `EVIDENCE_SUMS_OK`.
- Suíte CI completa e validadores cross-module verdes antes da PR.
- `CORRECTION.md` registra hashes antigo/novo e o que não mudou.

## O que não foi feito / não é alegado

- Nenhum arquivo de evidência foi modificado; apenas a linha de manifesto incorreta.
- Nenhum claim de performance, qualidade ou aprovação independente.
- Nenhuma supressão de erro; a divergência foi corrigida e documentada.

## Rollback

Reverter o validador/testes, a linha de manifesto e o `CORRECTION.md`, o workflow, WO/lock/evidência/delta e a entrada de checkpoint correspondente.
