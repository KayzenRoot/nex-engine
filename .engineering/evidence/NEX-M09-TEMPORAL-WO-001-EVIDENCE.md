# Evidence Bundle · NEX-M09-TEMPORAL-WO-001 (estabilidade temporal)

**Status:** `MEASUREMENT_EVIDENCE / SINGLE_SESSION / TEMPORAL_STABILITY_OBSERVED / NO_QUALITY_CLAIM`
**Issue:** #14 · **Base:** `cefd2a045a410147b96577a547239f75be5215d5` · **Harness source SHA:** `22f428aebf43da39750adb6a8c919d0b2721d9a1`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- `nex_bench/gpu_profile/evidence/windows-rtx5050-2026-11-14-m01-temporal/`: 30 PNGs (5 por célula), manifesto, fatos, análise e SHA-256 de 33 arquivos.
- `docs/benchmarks/m09/temporal-stability.v1.json`, `TEMPORAL-STABILITY-REPORT.md` e builder determinístico.
- `tests/ci/test_temporal_stability.py`: 8 testes.
- Atlas M09 atualizado para 10 bundles, 66 imagens e 384 arquivos.

## Sessão medida

- Windows · RTX 5050 · NVIDIA 617.14 / Vulkan forward_plus · Godot 4.7.2-stable.
- 1280×720, 3 cenas × 2 presets × 5 frames, intervalo de 30 frames após warmup de 180.
- Source do harness: `22f428aebf43da39750adb6a8c919d0b2721d9a1`.

## Resultados

| Cena | Preset | Frames | SHA-256 únicos | Frame-a-frame mean abs | Pixels alterados |
|---|---|---:|---:|---:|---:|
| corridor_static | ab-low | 5 | 1 | 0.0000 | 0.000% |
| corridor_static | ab-high | 5 | 1 | 0.0000 | 0.000% |
| arena_combat | ab-low | 5 | 1 | 0.0000 | 0.000% |
| arena_combat | ab-high | 5 | 1 | 0.0000 | 0.000% |
| dense_city | ab-low | 5 | 1 | 0.0000 | 0.000% |
| dense_city | ab-high | 5 | 1 | 0.0000 | 0.000% |

- Todas as cinco frames de cada célula são byte-idênticas (um SHA-256 por célula).
- Todas as comparações frame-a-frame são exatamente zero neste workload estático.
- Nenhuma variação temporal foi observada.

## Verificação

- 30/30 PNGs 1280×720 RGB8; 33 arquivos cobertos por `SHA256SUMS.txt`.
- `build_temporal_stability.py --check` reproduz o relatório.
- Atlas M09 atualizado e reproduzível com 10 bundles.
- Suítes completas em worktree LF limpo verificadas antes do squash.
- PR protegida e checkpoint pós-merge verificados separadamente.

## O que não foi feito / não é alegado

- Nenhuma mudança nas cenas base, `project.godot`, hub, renderer, shaders ou engine.
- Cenas estáticas; sem animação, movimento de câmera ou efeitos temporais dinâmicos.
- Comparação é byte a byte de RGB; não modela percepção humana ou color space.
- Nenhum claim de qualidade visual, FPS ou generalização.
- M09 parent (#14) permanece `NOT_ADMITTED`.

## Rollback

Remover o modo de sequência do harness, o bundle de evidência, `temporal-stability.v1.json`/`TEMPORAL-STABILITY-REPORT.md`/builder, o teste novo, a entrada no atlas e o delta/WO/lock correspondentes.

## Próximos passos

- Animação, movimento de câmera ou efeitos temporais dinâmicos exigem WO própria.
