# NEX M05 · Final VFX gate

**Status:** `M05_VFX_REFERENCE_COMPLETE / OWNER_AUTHORIZED / ADMIN_SOLO_NOT_INDEPENDENT`
**Data:** 2026-11-15 · **Base:** `dd840f86023057a4dc8af92148cdf36911175613`
**Parent:** #10 · **Sub-issues:** #52 S01, #53 S02, #54 S03, #55 S04, #56 S05, #57 S06, #58 S07.

## O que foi concluído

| Sub-issue | Entrega | Evidência |
|---|---|---|
| #52 SpellFX | Ponte `spellfx.v1` com 12 checks | `nex_bench/scenes/m05_vfx/spell_fx.gd`; `spell-fx-smoke-2026-11-15.json` |
| #53 Elemental FX | Fire, frost, lightning, smoke, impact e projectile | `fx_library.gd`; 18 capturas em 3 cenas |
| #54 Projectile/HitEcho | Trilha de projétil e impacto visuais | `*_projectile.png`; `*_impact.png` |
| #55 Combat Clarity | 25 eventos com 8 luzes na arena | `arena_combat_all25.png` (28.055% de pixels) |
| #56 FX Budget/PulsePool | Budgets, expiração, cancelamento e stress | 12 checks; 9 runs + 3 baselines |
| #57 VFX R&D | Matriz GO/NO_GO | `vfx-runtime.v1.json` S06 |
| #58 QA/Steward | Validação, diffs, gate e PR | `vfx-runtime.v1.json`; este gate |

## Resultado

- **SpellFX:** 12/12 checks; `max_active=128`, `max_per_vfx=64`; autoridade de dano/hit permanece gameplay-owned.
- **Biblioteca:** 6 elementos originais; diferença mediana 1.000–7.065%; lightning no corredor chega a 36.666% por causa do feixe e da luz.
- **Capturas:** 19 PNGs 1920×1080 + 3 baselines; todas as imagens com efeito alteram pixels.
- **Stress:** GPU p95 **3.620/3.839/3.992 ms** e 1% low **220.73/221.40/104.48 FPS** para 1/25/100 eventos; baseline **3.210 ms / 219.73 FPS**.
- **Alocação:** +44.944 B (1), +1.776.912 B (25), +8.422.816 B (100) versus baseline.
- **Decisões:** GPUParticles3D/SpellFX/LightBridge GO; PulsePool/Projectile `GO_WITH_LIMITATIONS`; Combat Clarity e paridade PoE2 NO_GO.

## Limitações

- Sessão única, RTX 5050, driver NVIDIA 617.14; frames estáticos na matriz visual.
- Sem hit autoritativo, física de projétil, dano, hitbox ou colisão de partícula.
- Sem telegraphs, redução de flashes, ThreatBudget Scheduler ou acessibilidade.
- Sem warm pool, prewarm de shader, overdraw, VRAM ou import/cook.
- **Nenhum asset de terceiros. Nenhuma paridade com PoE2 é alegada.**
- Nenhum claim de FPS, qualidade cinematográfica ou ganho cross-device.
- Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; sem revisor independente.

## Fechamento

Com este gate, as issues **#52–#58 e #10** podem ser fechadas como `COMPLETED` após o merge protegido e os checks pós-merge. O próximo módulo base é **M06** (evidência/atlas), que deve consumir as capturas e os runs M05; M07–M12 continuam bounded.
