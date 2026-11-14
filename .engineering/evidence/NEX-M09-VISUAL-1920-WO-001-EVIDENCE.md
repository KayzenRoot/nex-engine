# Evidence Bundle · NEX-M09-VISUAL-1920-WO-001 (verdade visual em 1920×1080)

**Status:** `MEASUREMENT_EVIDENCE / SINGLE_SESSION / VISUAL_DIFFERENCE_OBSERVED / NO_QUALITY_CLAIM`
**Issue:** #14 · **Base:** `06eb6d92da50bdb8105bbc8f7b6bed98faebb329` · **Harness source SHA:** `06eb6d92da50bdb8105bbc8f7b6bed98faebb329`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-visual-1920/`: 18 PNGs 1920×1080, manifesto, fatos, análise e SHA-256 de 21 arquivos.
- `docs/benchmarks/m09/m01-visual-1920.v1.json`, `M01-VISUAL-1920-REPORT.md` e builder determinístico.
- `tests/ci/test_m01_visual_1920.py`: 9 testes.
- Atlas M09 atualizado para 9 bundles, 36 imagens e 351 arquivos.

## Sessão medida

- Windows · RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · Godot 4.7.2-stable.
- 1920×1080, 3 cenas × 2 presets × 3 repetições (L/H/L/H/L/H por cena).
- Source do harness: `06eb6d92da50bdb8105bbc8f7b6bed98faebb329`.

## Resultados

| Cena | A/A idêntico | A/A mean abs | A/B mean abs | A/B max abs | A/B pixels alterados | A/B PSNR |
|---|---|---|---|---|---:|---:|
| corridor_static | sim (3+3) | 0.0000 | 0.4168 | 167 | 3.367% | 38.485 dB |
| arena_combat | sim (3+3) | 0.0000 | 0.4215 | 189 | 3.354% | 36.851 dB |
| dense_city | sim (3+3) | 0.0000 | 0.1785 | 146 | 1.276% | 40.464 dB |

- Cada par cena/preset tem um único SHA-256 compartilhado pelas três repetições.
- A/B mean abs é ligeiramente menor que em 1280×720: −18.8% (corridor), −13.9% (arena), −23.0% (city).
- A direção é consistente: o preset high altera a imagem e city tem a menor diferença.

## Verificação

- 18/18 PNGs 1920×1080 RGB8; 21 arquivos cobertos por `SHA256SUMS.txt`.
- `build_m01_visual_1920.py --check` reproduz o relatório.
- Atlas M09 atualizado e reproduzível com 9 bundles.
- Suítes completas em worktree LF limpo verificadas antes do squash.
- PR protegida e checkpoint pós-merge verificados separadamente.

## O que não foi feito / não é alegado

- Nenhuma mudança nas cenas base, `project.godot`, hub, renderer, shaders ou engine.
- Sessão única; frame estático; sem animação, temporal effects ou movimento de câmera.
- Comparação é byte a byte de RGB; não modela percepção humana ou color space.
- Nenhum claim de qualidade visual, superioridade de preset, FPS ou generalização.
- M09 parent (#14) permanece `NOT_ADMITTED`.

## Rollback

Remover o bundle de evidência, `m01-visual-1920.v1.json`/`M01-VISUAL-1920-REPORT.md`/builder, o teste novo, a entrada no atlas e o delta/WO/lock correspondentes.

## Próximos passos

- 2560×1440, animação/temporal ou integração no hub exigem WO própria.
