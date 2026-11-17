# NEX reference build · Windows x86_64

**Status:** `REFERENCE_BUILD_VERIFIED / ADMIN_SOLO_NOT_INDEPENDENT`

**Source SHA:** `4f822fc9dbe7b2b54d12a470913b3c33ddb8f88b` · **Godot:** 4.7.2.stable (`ed1daf0bf`)

## Artifact

- `build/NEXEngine.exe` · **109522728 bytes**
- SHA-256: `9aae397ec302a4ba280db2e856abd15550ccab5bbfb989edd3cae1a74eb22f8c`
- O executável não é versionado; `build/` é ignorado.

## Verificação

- Smoke do projeto staged: **PASS**
- Export release: **PASS**
- Executável headless: **PASS**
- GUI Windows: **PASS**

## Capturas GUI

| Arquivo | Dimensões | SHA-256 |
|---|---|---|
| `evidence/nex-mode-corridor.png` | 1296×759 | `15ee141ffda7a461…` |
| `evidence/nex-mode-arena.png` | 1296×759 | `766d0e5941405744…` |
| `evidence/nex-mode-dense-city.png` | 1296×759 | `7b584e0e1bb77cdd…` |
| `evidence/nex-mode-density.png` | 1296×759 | `2f7534d0d95590ad…` |
| `evidence/nex-mode-diagnostics.png` | 1296×759 | `ab4df2848ceae089…` |

## Limitações

- reference visual lab export only; not a game, engine release or store build
- no installer, code signing, auto-update or distribution license
- no FPS, GPU p95, VRAM, quality or PoE2 parity claim
- GUI screenshots are local evidence, not a benchmark
- the executable is not committed; rebuild it with --build
- audit remains ADMIN_SOLO / NOT_INDEPENDENT

Gerado por `scripts/build_reference_export.py`; o executável deve ser reconstruído localmente.
