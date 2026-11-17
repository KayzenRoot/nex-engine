# Checkpoint Delta · NEX-REFERENCE-BUILD-WO-001 (PROPOSED)

**Status:** `PROPOSED / NOT_PROMOTED / REQUIRES_OWNER_DECISION`
**Base:** `4f822fc9dbe7b2b54d12a470913b3c33ddb8f88b`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT`

## Delta proposto

1. **Reference build admitido:** `NEX-ADR-0024` / `NEX-D-035`, Windows x86_64 local.
2. **Preset:** Windows Desktop, PCK embutido, ícone ICO M12.
3. **Staging:** remove projetos aninhados e entry points standalone, preserva cenas base e density ladder.
4. **Artefato:** `build/NEXEngine.exe`, 109522728 bytes, SHA-256 `9aae397e...`.
5. **Verificação:** smoke staged, export, headless e GUI PASS; 5 capturas 1296×759.
6. **CI:** `build_reference_export.py --check` no Fast Lane.
7. **Gate:** `REFERENCE-BUILD-GATE.md`; issue #300 fechada após squash e checks.

## O que NÃO muda

- Nenhum required context, regra de proteção ou permissão de CI é alterado.
- Nenhum installer, assinatura, distribuição, engine/renderer ou cena de produção.
- Distribuição/trademark permanecem `DISTRIBUTION_TRADEMARK_PENDING`.
- Nenhum claim de FPS/qualidade ou paridade com PoE2.

## Evidência de apoio

- `.engineering/evidence/NEX-REFERENCE-BUILD-WO-001-EVIDENCE.md`
- `docs/benchmarks/build/reference-build.v1.json`
- `docs/benchmarks/build/REFERENCE-BUILD-GATE.md`
- `tests/ci/test_reference_build.py`
