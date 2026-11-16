# NEX-ADR-0016 · Admissão full reference do M05 e biblioteca de VFX

**Status:** `OWNER_DIRECTIVE / APPROVED_ON_GOVERNANCE_MERGE`
**Data:** 2026-11-15
**Owner:** KayzenRoot
**Auditoria:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Base de admissão:** `dd840f86023057a4dc8af92148cdf36911175613`

## Contexto

O Owner autorizou finalizar os módulos base com rendering/runtime real, após M01, M02, M03 e M04. O M05 já tinha contrato `spellfx.v1`, dataset de orçamento não-rendering e admissão bounded (`NEX-ADR-0009`/`NEX-ADR-0011`); faltavam a ponte de requests, a biblioteca elemental nativa, a integração de luzes, o stress concorrente e o gate final.

## Decisão

Admitir, de forma **full reference e bounded ao M05**:

- **SpellFX:** ponte de requests `spellfx.v1` com idempotência por `event_id`, autoridade de gameplay data-only, budgets `max_active=128`/`max_per_vfx=64`, tiers low/medium/high, cancelamento e expiração; 12 checks de smoke.
- **Biblioteca elemental:** seis efeitos originais (`fire`, `frost`, `lightning`, `smoke`, `impact`, `projectile`) em `GPUParticles3D` nativo com `ParticleProcessMaterial`, textura radial procedural e materiais emissivos; sem assets de terceiros.
- **Integração nativa:** `preset_ab` com `NEX_PRESET_AB_VFX`, `NEX_PRESET_AB_VFX_COUNT`, SpellFX e LightBridge M03; luzes VFX com `shadow_policy=none` e budget de grupo.
- **Evidência:** 19 capturas visuais a 1920×1080 em três cenas (6 elementos + 25 eventos), 3 baselines sem VFX, 9 runs de stress (1/25/100 eventos) e 3 runs baseline.
- **R&D/QA:** matriz GO/NO_GO, gate e fechamento de #52–#58 e #10 após squash protegido.

## Escopo de arquivos admitido

- `nex_bench/scenes/m05_vfx/**` (SpellFX, biblioteca, smoke).
- `nex_bench/scenes/preset_ab/preset_ab.gd` (flags e integração VFX/LightBridge).
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m05-vfx/**`.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m05-vfx-perf/**`.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-15-m05-vfx-baseline/**`.
- `docs/benchmarks/m05/**` e `tests/ci/test_m05_final.py`.
- Enforcement de builders e workflow CI.

## Exclusões explícitas

- Nenhum asset, shader, cena ou paridade com PoE2; **nenhuma paridade com PoE2 é alegada**.
- Nenhum hit autoritativo, física de projétil, dano, hitbox ou colisão de partícula.
- Nenhum telegraph, redução de flashes, ThreatBudget Scheduler ou opção de acessibilidade.
- Nenhum warm pool, prewarm de shader, overdraw, VRAM ou pipeline de import/cook.
- Nenhum renderer/runtime de M06–M12, jogo, gameplay, rede ou cloud.
- Nenhum claim generalizado de FPS/qualidade, cross-device ou cinematográfico.
- Nenhum relaxamento de CI, segurança, testes, locks, ruleset ou auditoria solo.

## Condições e gates

1. WO/Context Lock, evidência e todos os checks no HEAD exato.
2. `build_fx_budget_dataset.py --check` e `build_m05_runtime.py --check` reproduzem os artefatos.
3. SpellFX smoke `12 checks` PASS; 9 validações de stress PASS.
4. Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; auditoria permanece `ADMIN_SOLO / NOT_INDEPENDENT`.
5. M06–M12 continuam bounded e exigem WO própria.
6. O fechamento de issues só ocorre após squash protegido e checks pós-merge verdes.

## Consequências

- M05 passa a ser o quinto módulo base concluído como **VFX de referência**, não como jogo.
- M06/M09 herdam as capturas e os runs para evidência; M11 pode auditar os assets procedurais (originais).
- O custo de VFX fica documentado por evento (1/25/100), sem generalização para produção.
