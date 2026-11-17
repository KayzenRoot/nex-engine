# NEX-ADR-0025 · ARPG reference demo original

**Status:** `OWNER_DIRECTIVE / APPROVED_ON_GOVERNANCE_MERGE`
**Data:** 2026-11-17
**Owner:** KayzenRoot
**Auditoria:** `ADMIN_SOLO / NOT_INDEPENDENT`
**Base de admissão:** `a872323b3eedc9cf442fd10e417b8ce70f01bae2`
**Issue:** #303

## Contexto

O Owner pediu um personagem e um pequeno cenário de exemplo em estilo ARPG isométrico dark fantasy, inspirado no gênero de Path of Exile 2. O executável de referência não expõe editor nem endpoint MCP; por isso o conteúdo foi implementado diretamente no projeto Godot e recompilado no reference build existente.

## Decisão

Admitir, de forma **bounded e local**, um demo ARPG original:

- **Cena `arpg_demo`** integrada como **F5 ARPG DEMO** no hub.
- **Personagem procedural** com corpo, capuz, ombros, braços, pernas, capa e espada emissiva.
- **Arena procedural** de pedra com paredes, pilares, arco, tochas, braseiros e runas.
- **Dummy de treino** com vida, hit flash e restauração.
- **Controles ARPG:** LMB click-to-move, WASD, RMB/SPACE ataque, wheel zoom.
- **HUD original:** vida/mana, barra do dummy, slots e dicas.
- **Câmera isométrica** com follow e clamp dentro da arena.
- **Verificação:** smoke nativo, 6 capturas GUI, evidência de ataque e movimento, build exportado.

## Escopo de arquivos admitido

- `nex_bench/scenes/arpg_demo/**` (cena, personagem, HUD).
- `nex_bench/hub.gd`, `nex_bench/smoke.gd`.
- `scripts/build_reference_export.py`, `scripts/capture-reference-gui.ps1`.
- `docs/benchmarks/build/**`, `docs/benchmarks/arpg/**`.
- `tests/ci/test_reference_build.py`, `tests/ci/test_arpg_demo.py`.
- ADR/ledger/WO/lock/evidência/delta, AGENTS/SCOPE/CHECKPOINT e fechamento de #303.

## Exclusões explícitas

- Nenhum asset, nome, cena, shader, personagem, UI ou animação de Path of Exile/PoE2.
- Nenhuma paridade com PoE2; o estilo é inspiração de gênero, com conteúdo original.
- Nenhum gameplay completo, dano autoritativo, hitbox, física, rede, progressão ou save.
- Nenhum personagem de produção, rig, skin ou asset de terceiros.
- Nenhum installer, code signing, distribuição, licença de marca ou claim de FPS/qualidade.
- Nenhum relaxamento de CI, segurança, testes, locks, ruleset ou auditoria solo.

## Condições e gates

1. WO/Context Lock, evidência e todos os checks no HEAD exato.
2. F5 abre a cena no executável exportado; smoke headless PASS.
3. Ataque reduz o dummy e atualiza a barra; movimento por clique funciona.
4. 6 capturas GUI e evidências de ataque/movimento com hashes.
5. Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.
6. O fechamento de #303 só ocorre após squash protegido e checks pós-merge verdes.

## Consequências

- O visual lab passa a ter um exemplo ARPG interativo original.
- O demo é uma peça de referência, não um jogo ou release.
- Qualquer evolução para gameplay real exige nova Work Order e escopo próprio.
