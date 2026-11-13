# NEX M01 · Baseline congelado (audit pack)

**Status:** `FROZEN_PROPOSED / NOT_ENGINE_COMPLETION / NOT_A_BENCHMARK_CLAIM`
**Work Order:** NEX-M01-S07-WO-001 (Issue #27) · **Modo:** ADMIN_SOLO `NOT_INDEPENDENT`
**Base:** `871fd1bc89c272ba04327ddc81e407d35ff5fee0`
**Manifesto verificável:** [`manifest.json`](manifest.json) (SHA-256 de cada artefato referenciado)

## O que está congelado

| Dimensão | Valor congelado |
|---|---|
| Engine | Godot `4.7.2-stable`, commit upstream `ed1daf0bf001b61586d9930840f2f1394092c079` |
| Binário oficial | SHA-256 `ab1824f85bfd8e0e4128182c000c4003a3e042245b2967848d089b2a04b22424` |
| Toolchain lock | `.nex/toolchain/NEX-M00-WO-001-toolchain-lock.json` |
| Renderer/driver | `forward_plus` / Vulkan 1.4.351 |
| GPU/driver | NVIDIA GeForce RTX 5050, driver `617.14` |
| Host | Windows 11 build 26300 (referência; RAM total não auditada) |
| Viewport | 1280×720, VSync 1, `max_fps = 0` |
| Contratos | `contracts/m01/*` (integrados), `contracts/m02/render_core.v1`, `contracts/m07/render2d.v1` |
| S04 workload | Density Ladder, seed `20261012`, counts 25/50/100/200, combined 25-only |
| S05 workload | Lighting Matrix, presets determinísticos, counts 25/100/200, combined 25-only |
| Medição | 2 s warmup + 30 s observação por run, validador independente |

## Matrizes verificadas

- **S04:** 12/12 capturas `COMPLETE` (25g 3/3, 100g 3/3, 200g 3/3, 25 combined 3/3), 1800–2250 amostras de pacing por run; 8 históricas + 4 da retomada.
- **S05:** 15/15 capturas `COMPLETE` (5 presets × counts, combined 25-only, baseline-25 ×3), 1800 amostras por run; spreads de baseline-25 = 0,002 ms (GPU p50).
- **S02:** FramePulse sintético `SYNTHETIC_NOT_MEASURED` (não é profiling real).
- **S03:** comparador Visual Truth determinístico (testes sintéticos; sem goldens de hardware além das capturas S04).
- **S06:** radar de pesquisa, sem medições.

## O que NÃO está congelado / não é afirmado

- **Não** é conclusão do engine, do parent M01 ou de M02–M12.
- **Não** há meta de FPS atingida: os runs usam 1280×720 com VSync; metas 1080p60/120 permanecem **aspiracionais**.
- **Não** há comparação entre sessões de pacing diferentes (~75 vs ~60 callbacks/s) nem input-to-photon.
- **Não** há VRAM total medida; `RENDERER_ALLOCATION_BYTES` é alocação do renderer e histórico da sessão.
- **Não** há medição cloud/Docker/Linux substituindo Windows nativo; CI headless é smoke, não benchmark.
- O resize-negative do S04 permanece `NOT_EXERCISABLE` sob `canvas_items`.
- O crash histórico `0xC0000005` do M00 permanece de causa desconhecida, risco residual aceito pelo Owner.

## Como reproduzir a auditoria

```powershell
python docs/benchmarks/m01/tools/build_manifest.py --check
python -m unittest discover -s tests/ci -p "test_m01_baseline_audit.py" -v
```

`build_manifest.py --check` recalcula todos os SHA-256 e falha se qualquer byte divergir. O manifesto não duplica arquivos grandes; ele referencia caminhos e digests.
