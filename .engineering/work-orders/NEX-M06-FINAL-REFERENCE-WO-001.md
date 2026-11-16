# NEX-M06-FINAL-REFERENCE-WO-001 | Fechamento da performance de referência M06

**Status:** `OWNER_STANDING_AUTHORIZATION / EXECUTABLE`
**Admissão:** `NEX-ADR-0017` / `NEX-D-028`; instrução do Owner de 2026-11-16 para finalizar o M06 com medições reais, sem paridade com PoE2.
**Base:** `main` `c763319d04d0bf353c15db8378872bdf8fab1734`.
**Modo:** ADMIN_SOLO (`NOT_INDEPENDENT`). **Risco:** ELEVATED (33 runs nativos, GPU e capturas de performance).
**Lock:** `.engineering/context-locks/NEX-M06-FINAL-REFERENCE-WO-001-EXECUTION.json`.

## Objetivo

Finalizar o M06 como performance de referência: laboratório nativo para instancing, LOD, frustum, render scale e fillrate; planners testáveis para streaming, frame pacing e VRAM; atlas de gargalos com 33 runs; R&D/QA e fechamento de #59–#68 e #11.

## Escopo

- `nex_bench/scenes/m06_performance/`: `batch_weave.gd`, `lod_governor.gd`, `occlusion_mapper.gd`, `stream_guard.gd`, `frame_pacer.gd`, `vram_sentinel.gd`, `fill_rate_xray.gd`, `bottleneck_atlas.gd`, `modules_smoke.gd`, `stream_smoke.gd`, `vram_smoke.gd`.
- `nex_bench/scenes/preset_ab/preset_ab.gd`: flags `NEX_PRESET_AB_M06*`, métricas de draw calls/objetos/primitivas.
- Evidence `windows-rtx5050-2026-11-16-m06/`: 33 runs validados, 27 imagens, 3 smokes, manifests e SHA256SUMS.
- `docs/benchmarks/m06/tools/build_m06_runtime.py`, `M06-RUNTIME.md`, `m06-runtime.v1.json`, `M06-FINAL-GATE.md`.
- `tests/ci/test_m06_final.py`; enforcement no workflow.
- ADR/ledger/WO/lock/evidência/delta, AGENTS/SCOPE/CHECKPOINT e fechamento de issues.

## Fora de escopo

- Renderer core, GDExtension, Godot fork, `project.godot`.
- LOD engine de produção, oclusão baked, render scale dinâmico, shader prewarm, VRAM eviction.
- Streaming de cena/prefetch de disco, orçamento global intermodular.
- Jogo, gameplay, rede, cloud, assets de terceiros ou paridade com PoE2.
- Claims generalizados de FPS, qualidade ou cross-device.

## DoD

- 33 runs nativos validados; 27 imagens; 3 smokes PASS (`78 + 17 + 9` checks).
- S02: draw calls 385→223 no corredor, diff visual 0.000%, CPU ~-6%.
- S03: GPU p95 -8.17%/-7.10%/-1.00%; pixels 3.458%/4.314%/0.967%.
- S04: mapper customizado **NO_GO**; arena false-hide 2.284%; oclusão real `INCONCLUSIVE_NOT_BAKED`.
- S05: StreamGuard 17 checks; cargas frias 14.0–21.0 ms.
- S06: render scale 0.85/0.70 com GPU -15.41%/-28.23%; pixels 2.478%/3.748%.
- S09: VRAM 12.6 MB → 211.5 MB ao carregar 22 texturas (+198.9 MB).
- S10: 1440p +135.9% vs 720p em 1 evento; 100 vs 1 evento em 1080p +11.1%.
- Builders `--check`; suíte CI verde; PR protegida e checkpoint pós-merge.
- Issues #59–#68 e #11 fechadas com comentário de evidência.

## STOP

- Base/HEAD divergente, smoke falhando, run não validado, imagem ausente, check vermelho, claim de paridade com PoE2 ou generalização → parar e registrar.
