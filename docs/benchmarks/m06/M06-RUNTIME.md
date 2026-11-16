# NEX M06 · Performance runtime

**Status:** `M06_PERFORMANCE_REFERENCE_DERIVED / NATIVE_LAB / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`

**Source SHA:** `c763319d04d0bf353c15db8378872bdf8fab1734` · **GPU:** NVIDIA GeForce RTX 5050 · 4.7.2-stable

## S01 · Bottleneck Atlas

- **BOTTLENECK_ATLAS_DERIVED**: 33 grupos nativos.
- Classificações: `{'pacing': 11, 'gpu': 22}`.

## S02 · BatchWeave

| Cena | Variante | GPU p95 | CPU p95 | Draw calls | GPU vs individual | Pixels |
|---|---|---:|---:|---:|---:|---:|
| corridor_static | individual | 3.198 ms | 0.658 ms | 385 | +0.00% | 0.000% |
| corridor_static | multimesh | 3.191 ms | 0.618 ms | 223 | -0.22% | 0.000% |
| corridor_static | batched | 3.202 ms | 0.639 ms | 272 | +0.13% | 0.000% |
| arena_combat | individual | 3.580 ms | 0.686 ms | 313 | +0.00% | 0.000% |
| arena_combat | multimesh | 3.569 ms | 0.653 ms | 219 | -0.31% | 0.000% |
| arena_combat | batched | 3.577 ms | 0.642 ms | 251 | -0.08% | 0.000% |
| dense_city | individual | 3.266 ms | 0.665 ms | 206 | +0.00% | 0.000% |
| dense_city | multimesh | 3.300 ms | 0.625 ms | 191 | +1.04% | 0.000% |
| dense_city | batched | 3.299 ms | 0.642 ms | 231 | +1.01% | 0.000% |

## S03 · LOD Governor

| Cena | High GPU | Governor GPU | Delta GPU | 1% low delta | High/Low | Pixels | PSNR |
|---|---:|---:|---:|---:|---:|---:|---:|
| corridor_static | 3.453 ms | 3.171 ms | -8.17% | -39.39% | 3/80 | 3.458% | 37.11 dB |
| arena_combat | 3.873 ms | 3.598 ms | -7.10% | +0.29% | 5/61 | 4.314% | 37.37 dB |
| dense_city | 3.298 ms | 3.265 ms | -1.00% | +0.35% | 9/68 | 0.967% | 47.45 dB |

## S04 · Occlusion Mapper

| Cena | GPU off | GPU on | Delta GPU | CPU delta | Draw calls | Culled | Pixels |
|---|---:|---:|---:|---:|---:|---:|---:|
| corridor_static | 4.298 ms | 4.293 ms | -0.12% | -2.79% | 368->368 | 6 | 0.000% |
| arena_combat | 4.126 ms | 4.127 ms | +0.02% | -2.17% | 270->251 | 21 | 2.284% |
| dense_city | 3.447 ms | 3.434 ms | -0.38% | -7.53% | 189->152 | 64 | 0.095% |

- Oclusão real: **INCONCLUSIVE_NOT_BAKED** (sem occluders baked).

## S05 · StreamGuard

- **17 checks**, 6 frames até pronto; estado `{'failed': 1, 'idle': 0, 'loading': 0, 'ready': 3}`.
- `res://scenes/base/corridor_static.tscn`: 14.029 ms
- `res://scenes/base/arena_combat.tscn`: 14.031 ms
- `res://scenes/base/dense_city.tscn`: 20.954 ms

## S06 · FramePacer / render scale

| Escala | GPU p95 | Delta | 1% low | Pixels | PSNR |
|---:|---:|---:|---:|---:|---:|
| 1.00 | 3.556 ms | +0.00% | 219.44 | 0.000% | 100.00 dB |
| 0.85 | 3.008 ms | -15.41% | 219.71 | 2.478% | 44.99 dB |
| 0.70 | 2.552 ms | -28.23% | 221.52 | 3.748% | 43.07 dB |

## S07 · decisões

| Tecnologia | Decisão | Evidência |
|---|---|---|
| Bottleneck Atlas | **GO** | 33 native runs classified from measured GPU/CPU/pacing |
| BatchWeave / MultiMesh | **GO** | draw calls fall 385->223 in corridor with near-zero image diff |
| LOD Governor | **GO_WITH_LIMITATIONS** | GPU p95 -8.2%/-7.1%/-1.0%; 1% low mixed and 0.967-4.314% pixels change |
| Occlusion Mapper / custom frustum | **NO_GO** | GPU unchanged; arena false-hide 2.284% and no corridor draw-call gain |
| StreamGuard | **GO_WITH_LIMITATIONS** | 17 checks; cold loads 14.0-21.0 ms; no scene streaming policy |
| FramePacer / static render scale | **GO_WITH_LIMITATIONS** | GPU -15.4% at 0.85 and -28.2% at 0.7; 2.478-3.748% pixels change |
| VRAM Sentinel | **GO_WITH_LIMITATIONS** | engine video memory 12.6 MB -> 211.5 MB while loading 22 textures |
| FillRate X-Ray | **GO_WITH_LIMITATIONS** | 1440p +135.9% vs 720p at 1 event; 100 events +11.1% vs 1 at 1080p |

## S08 · QA

- 33 runs, 27 imagens, 78 checks de módulos, 17 de streaming e 9 de VRAM.

## S09 · VRAM Sentinel

- 22 texturas; engine video memory 12605824 -> 211489664 bytes (+198883840).
- Estado `OK` com ratio 0.0352.

## S10 · FillRate X-Ray

| Eventos | Resolução | GPU p95 | CPU p95 | Overdraw proxy |
|---:|---|---:|---:|---:|
| 1 | 1280x720 | 2.145 ms | 1.082 ms | 0.0044 |
| 1 | 1920x1080 | 3.577 ms | 1.068 ms | 0.0020 |
| 1 | 2560x1440 | 5.061 ms | 1.320 ms | 0.0011 |
| 10 | 1280x720 | 2.233 ms | 1.184 ms | 0.0444 |
| 10 | 1920x1080 | 3.737 ms | 1.136 ms | 0.0198 |
| 10 | 2560x1440 | 5.294 ms | 1.314 ms | 0.0111 |
| 100 | 1280x720 | 2.434 ms | 2.049 ms | 0.4444 |
| 100 | 1920x1080 | 3.975 ms | 2.110 ms | 0.1975 |
| 100 | 2560x1440 | 5.578 ms | 2.471 ms | 0.1111 |

## Observações

- 33 native runs cover instancing, LOD, frustum, render scale and fillrate
- MultiMesh keeps the frame visually identical while reducing corridor draw calls 385->223
- LOD Governor lowers GPU p95 by 8.2%/7.1%/1.0% with 0.967-4.314% pixel change
- custom frustum mapping does not reduce GPU time and hides 2.284% of the arena frame
- render scale 0.85/0.70 lowers GPU p95 by 15.4%/28.2% with 2.478%/3.748% pixel change
- 100 VFX events at 1440p cost 5.578 ms GPU p95 versus 5.061 ms at 1 event
- StreamGuard loads three scenes in 14.0-21.0 ms with 17 checks
- VRAM Sentinel observes 198.9 MB of engine video memory for 22 loaded textures

## Limitações

- single session, one GPU and driver; 1920x1080 lab unless stated
- custom LOD governor is not Godot automatic mesh LOD or a production LOD engine
- true occlusion culling requires baked occluders and was not exercised
- no dynamic adaptive render scale, no shader prewarm and no VRAM eviction
- draw calls are engine counters, not per-material GPU pipeline proof
- overdraw is a deterministic proxy, not a fragment counter
- no production game, no PoE2 parity and no generalized FPS claim

Gerado por `docs/benchmarks/m06/tools/build_m06_runtime.py`; não é paridade com PoE2.
