# Evidence Bundle · NEX-M06-FULL-ADVISORIES-WO-001

**Status:** `EVIDENCE_DERIVATION / ADMIN_SOLO_NOT_INDEPENDENT`
**Parents:** M06 #11 · M09 #14 · **Base:** `8ca0e0f42b92e929bc87628436c893bd341f3ba7`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `build_advisories.py` com `--full` e `--check-full`; `build_report`/`render_markdown` parametrizados sem alterar a saída curada.
- `advisories-full.v1.json` e `ADVISORIES-FULL.md`: **144 advisórios** derivados de `m09-observations-full.v1.json`.
- `tests/ci/test_m06_full_advisories.py`: 4 testes (cobertura, resumo, segurança, reprodutibilidade, curadoria intacta).
- `tests/ci/test_builder_check_enforcement.py` + workflow: `--check-full` no job requerido; **20 comandos / 18 arquivos**.
- WO/lock/evidência/delta correspondentes.

## Resultado

- 144/144 observações `pacing` no cap de 240 fps.
- Headroom de render **3.327–4.009 ms**; maior GPU share **21.05%**; frame alvo **4.167 ms**.
- Todas as recomendações `LOW` e `requires_measurement=true`; nenhum claim de FPS ou qualidade.
- Saída curada permanece byte-idêntica (12 advisórios; `--check` PASS).

## Verificação

- `--check-full` e `--check` PASS em worktree LF limpo sobre `8ca0e0f4`.
- Suítes: CI **495**, contratos **203**, telemetria **31** — OK.
- Nenhuma observação, atlas, contrato, cena, harness, ruleset ou medição alterada.

## O que não foi feito / não é alegado

- Nenhuma nova medição, captura ou renderização real.
- Nenhum parent novo admitido; M04–M05, M07–M08 e M10–M12 seguem `NOT_ADMITTED`.
- Sem generalização cross-device/cross-sessão; sessão única em uma RTX 5050.
- Nenhuma aprovação independente; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Rollback

Reverter builder, artefatos full, README, testes, workflow, WO/lock/evidência/delta e a entrada de checkpoint correspondente.
