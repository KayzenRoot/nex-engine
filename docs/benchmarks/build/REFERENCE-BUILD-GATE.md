# NEX reference build · final gate

**Status:** `REFERENCE_BUILD_VERIFIED / WINDOWS_X86_64 / LOCAL_EXPORT / ADMIN_SOLO_NOT_INDEPENDENT`
**Data:** 2026-11-17 · **Base:** `4f822fc9dbe7b2b54d12a470913b3c33ddb8f88b`
**Issue:** #300.

## O que foi concluído

| Área | Entrega | Evidência |
|---|---|---|
| Preset | Windows Desktop x86_64, PCK embutido | `nex_bench/export_presets.cfg` |
| Staging | Projetos aninhados e entry points standalone removidos | `scripts/build_reference_export.py` |
| Build | `build/NEXEngine.exe` 109522728 bytes | SHA-256 `9aae397e...` |
| Smoke | Projeto staged + executável headless | PASS |
| GUI | F1–F4 e F9; 5 capturas 1296×759 | `docs/benchmarks/build/evidence/` |
| CI | `--check` no Fast Lane | PASS |

## Resultado

- **Godot:** 4.7.2-stable (`ed1daf0bf...`), templates oficiais Windows x86_64.
- **Artefato:** 109522728 bytes; SHA-256 `9aae397ec302a4ba280db2e856abd15550ccab5bbfb989edd3cae1a74eb22f8c`.
- **GUI observada:** Forward+ / Vulkan, RTX 5050, 60 FPS observado (não benchmark), 28 draw calls, 766 objetos 3D, 88.0 MiB de renderer allocation.
- **Cenas:** corridor, arena, dense city e density ladder; diagnóstico F9 funcional.

## Limitações

- Build local de referência; não é release, installer ou distribuição.
- Sem code signing, auto-update, loja ou licença de distribuição.
- Sem alteração no engine Godot, renderer core, shader, cena de produção, gameplay ou rede.
- Sem asset de terceiros; ícone original do M12.
- **Nenhuma paridade com PoE2 é alegada.**
- Sem claim de FPS, GPU p95, VRAM ou qualidade.
- Distribuição/trademark permanecem `DISTRIBUTION_TRADEMARK_PENDING`.
- Auditoria `ADMIN_SOLO / NOT_INDEPENDENT`.

## Fechamento

Com este gate, a issue **#300** foi fechada como `COMPLETED` após o merge protegido da PR #301 (`8a23e418f251cca167cc611f439ce5c96db1ed0f`) e **14/14 checks pós-merge SUCCESS**. O executável deve ser reconstruído localmente com `python scripts/build_reference_export.py --build --gui`; ele não é versionado.
