# NEX-ADR-0013 · Admissão full reference do M02 e fechamento do renderer

**Status:** `OWNER_DIRECTIVE / APPROVED_ON_GOVERNANCE_MERGE`
**Data:** 2026-11-15
**Owner:** KayzenRoot
**Auditoria:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Base de admissão:** `fa1adae7ab67e38c2556d126627006c338e2e8f4`

## Contexto

O Owner autorizou finalizar os módulos base com rendering/runtime real, começando pelo M01 e seguindo para o M02. A admissão bounded anterior (`NEX-ADR-0008`) cobria câmera, sightline, profundidade, temporal e perfis apenas como protótipos/análise; ela não autorizava a aceitação plena do renderer M02.

## Decisão

Admitir, de forma **full reference e bounded ao M02**, sobre as cenas M01:

- Câmera S01: aspect ratios, 3D↔tela, fast follow e golden de câmera.
- Sightline S02: reveal renderizado com parede/oclusor de teste, fade e custo GPU.
- DepthWeave S03: overlay alpha renderizado, sorting e conflitos.
- TemporalGuard S04: TAA nativo off/on em sequência de câmera; compositor customizado declarado NO_GO quando não há benefício.
- RenderPassport S05: capability passport runtime e perfis quality/balanced/performance reversíveis.
- S06 R&D: matriz GO/NO_GO; S07 QA: ledger e gate final.
- Fechamento de #28–#34 e #7 após squash protegido e checks pós-merge.

## Escopo de arquivos admitido

- `nex_bench/scenes/preset_ab/preset_ab.gd` (flags aditivas), `nex_bench/scenes/m02_camera/**`, `nex_bench/scenes/m02_temporal/**`.
- `nex_modules/render3d/profiles/runtime_probe.gd`.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m02-*`.
- `docs/benchmarks/m02/**` e `tests/ci/test_m02*`.

## Exclusões explícitas

- Nenhum renderer/runtime de M03–M12, shader customizado, compositor customizado, GI, sombras ou VFX reais.
- Nenhum jogo, gameplay, rede, cena de produção ou asset de terceiros.
- Nenhum claim generalizado de FPS/qualidade, cross-device ou input-to-photon.
- Nenhum relaxamento de CI, segurança, testes, locks, ruleset ou auditoria solo.

## Condições e gates

1. WO/Context Lock, evidência e todos os checks no HEAD exato.
2. Builders `--check` reproduzem o relatório runtime e o QA ledger.
3. Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; a auditoria permanece `ADMIN_SOLO / NOT_INDEPENDENT`.
4. M03–M12 continuam bounded e exigem WO própria.
5. O fechamento de issues só ocorre após squash protegido e checks pós-merge verdes.

## Consequências

- M02 passa a ser o segundo módulo base concluído como **renderer de referência**, não como jogo.
- O baseline M01 e o budget 1080p são consumidos pelo M02; o M03 herda o mesmo harness e as mesmas limitações.
- O compositor customizado de temporal permanece NO_GO; TAA nativo segue disponível.
