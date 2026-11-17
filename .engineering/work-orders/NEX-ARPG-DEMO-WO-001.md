# NEX-ARPG-DEMO-WO-001 | Personagem e cenário ARPG original

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** `NEX-ADR-0025` / `NEX-D-036`; instrução do Owner de 2026-11-17 para criar personagem e cenário de exemplo em estilo ARPG.
**Base:** `main` `a872323b3eedc9cf442fd10e417b8ce70f01bae2`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** STANDARD (conteúdo procedural e demo local).
**Lock:** `.engineering/context-locks/NEX-ARPG-DEMO-WO-001-EXECUTION.json`.
**Issue:** #303.

## Objetivo

Adicionar ao visual lab um demo ARPG isométrico dark fantasy com personagem, arena, tochas, dummy de treino, câmera e HUD, integrado como F5 e verificado no executável exportado.

## Escopo

- `nex_bench/scenes/arpg_demo/arpg_demo.tscn`, `arpg_demo.gd`, `arpg_hud.gd`.
- `nex_bench/hub.gd` (F5, labels, guardas de captura) e `nex_bench/smoke.gd`.
- `scripts/build_reference_export.py` e `scripts/capture-reference-gui.ps1` (6 capturas).
- `docs/benchmarks/build/**` (evidência, capturas, gate) e `docs/benchmarks/arpg/**`.
- `tests/ci/test_reference_build.py`, `tests/ci/test_arpg_demo.py`.
- ADR/ledger/WO/lock/evidência/delta, AGENTS/SCOPE/CHECKPOINT e fechamento de #303.

## Fora de escopo

- Assets, nomes, cenas ou personagens de Path of Exile/PoE2; paridade com PoE2.
- Gameplay completo, dano autoritativo, hitbox, física, rede, progressão ou save.
- Personagem de produção, rig, skin, animação importada ou asset de terceiros.
- Installer, code signing, distribuição, licença de marca.
- FPS, GPU p95, VRAM, qualidade ou aprovação independente.

## DoD

- F5 ativa `ArpgDemo` no executável exportado.
- Personagem move por clique/WASD; ataque reduz o dummy de 100 para 82.
- HUD mostra vida/mana, barra do dummy e controles.
- Smoke headless **PASS**; 6 capturas GUI 1296×759; evidências de ataque/movimento.
- `build_reference_export.py --check` **PASS**; suíte CI/contracts/telemetry verde.
- PR protegida, checks pós-merge, checkpoint e issue #303 fechada.

## STOP

- Base/HEAD divergente, cena não carregando, F5 quebrado, ataque/movimento sem efeito, asset de terceiros, claim de paridade com PoE2, check vermelho ou distribuição não autorizada → parar e registrar.
