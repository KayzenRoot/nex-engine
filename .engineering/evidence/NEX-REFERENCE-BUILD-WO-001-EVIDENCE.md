# Evidence Bundle · NEX-REFERENCE-BUILD-WO-001

**Status:** `REFERENCE_BUILD_EVIDENCE / WINDOWS_X86_64 / LOCAL_EXPORT / ADMIN_SOLO_NOT_INDEPENDENT`
**Issue:** #300 · **Base:** `4f822fc9dbe7b2b54d12a470913b3c33ddb8f88b`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- Preset **Windows Desktop** x86_64 com PCK embutido e ícone ICO do M12.
- Staging que remove os `project.godot` aninhados e os entry points standalone, preservando as três cenas base e o density ladder.
- Scripts `build_reference_export.py` e `capture-reference-gui.ps1`.
- Executável `build/NEXEngine.exe` (não versionado).
- Evidência `reference-build.v1.json`, `REFERENCE-BUILD.md`, 5 capturas GUI e gate.
- Teste `tests/ci/test_reference_build.py` e `--check` no Fast Lane.

## Resultado

- **Godot:** 4.7.2-stable (`ed1daf0bf...`), templates oficiais Windows x86_64.
- **Artefato:** **109522728 bytes**, SHA-256 `9aae397ec302a4ba280db2e856abd15550ccab5bbfb989edd3cae1a74eb22f8c`.
- **Smoke staged:** PASS.
- **Export release:** PASS.
- **Executável headless:** PASS.
- **GUI Windows:** PASS; 5 capturas 1296×759 (corridor, arena, dense city, density ladder, diagnostics).
- **Diagnóstico observado:** Forward+ / Vulkan, RTX 5050, 60 FPS observado (não benchmark), 28 draw calls, 766 objetos 3D, 88.0 MiB de renderer allocation.
- **`--check`:** PASS.

## O que não foi feito / não é alegado

- Nenhum installer, code signing, auto-update, loja ou distribuição pública.
- Nenhuma alteração no engine Godot, renderer core, shader, cena de produção, gameplay ou rede.
- Nenhum asset de terceiros; o ícone é o ICO original do M12.
- Nenhum FPS, GPU p95, VRAM, qualidade, paridade com PoE2 ou aprovação de marca.
- Licença de distribuição/trademark permanece `DISTRIBUTION_TRADEMARK_PENDING`.
- Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; sem revisor independente.

## Rollback

Reverter preset/ícone/scripts/evidência/teste, remover `build/` local, reverter `.gitignore`, workflow, ADR/ledger/WO/lock/evidência/delta, AGENTS/SCOPE/CHECKPOINT e o fechamento da issue.
