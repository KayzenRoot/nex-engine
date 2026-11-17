# Evidence Bundle · NEX-ARPG-DEMO-WO-001

**Status:** `ARPG_REFERENCE_DEMO_EVIDENCE / PROCEDURAL_ORIGINAL / LOCAL_BUILD / ADMIN_SOLO_NOT_INDEPENDENT`
**Issue:** #303 · **Base:** `a872323b3eedc9cf442fd10e417b8ce70f01bae2`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- Cena `nex_bench/scenes/arpg_demo/arpg_demo.tscn` com personagem, arena, tochas, dummy e câmera.
- Scripts `arpg_demo.gd` e `arpg_hud.gd`, 100% procedurais.
- Integração **F5 ARPG DEMO** no hub, com guardas de captura e GPU panel oculto no demo.
- Controles LMB/WASD, RMB/SPACE, wheel zoom.
- HUD com vida/mana, barra do dummy, slots e dicas.
- Smoke nativo atualizado; 6 capturas GUI; evidências de ataque e movimento.
- Reference build reexportado.

## Resultado

- **Artefato:** `build/NEXEngine.exe`, **109548888 bytes**, SHA-256 `0f93eaa9c38c061ed7fae19009511dafd5d9f26eef806ac9f768393b7d6a3bdc`.
- **Smoke staged/export/headless/GUI:** PASS.
- **Capturas GUI:** 6 × 1296×759 (corridor, arena, dense city, density, ARPG, diagnostics).
- **ARPG ataque:** dummy 100 → 82, barra atualizada, hit flash.
- **ARPG movimento:** clique no chão move o personagem; câmera segue e permanece dentro da arena.
- **Cena:** personagem com capuz/capa/espada emissiva, arena de pedra, pilares, arco, tochas, braseiros, runas e dummy.

## O que não foi feito / não é alegado

- Nenhum asset, nome, cena, shader ou personagem de Path of Exile/PoE2.
- Nenhuma paridade com PoE2; estilo é inspiração de gênero com conteúdo original.
- Nenhum gameplay completo, dano autoritativo, hitbox, física, rede, progressão ou save.
- Nenhum personagem de produção, rig, skin ou asset de terceiros.
- Nenhum installer, code signing, distribuição ou licença de marca.
- Nenhum claim de FPS, GPU p95, VRAM ou qualidade.
- Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; sem revisor independente.

## Rollback

Reverter a cena/scripts do demo, hub/smoke, scripts de build/captura, evidência/capturas, teste, ADR/ledger/WO/lock/evidência/delta, AGENTS/SCOPE/CHECKPOINT e o fechamento da issue.
