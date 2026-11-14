# Evidence Bundle · NEX-M12-VALIDATOR-WO-001 (Identity validator)

**Status:** `PROTOTYPE_EVIDENCE / ANALYSIS_ONLY / NO_ASSET_GENERATION / NO_BRAND_APPROVAL`
**Issue:** #17 · **Base:** `25113e7dfcb12091aeb79b77cb82c9e7aed95549` · **Code SHA:** `0df758843118bc48ab671fd21ae4dadb0255258e`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_modules/brand/tokens/`: projeto Godot autocontido com `identity_validator.gd`, `main.tscn`, `project.godot`, `smoke.gd`, `README.md` e log headless.
- `tests/ci/test_identity_validator.py`: 9 testes estruturais (arquivos/projeto, API, vocabulário `identity.v1`, vereditos/achados, ausência de geração de assets, marcador/evidência, limites, ausência de claim de marca/contraste em tela).

## Verificação executada

```powershell
& "<pinned Godot 4.7.2>" --headless --path nex_modules/brand/tokens `
  --rendering-method gl_compatibility --script res://smoke.gd
```

Resultado: **`NEX_M12_VALIDATOR_SMOKE_PASS: 36 checks`** (exit 0), log em `nex_modules/brand/tokens/evidence/headless-smoke-2026-11-14.log`.

Cobertura dos 36 checks:
- identidade válida: `READY_FOR_UI`, 8 tokens, 8 papéis, contraste de texto ≥4.5, 8 spacing steps, 3 variantes de logo, determinismo;
- paleta: token duplicado, papel obrigatório ausente, contraste de texto/primário/accent abaixo do limite;
- tipografia: display ≤ body, peso duplicado, peso não múltiplo de 100;
- logo: viewBox com largura/altura zero;
- spacing: escala não ascendente e valor abaixo da base;
- acessibilidade: threshold de texto grande acima do threshold de texto;
- proveniência `MEASURED` sem evidência;
- documentos inválidos: schema, paleta vazia, hex uppercase, focus ring zero;
- `clear()` e último relatório.

## O que não foi feito / não é alegado

- Nenhum logo, tema, SVG ou asset de UI gerado ou aprovado.
- Contraste calculado dos hex declarados, não medido em tela; tipografia/spacing validados estruturalmente.
- Aprovação de marca/trademark fora de escopo.
- Nenhum claim de FPS, rendering ou qualidade.
- M12 parent (#17) permanece `NOT_ADMITTED`.

## Rollback

Remover `nex_modules/brand/tokens/**`, `tests/ci/test_identity_validator.py`, este bundle, o delta e a WO/lock correspondentes.

## Próximos passos

- Geração/revisão real de marca e UI exige WO própria.
- Integração visual em cena exige WO de rendering.
