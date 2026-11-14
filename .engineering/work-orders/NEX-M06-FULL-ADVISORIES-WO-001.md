# NEX-M06-FULL-ADVISORIES-WO-001 | Advisórios derivados do dataset completo

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** continuação autônoma autorizada (NEX-ADR-0005); M06/M09 são `BOUNDED_ADMITTED_EVIDENCE_PIPELINE` desde NEX-ADR-0006.
**Base:** `main` `8ca0e0f42b92e929bc87628436c893bd341f3ba7`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`), NEX-ADR-0004 / NEX-D-014 / NEX-ADR-0005. **Risco:** STANDARD (derivação de evidência).
**Lock:** `.engineering/context-locks/NEX-M06-FULL-ADVISORIES-WO-001-EXECUTION.json`.

## Objetivo

Derivar advisórios determinísticos das **144 observações `performance.v1`** já integradas, completando a cadeia observações → atlas → advisórios sem nova medição. O modo `--full` reutiliza a mesma semântica de headroom, participação GPU/CPU e recomendação de baixo risco da seleção curada.

## Escopo

- `docs/benchmarks/m06/tools/build_advisories.py`: modos `--full` e `--check-full`; `build_report`/`render_markdown` parametrizados sem alterar a saída curada.
- `docs/benchmarks/m06/advisories-full.v1.json` e `ADVISORIES-FULL.md`: 144 advisórios.
- `docs/benchmarks/m06/README.md`: uso, resumo e limitações.
- `tests/ci/test_m06_full_advisories.py`: 6 testes de cobertura, resumo, segurança e reprodutibilidade.
- `tests/ci/test_builder_check_enforcement.py` e `.github/workflows/nex-ci-fastlane.yml`: enforcement de `--check-full` (20 comandos / 18 arquivos).
- Evidência, delta e este WO/lock.
- Promoção de checkpoint em PR documental separado.

## Fora de escopo

- Nova medição, captura, renderização real ou mudança de cena/harness.
- Alterar observações, atlas, contrato `performance.v1`, builders de conversão ou dados M09.
- Novos parents, runtime, renderer, shaders, hub, `project.godot`.
- Claims de FPS, qualidade, ganho universal ou generalização cross-device/sessão.

## DoD

- 144 advisórios únicos, todos `pacing`, com recomendação `LOW` e `requires_measurement`.
- Resumo: headroom 3.327–4.009 ms, maior GPU share 21.05%, frame alvo 4.167 ms.
- Saída curada permanece byte-idêntica (12 advisórios); `--check` e `--check-full` passam.
- Suítes CI/contratos/telemetria verdes em worktree LF limpo; PR protegida e checkpoint pós-merge.

## STOP

- Base/HEAD divergente, observação inválida, divergência da saída curada, necessidade de nova medição ou check vermelho → parar e registrar.
