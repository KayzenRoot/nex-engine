# Checkpoint Delta · NEX-M12-FINAL-REFERENCE-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `c2c13c57b4de7a5114db2e2b79d37a7e026bfa62`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **M12 full reference admitido:** `NEX-ADR-0023` / `NEX-D-034`, bounded ao sistema de marca.
2. **Wordmark final:** NEX ENGINE em paths outline, sem dependência de fonte.
3. **Paleta canônica:** 5 tokens; Mist/Graphite 16.48:1; Cobalt/Graphite 4.27:1.
4. **App icons:** 9 PNGs, ICO 47845 bytes, ICNS 45394 bytes; 10 UI icons.
5. **`identity.v1`:** `READY_FOR_UI`, zero findings, 14 checks no smoke final.
6. **Builder:** `build_brand_kit.py --check` no Fast Lane.
7. **Gate:** `M12-FINAL-GATE.md`; issue #17 fechada após squash e checks.

## O que NÃO muda

- Nenhuma integração com editor UI, launcher, installer, hub, renderer ou binário.
- Nenhum required context, regra de proteção ou permissão de CI é alterado.
- Distribuição e trademark permanecem `DISTRIBUTION_TRADEMARK_PENDING`.
- Nenhum asset de terceiros, claim de FPS/qualidade ou paridade com PoE2.

## Evidência de apoio

- `.engineering/evidence/NEX-M12-FINAL-REFERENCE-WO-001-EVIDENCE.md`
- `assets/brand/`
- `docs/benchmarks/m12/brand-kit.v1.json`
- `docs/benchmarks/m12/M12-FINAL-GATE.md`
- `tests/ci/test_m12_final.py`
