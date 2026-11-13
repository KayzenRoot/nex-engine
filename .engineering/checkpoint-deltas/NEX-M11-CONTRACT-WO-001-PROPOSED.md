# Checkpoint Delta · NEX-M11-CONTRACT-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `ad18bdd64f7b9745bc606d36f36d2431ac708d10` · **Code SHA:** `292c8ac40902c9f4936304152d8850f04e3b527b`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **Contrato M11 v1 definido:** `asset_pipeline.v1` cobre estágios, licenças SPDX, dependências, import settings e orçamentos.
2. **Parent M11 (#16) permanece NOT_ADMITTED.** Nenhum import/cook/carregamento, engine, CI ou `project.godot`.
3. **Ownership prospectivo:** `nex_modules/assets/**` mapeado sem admissão implícita.
4. **Licenciamento/qualidade:** contrato de representação; nenhuma licença foi verificada ou aprovada.
5. **Próximos incrementos:** auditor/planejador de pipeline e M12 exigem WO própria.

## O que NÃO muda

- M01–M10 permanecem como estão; nenhum checkpoint promovido por este delta.

## Evidência de apoio

- `.engineering/evidence/NEX-M11-CONTRACT-WO-001-EVIDENCE.md`
- `tests/contracts/test_m11_asset_pipeline_contract.py` (19 testes)
- Suíte de contratos: 169 testes OK.
