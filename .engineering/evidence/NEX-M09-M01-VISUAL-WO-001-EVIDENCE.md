# Evidence Bundle · NEX-M09-M01-VISUAL-WO-001 (verdade visual das cenas M01)

**Status:** `MEASUREMENT_EVIDENCE / SINGLE_SESSION / VISUAL_DIFFERENCE_OBSERVED / NO_QUALITY_CLAIM`
**Issue:** #14 · **Base:** `647670eecf051849970e659e5ef5b98da4413367` · **Harness source SHA:** `952b5a63bc1696cadf7436a061a7d996c80fa220`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- Modo visual no harness `preset_ab`: `NEX_PRESET_AB_VISUAL=1`, 180 frames de warmup, leitura do viewport após `RenderingServer.frame_post_draw`, flip Y e PNG 1280×720.
- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-visual/`: 18 PNGs, manifesto, fatos, análise e SHA-256 de 21 arquivos.
- `docs/benchmarks/m09/m01-visual.v1.json`, `M01-VISUAL-REPORT.md`, builder determinístico e decoder PNG mínimo (`png_image.py`).
- `tests/ci/test_m01_visual.py`: 11 testes, incluindo determinismo A/A, diferença A/B e reprodutibilidade.

## Sessão medida

- Windows · RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · Godot 4.7.2-stable.
- 1280×720 · 3 cenas × 2 presets × 3 repetições (L/H/L/H/L/H por cena).
- Source do harness: `952b5a63bc1696cadf7436a061a7d996c80fa220`.

## Resultados

| Cena | A/A idêntico | A/A mean abs | A/B mean abs | A/B max abs | A/B pixels alterados | A/B PSNR |
|---|---|---|---|---|---:|---:|
| corridor_static | sim (3+3) | 0.0000 | 0.5135 | 170 | 4.077% | 37.406 dB |
| arena_combat | sim (3+3) | 0.0000 | 0.4898 | 187 | 3.884% | 36.386 dB |
| dense_city | sim (3+3) | 0.0000 | 0.2317 | 133 | 1.745% | 39.763 dB |

- Cada par cena/preset tem um único SHA-256 compartilhado pelas três repetições; todas as comparações A/A são exatamente zero.
- Os três pares A/B por cena produzem as mesmas métricas, pois as repetições são byte-idênticas.
- A diferença confirma mudança de estado de rendering, não ranking de qualidade.

## Verificação

- 18/18 PNGs 1280×720 RGB8; 21 arquivos cobertos por `SHA256SUMS.txt`.
- `build_m01_visual.py --check` reproduz `m01-visual.v1.json`/`M01-VISUAL-REPORT.md`.
- `build_ab.py --check`, `build_scaling.py --check` e `build_m01_ab.py --check` continuam reproduzindo os relatórios anteriores.
- Suítes completas em worktree LF limpo verificadas antes do squash.
- PR protegida e checkpoint pós-merge verificados separadamente.

## O que não foi feito / não é alegado

- Nenhuma mudança nas cenas base, `project.godot`, hub, renderer, shaders ou engine.
- Sessão única; frame estático; sem animação, temporal effects ou movimento de câmera.
- Fillers podem sobrepor props; não é uma cena de beleza.
- Comparação é byte a byte de RGB; não modela percepção humana ou color space.
- Nenhum claim de qualidade visual, superioridade de preset, FPS ou generalização.
- M09 parent (#14) permanece `NOT_ADMITTED`.

## Rollback

Remover o modo visual do harness, `png_image.py`, o builder e relatório visuais, o bundle de evidência, o teste novo e o delta/WO/lock correspondentes.

## Próximos passos

- Animação/temporal effects, golden images perceptuais ou integração no hub exigem WO própria.
