# NEX reference build · Windows x86_64

**Status:** `REFERENCE_BUILD_VERIFIED / ADMIN_SOLO_NOT_INDEPENDENT`

**Source SHA:** `a872323b3eedc9cf442fd10e417b8ce70f01bae2` · **Godot:** 4.7.2.stable (`ed1daf0bf`)

## Artifact

- `build/NEXEngine.exe` · **109548888 bytes**
- SHA-256: `0f93eaa9c38c061ed7fae19009511dafd5d9f26eef806ac9f768393b7d6a3bdc`
- O executável não é versionado; `build/` é ignorado.

## Verificação

- Smoke do projeto staged: **PASS**
- Export release: **PASS**
- Executável headless: **PASS**
- GUI Windows: **PASS**

## Capturas GUI

| Arquivo | Dimensões | SHA-256 |
|---|---|---|
| `evidence/nex-mode-corridor.png` | 1296×759 | `99a0e0159d110dd1…` |
| `evidence/nex-mode-arena.png` | 1296×759 | `ba8f0ef851380dd3…` |
| `evidence/nex-mode-dense-city.png` | 1296×759 | `2fea218a76c5a049…` |
| `evidence/nex-mode-density.png` | 1296×759 | `bcf6907aa597b9a5…` |
| `evidence/nex-mode-arpg.png` | 1296×759 | `a81332a7b84c700e…` |
| `evidence/nex-mode-diagnostics.png` | 1296×759 | `d3f8825e2bd7cc05…` |

## Limitações

- reference visual lab export only; not a game, engine release or store build
- no installer, code signing, auto-update or distribution license
- no FPS, GPU p95, VRAM, quality or PoE2 parity claim
- GUI screenshots are local evidence, not a benchmark
- the executable is not committed; rebuild it with --build
- audit remains ADMIN_SOLO / NOT_INDEPENDENT

Gerado por `scripts/build_reference_export.py`; o executável deve ser reconstruído localmente.
