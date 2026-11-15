# NEX-ADR-0012 · Admissão full reference do M01 e fechamento do laboratório

**Status:** `OWNER_DIRECTIVE / APPROVED_ON_GOVERNANCE_MERGE`
**Data:** 2026-11-15
**Owner:** KayzenRoot
**Auditoria:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Base de admissão:** `900d2b2d031a87048702625a1e98bc50905bc663`

## Contexto

O Owner autorizou explicitamente admitir e implementar a camada de rendering/runtime, produzir medições e golden images reais, fechar as decisões de budget M01 e marca M12, e executar os módulos de otimização/streaming, começando pela finalização do módulo base **M01**. A admissão bounded anterior (`NEX-ADR-0008`) cobria apenas contratos, cenas de referência, protótipos e evidência; ela não autorizava a aceitação plena do laboratório visual M01.

## Decisão

Admitir, de forma **full reference e bounded ao laboratório M01**:

- As três cenas base `corridor_static`, `arena_combat` e `dense_city`, com materiais, luzes e fillers determinísticos.
- O harness nativo `nex_bench/scenes/preset_ab/**` e o perfilador `nex_bench/gpu_profile/**` em modo janela nativa, VSync off e captura de viewport.
- A golden matrix 1920×1080 (3 cenas × 2 presets × 3 repetições), a comparação A/A/A e A/B com regiões fixas, e a aprovação `OWNER_APPROVED_ADMIN_SOLO`.
- O orçamento de performance 1080p (GPU/CPU/pacing/1% low) e a meta experimental 120 FPS, com a decisão do Owner registrada.
- A auditoria de licenças das cenas M01 e o gate final `M01-FINAL-GATE.md`.
- O fechamento das issues #21, #23, #27 e #6 após a integração protegida e o checkpoint.

## Escopo de arquivos admitido

- `nex_bench/scenes/base/**`, `nex_bench/scenes/preset_ab/**`, `nex_bench/presets/**`, `nex_bench/gpu_profile/**`.
- `docs/benchmarks/m01/**` e `tests/ci/test_m01*`.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m01-golden/**` e `...-m01-perf-1080/**`.
- `docs/benchmarks/m01/tools/build_golden_matrix.py` e `build_performance_budget.py`.

## Exclusões explícitas

- Nenhum jogo, gameplay, rede, servidor, MMORPG ou cena de produção.
- Nenhum renderer/runtime de M02–M12, shader customizado, `ShaderMaterial`, compositor, GI, sombras ou VFX reais.
- Nenhum asset de terceiros, loja de assets, cloud ou serviço pago.
- Nenhum claim de FPS/qualidade generalizado, cross-device ou input-to-photon.
- Nenhum relaxamento de CI, segurança, testes, locks, ruleset ou auditoria solo.

## Condições e gates

1. WO/Context Lock, evidência e todos os checks no HEAD exato.
2. Golden matrix e budget reproduzíveis por builders `--check`.
3. Aprovação do budget registrada como `OWNER_APPROVED`; a auditoria permanece `ADMIN_SOLO / NOT_INDEPENDENT`.
4. M02–M12 continuam bounded e exigem WO própria para rendering/runtime.
5. O fechamento de issues só ocorre após squash protegido e checks pós-merge verdes.

## Consequências

- M01 passa a ser o primeiro módulo base **concluído como laboratório de referência**, não como jogo.
- O baseline visual e o budget 1080p ficam disponíveis para M02–M06.
- A decisão de marca M12 permanece separada e não é coberta por este ADR.
