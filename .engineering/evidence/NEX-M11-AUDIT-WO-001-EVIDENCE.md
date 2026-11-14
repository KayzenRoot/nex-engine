# Evidence Bundle · NEX-M11-AUDIT-WO-001 (Asset pipeline auditor)

**Status:** `PROTOTYPE_EVIDENCE / ANALYSIS_ONLY / NO_IMPORT / NO_COOK / NO_LICENSE_CLEARANCE`
**Issue:** #16 · **Base:** `bc849b42fd8772bcbe35df9cec9d40cd80dffe93` · **Code SHA:** `30b3f211718b2dd0a9f3ecd497d1dc071e86fbdf`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_modules/assets/license_audit/`: projeto Godot autocontido com `asset_pipeline_auditor.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md` e log headless.
- `tests/ci/test_asset_pipeline_auditor.py`: 9 testes estruturais (arquivos/projeto, API, vocabulário `asset_pipeline.v1`, vereditos/achados, ausência de import/cook, marcador/evidência, limites, ausência de claim de licença/qualidade).

## Verificação executada

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/assets/license_audit `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Resultado: **`NEX_M11_AUDIT_SMOKE_PASS: 43 checks`** (exit 0), log em `nex_modules/assets/license_audit/evidence/headless-smoke-2026-11-14.log`.

Cobertura dos 43 checks:
- documento válido: `READY_FOR_INTEGRATION`, métricas de assets/bytes, zero high/medium, determinismo;
- duplicatas, ordem/falha/pendência de estágio, artefato cooked ausente;
- licença rejeitada/não verificada, verificação obrigatória, SPDX não permitido, atribuição ausente;
- dependência pendente/self/ciclo;
- orçamentos de assets/bytes totais/textura/licenças não verificadas;
- achados de qualidade: textura sem compressão (low), textura oversized (medium), modelo sem LODs (low);
- documentos inválidos: schema, assets vazios, asset id inválido;
- `clear()` e último relatório.

## O que não foi feito / não é alegado

- Nenhum asset importado, cookado, carregado ou renderizado; nenhuma licença verificada.
- Orçamentos usam `cooked_bytes` declarado, não o filesystem.
- Ciclos são aritmética de grafo; achados de qualidade são heurísticos estruturais.
- Nenhum claim de licenciamento, qualidade ou performance.
- M11 parent (#16) permanece `NOT_ADMITTED`.

## Rollback

Remover `nex_modules/assets/license_audit/**`, `tests/ci/test_asset_pipeline_auditor.py`, este bundle, o delta e a WO/lock correspondentes.

## Próximos passos

- Import/cook reais e auditoria de licença exigem WO de pipeline com ferramentas reais.
- M12 permanece não admitido.
