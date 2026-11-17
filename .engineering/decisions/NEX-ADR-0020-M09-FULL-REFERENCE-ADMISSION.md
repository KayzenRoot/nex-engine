# NEX-ADR-0020 · Admissão full reference do M09 e ferramentas de editor

**Status:** `OWNER_DIRECTIVE / APPROVED_ON_GOVERNANCE_MERGE`
**Data:** 2026-11-17
**Owner:** KayzenRoot
**Auditoria:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Base de admissão:** `371ca4ab4a5f70debc96e84bba55aba3870fc9cf`

## Contexto

O Owner autorizou construir a NEX Engine de forma contínua e autônoma, finalizando os módulos base. O M09 já tinha contrato `preset_pack.v1`, o `PresetResolver` com 50 checks headless e uma grande campanha de benchmarks M09, mas não tinha ferramentas de lint de assets, guarda de importação nem geração de recipe reproduzível.

## Decisão

Admitir, de forma **full reference e bounded ao M09**:

- **PresetResolver:** manter o resolvedor determinístico de `preset_pack.v1` com 50 checks.
- **PerfLint:** lint determinístico de assets e cenas com orçamentos de textura, luzes, draw calls, alpha, sombras e cargas síncronas; 42 checks.
- **ImportGuard:** planejamento de importação com extensões permitidas, limites de bytes, SHA-256, conflitos e NOOP; nunca escreve ou sobrescreve arquivos.
- **BenchmarkRecipe:** geração e validação de recipe reproduzível com cena, preset, seed, driver, SHA e runs.
- **Fixtures determinísticas:** 4 arquivos de fixture e smoke headless.
- **Evidência:** `m09-editor-smoke-2026-11-17.json`, relatório `editor-tools.v1.json` e gate.
- **R&D/QA:** decisões GO/GO_WITH_LIMITATIONS e fechamento de #14 após squash protegido.

## Escopo de arquivos admitido

- `nex_modules/tools/editor_lab/**` (PerfLint, ImportGuard, RecipeBuilder, fixtures e smoke).
- `docs/benchmarks/m09/editor-tools.v1.json`, `EDITOR-TOOLS.md` e `tools/build_m09_editor_tools.py`.
- `tests/ci/test_m09_final.py`.
- Enforcement de builders e workflow CI.

## Exclusões explícitas

- Nenhuma importação real de asset, escrita em disco, overwrite ou pipeline de import/cook.
- Nenhum rendering, shader, cena de produção, editor core ou `project.godot` principal alterado.
- Nenhum asset gerado no Git além das fixtures determinísticas.
- Nenhum M10–M12, gameplay, rede, cloud ou asset de terceiros.
- Nenhum FPS, frame-time, VRAM, qualidade ou paridade com PoE2.
- Nenhum relaxamento de CI, segurança, testes, locks, ruleset ou auditoria solo.

## Condições e gates

1. WO/Context Lock, evidência e todos os checks no HEAD exato.
2. `build_m09_editor_tools.py --check` reproduz o relatório; smoke `42 checks` PASS.
3. PresetResolver smoke `50 checks` PASS; 4 fixtures determinísticas.
4. Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; auditoria permanece `ADMIN_SOLO / NOT_INDEPENDENT`.
5. M10–M12 continuam bounded e exigem WO própria.
6. O fechamento de issue só ocorre após squash protegido e checks pós-merge verdes.

## Consequências

- M09 passa a ser o nono módulo base concluído como **ferramentas de editor de referência**, não como jogo.
- M10–M12 podem consumir as recipes e o lint; M11 pode auditar as fixtures e licenças.
- ImportGuard e PerfLint permanecem ferramentas determinísticas, não benchmarks de hardware.
