# Checkpoint Delta · NEX-M09-RESOLVER-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `ec7048ff0c52671d2fb4d6b8e84aaf15ac9fef5d` · **Code SHA:** `bb320b3cd6f06ee355405b4d193348576081cc93`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M09-RESOLVER concluído como protótipo isolado:** carga/validação de `preset_pack.v1`, compatibilidade, resolução por tier/id, overrides e reduced motion.
2. **Parent M09 (#14) permanece NOT_ADMITTED.** Nenhum preset aplicado, engine, CI ou `project.godot`.
3. **Contrato `preset_pack.v1` consumido:** tiers, blocos, ranges e compatibilidade espelhados; nenhum contrato alterado.
4. **Runtime/performance:** `INCONCLUSIVE_NOT_RUN`; nenhum claim de FPS/qualidade.
5. **Próximos incrementos:** aplicação em runtime e M11/M12 exigem WO própria.

## O que NÃO muda

- M01–M08/M10–M12 permanecem como estão; nenhum checkpoint promovido por este delta.

## Evidência de apoio

- `.engineering/evidence/NEX-M09-RESOLVER-WO-001-EVIDENCE.md`
- `nex_modules/tools/preset_resolver/evidence/headless-smoke-2026-11-13.log` (`NEX_M09_RESOLVER_SMOKE_PASS: 50 checks`)
- `tests/ci/test_preset_resolver.py` (9 testes)
