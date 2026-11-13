# Evidence Bundle · NEX-M12-CONTRACT-WO-001 (Visual identity contract v1)

**Status:** `CONTRACT_ONLY / NO_BRAND_ASSETS / NO_BRAND_APPROVAL / NOT_MODULE_ADMISSION`
**Issue:** #17 · **Base:** `eca91947ad3785b33bbe7cf1bb1c7c09e6b78500` · **Code SHA:** `1dcc06059a9b2c5fa76ffe05c55df7622e4660e4`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `contracts/m12/identity.v1.schema.json`: paleta com papéis, tipografia, logo SVG (mark/wordmark/monochrome) com digests/viewBox, escala de spacing, acessibilidade/contraste e proveniência.
- `contracts/m12/ownership.v1.json`: ownership prospectivo de `nex_modules/brand/**`.
- `docs/contracts/m12.md`: invariantes, validação, ownership e compatibilidade.
- `tests/contracts/test_m12_identity_contract.py`: 18 testes, incluindo contraste WCAG calculado a partir dos hex.

## Invariantes verificados

- Tokens de paleta únicos; papéis `primary`/`background`/`foreground` obrigatórios; hex lowercase.
- Contraste foreground/background ≥ limite de texto; primary/error e success/warning ≥ limite de texto grande.
- Display > body; pesos únicos múltiplos de 100; line-height 1.0–2.5.
- viewBox com largura/altura positivas; digests SHA-256 lowercase; monochrome presente.
- Escala de spacing estritamente ascendente, ≥ base; largura máxima ≥320.
- Limite de texto grande ≤ limite de texto; focus ring ≥1 quando exigido.
- Proveniência exige evidência quando medida; FPS rejeitado.

## Verificação executada

```powershell
python -m unittest discover -s tests/contracts -p 'test_*.py' -v
```

Resultado: **187 testes OK** (169 preexistentes + 18 novos).

## O que não foi feito / não é alegado

- Nenhum logo, SVG, tema, token CSS ou asset de marca gerado.
- Nenhuma aprovação de marca ou contraste medido em tela; contraste é calculado dos hex declarados.
- M12 parent (#17) permanece `NOT_ADMITTED`; contratos M01–M11 inalterados.

## Rollback

Remover `contracts/m12/**`, `docs/contracts/m12.md`, o teste novo, este bundle, o delta e a WO/lock correspondentes.

## Próximos passos

- Geração/validação de assets de marca exige WO própria.
- M09 permanece não admitido.
