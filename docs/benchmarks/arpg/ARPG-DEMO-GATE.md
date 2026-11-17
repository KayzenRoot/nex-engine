# NEX ARPG reference demo · gate

**Status:** `ARPG_REFERENCE_DEMO_VERIFIED / ORIGINAL_PROCEDURAL_CONTENT / ADMIN_SOLO_NOT_INDEPENDENT`
**Data:** 2026-11-17 · **Base:** `a872323b3eedc9cf442fd10e417b8ce70f01bae2`
**Issue:** #303.

## O que foi concluído

| Área | Entrega | Evidência |
|---|---|---|
| Personagem | Capuz, capa, ombros, membros e espada emissiva | `arpg_demo.gd` |
| Arena | Piso, paredes, pilares, arco, tochas, braseiros e runas | `arpg_demo.gd` |
| Dummy | Vida, hit flash e restauração | `arpg_demo.gd` |
| HUD | Vida/mana, barra do dummy, slots e dicas | `arpg_hud.gd` |
| Integração | F5 ARPG DEMO no hub | `hub.gd`; smoke |
| Build | Executável 109548888 bytes | `reference-build.v1.json` |

## Resultado

- **Artefato:** `build/NEXEngine.exe` · **109548888 bytes** · SHA-256 `0f93eaa9c38c061ed7fae19009511dafd5d9f26eef806ac9f768393b7d6a3bdc`.
- **Smoke:** staged, export, headless e GUI PASS.
- **Capturas:** 6 × 1296×759; `nex-mode-arpg.png`, `arpg-attack.png`, `arpg-move.png`.
- **Ataque:** dummy **100 → 82**, barra e hit flash.
- **Movimento:** clique no chão move o personagem; câmera segue com clamp na arena.
- **Controles:** LMB/WASD, RMB/SPACE, wheel zoom.

## Limitações

- Demo de referência, não jogo ou release.
- Nenhum asset, nome, cena, shader ou personagem de Path of Exile/PoE2.
- **Nenhuma paridade com PoE2 é alegada.**
- Sem gameplay completo, dano autoritativo, hitbox, física, rede, progressão ou save.
- Sem personagem de produção, rig, skin ou asset de terceiros.
- Sem installer, code signing, distribuição ou licença de marca.
- Sem claim de FPS, GPU p95, VRAM ou qualidade.
- Distribuição/trademark permanecem `DISTRIBUTION_TRADEMARK_PENDING`.
- Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Fechamento

Com este gate, a issue **#303** pode ser fechada como `COMPLETED` após o merge protegido e os checks pós-merge. O demo é acessível por **F5** no executável de referência.
