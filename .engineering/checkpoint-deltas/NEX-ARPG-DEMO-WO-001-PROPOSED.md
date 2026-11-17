# Checkpoint Delta · NEX-ARPG-DEMO-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `a872323b3eedc9cf442fd10e417b8ce70f01bae2`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **ARPG demo admitido:** `NEX-ADR-0025` / `NEX-D-036`, bounded e local.
2. **Cena F5:** personagem, arena, tochas, dummy, câmera e HUD procedurais.
3. **Controles:** LMB/WASD, RMB/SPACE, wheel zoom.
4. **Verificação:** smoke PASS, 6 capturas GUI, ataque 100→82, movimento por clique.
5. **Artefato:** `build/NEXEngine.exe`, 109548888 bytes, SHA-256 `0f93eaa9...`.
6. **Gate:** `ARPG-DEMO-GATE.md`; issue #303 fechada após squash e checks.

## O que NÃO muda

- Nenhum required context, regra de proteção ou permissão de CI é alterado.
- Nenhum asset ou paridade com PoE2; nenhum gameplay/rede/produção.
- Distribuição/trademark permanecem `DISTRIBUTION_TRADEMARK_PENDING`.
- Nenhum claim de FPS/qualidade ou revisão independente.

## Evidência de apoio

- `.engineering/evidence/NEX-ARPG-DEMO-WO-001-EVIDENCE.md`
- `docs/benchmarks/build/reference-build.v1.json`
- `docs/benchmarks/build/evidence/nex-mode-arpg.png`
- `docs/benchmarks/build/evidence/arpg-attack.png`
- `docs/benchmarks/build/evidence/arpg-move.png`
- `tests/ci/test_arpg_demo.py`
