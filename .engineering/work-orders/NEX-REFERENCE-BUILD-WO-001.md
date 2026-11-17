# NEX-REFERENCE-BUILD-WO-001 | Reference build Windows x86_64

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** `NEX-ADR-0024` / `NEX-D-035`; instrução do Owner de 2026-11-17 para compilar e testar após os módulos base.
**Base:** `main` `4f822fc9dbe7b2b54d12a470913b3c33ddb8f88b`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** STANDARD (build local e automação GUI).
**Lock:** `.engineering/context-locks/NEX-REFERENCE-BUILD-WO-001-EXECUTION.json`.
**Issue:** #300.

## Objetivo

Produzir um executável Windows x86_64 do visual lab unificado, com staging que preserve as cenas base, smoke headless, teste GUI F1–F4/F9, evidência de artefato e verificação `--check` no CI.

## Escopo

- `nex_bench/export_presets.cfg` e `nex_bench/icon.ico` (ICO original M12).
- `scripts/build_reference_export.py` e `scripts/capture-reference-gui.ps1`.
- `docs/benchmarks/build/reference-build.v1.json`, `REFERENCE-BUILD.md`, `evidence/` e `REFERENCE-BUILD-GATE.md`.
- `tests/ci/test_reference_build.py`; `--check` no Fast Lane.
- `.gitignore` para `build/` e `nex_bench/.godot/`.
- ADR/ledger/WO/lock/evidência/delta, AGENTS/SCOPE/CHECKPOINT e fechamento de #300.

## Fora de escopo

- Installer, code signing, auto-update, loja ou distribuição pública.
- Engine Godot, renderer core, shader, cena de produção, gameplay, rede.
- Assets de terceiros, aprovação de marca, licença de distribuição/trademark.
- FPS, GPU p95, VRAM, qualidade, paridade com PoE2.

## DoD

- `build_reference_export.py --build --gui` produz `build/NEXEngine.exe`.
- Smoke staged **PASS**; export **PASS**; headless **PASS**; GUI **PASS**.
- 5 capturas de janela 1296×759, com SHA-256 na evidência.
- `--check` **PASS**; suíte CI/contracts/telemetry verde.
- PR protegida, checks pós-merge e checkpoint.
- Issue #300 fechada com comentário de evidência.

## STOP

- Base/HEAD divergente, template ausente ou não oficial, smoke/export/headless/GUI falhando, `.exe` rastreado no Git, check vermelho, claim de distribuição/FPS/qualidade ou paridade com PoE2 → parar e registrar.
