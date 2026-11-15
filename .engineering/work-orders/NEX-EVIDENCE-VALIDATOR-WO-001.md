# NEX-EVIDENCE-VALIDATOR-WO-001 | Validador global de SHA256SUMS

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** instrução contínua do Owner de 2026-11-15; enabler de governança/qualidade sem novo parent.
**Base:** `main` `2215b2f9615230a3f5e1b477427410ae71fbf9e4`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** LOW.
**Lock:** `.engineering/context-locks/NEX-EVIDENCE-VALIDATOR-WO-001-EXECUTION.json`.

## Objetivo

Validar todos os `SHA256SUMS.txt` do repositório contra os arquivos commitados, aceitando as variantes LF/CRLF de bundles históricos, e corrigir de forma transparente a única divergência real encontrada.

## Escopo

- `docs/benchmarks/tools/validate_evidence.py`: varre bundles, resolve caminhos relativos ao bundle ou à raiz, valida SHA-256 e falha em linha malformada, arquivo ausente ou digest divergente.
- `tests/ci/test_evidence_validator.py`: 7 testes, incluindo rejeição de missing/tampered/malformed e aceitação de CRLF.
- Correção de `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-10-12-final-head/SHA256SUMS.txt` linha 30, com `CORRECTION.md` no bundle explicando o hash antigo, o novo e o que não mudou.
- Enforcement no Fast Lane como terceiro validador cross-module.
- WO/lock/evidência/delta e checkpoint.

## Fora de escopo

- Alterar qualquer arquivo de evidência (apenas a linha de manifesto incorreta).
- Alterar medições, relatórios, imagens, contratos, builders, ruleset ou permissões.
- Claims de performance, qualidade ou aprovação independente.

## DoD

- `validate_evidence.py --check`: **27 bundles / 803 entradas**, 0 erros.
- `CORRECTION.md` registra os hashes antigo/novo e a ausência de mudança no arquivo de evidência.
- Testes do validador verdes; suíte CI completa verde; 3 validadores cross-module no Fast Lane.
- PR protegida e checkpoint pós-merge verificado.

## STOP

- Base/HEAD divergente, novo mismatch não explicado, alteração de conteúdo de evidência, check vermelho ou tentativa de suprimir erro → parar e registrar.
