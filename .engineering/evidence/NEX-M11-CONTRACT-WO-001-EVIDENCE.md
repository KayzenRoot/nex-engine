# Evidence Bundle · NEX-M11-CONTRACT-WO-001 (Asset pipeline contract v1)

**Status:** `CONTRACT_ONLY / NO_IMPORT / NO_COOK / NO_LICENSE_CLEARANCE / NOT_MODULE_ADMISSION`
**Issue:** #16 · **Base:** `ad18bdd64f7b9745bc606d36f36d2431ac708d10` · **Code SHA:** `292c8ac40902c9f4936304152d8850f04e3b527b`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `contracts/m11/asset_pipeline.v1.schema.json`: identidade/digest, estágios raw→imported→cooked→validated, licença SPDX/atribuição/verificação, import settings, dependências, política de licenciamento, orçamentos de assets/bytes/texturas e proveniência.
- `contracts/m11/ownership.v1.json`: ownership prospectivo de `nex_modules/assets/**`.
- `docs/contracts/m11.md`: invariantes, validação, ownership e compatibilidade.
- `tests/contracts/test_m11_asset_pipeline_contract.py`: 19 testes.

## Invariantes verificados

- IDs de asset únicos; SHA-256 lowercase; estágios únicos e ordenados (um `pass` posterior exige todos os anteriores `pass`).
- `require_cooked_artifact` exige estágio `cooked` com `pass` e artifact digest.
- Licença rejeitada é inválida; `require_verified_license`/`allow_unverified` e allowlist SPDX aplicados; atribuição exigida quando configurada.
- Dependências existem, não são self e o grafo é acíclico.
- Orçamentos de assets/bytes totais/bytes de textura/licenças não verificadas.
- Performance/proveniência com disponibilidade explícita; FPS rejeitado.

## Verificação executada

```powershell
python -m unittest discover -s tests/contracts -p 'test_*.py' -v
```

Resultado: **169 testes OK** (150 preexistentes + 19 novos).

## O que não foi feito / não é alegado

- Nenhum asset importado, cookado, carregado ou verificado; nenhuma licença aprovada.
- Nenhum claim de qualidade, licenciamento ou performance.
- M11 parent (#16) permanece `NOT_ADMITTED`; contratos M01–M10 inalterados.

## Rollback

Remover `contracts/m11/**`, `docs/contracts/m11.md`, o teste novo, este bundle, o delta e a WO/lock correspondentes.

## Próximos passos

- Planejador/auditor de pipeline exige WO própria.
- M12 permanece não admitido.
