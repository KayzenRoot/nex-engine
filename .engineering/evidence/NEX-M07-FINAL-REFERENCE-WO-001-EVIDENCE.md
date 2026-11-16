# Evidence Bundle · NEX-M07-FINAL-REFERENCE-WO-001

**Status:** `M07_RENDER2D_REFERENCE_EVIDENCE / NATIVE_2D_LAB / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`
**Parent:** M07 #12 · **Base:** `aa6256a82f6cd34e347b05ac43375ac4042d2ede`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** STANDARD

## Entregue

- **CanvasPlanner:** 46 checks headless; camadas, materiais, luzes, partículas e batching.
- **2D lighting:** `CanvasModulate` + 4 `PointLight2D` em cena nativa.
- **2D shadows:** `LightOccluder2D` + sombras de luz.
- **Normal maps:** `CanvasTexture` com `normal_texture`.
- **GPUParticles2D:** 6 emissores, 384 partículas.
- **Parallax:** `ParallaxBackground` com 3 camadas.
- **Quality profiles:** low/medium/high.
- **Evidência:** 9 runs nativos validados, 9 capturas 1920×1080, manifest e SHA256SUMS.
- **Builder/Gate:** `build_m07_runtime.py`, `M07-RUNTIME.md`, `m07-runtime.v1.json`, `M07-FINAL-GATE.md`.
- **Governança:** `NEX-ADR-0018`, `NEX-D-029`, WO/lock/evidência/delta.

## Resultado

- **S01:** CanvasPlanner 46 checks.
- **S02:** baseline GPU p95 **0.060 ms**; lighting **0.075 ms** (+25.00%), 16.218% de pixels.
- **S03:** shadows **0.100 ms** (+66.67% vs baseline, +33.3% vs lighting); shadows vs lighting 9.028% de pixels.
- **S04:** normal **0.082 ms** (+36.67% vs baseline, +9.3% vs lighting); normal vs lighting 14.542% de pixels.
- **S05:** particles **0.071 ms** (+18.33%); 0.979% de pixels.
- **S06:** parallax **0.070 ms** (+16.67%); 23.006% de pixels.
- **S07:** quality low/medium/high **0.065 / 0.081 / 0.153 ms**.
- **S08:** 9 runs, 9 imagens, 46 checks, 0 assets de terceiros.
- Nenhum asset de terceiros; todas as texturas e cenas são procedurais.

## Verificação

- `m07_lab.gd`: `NEX_M07_LAB` em 9 modos; `NEX_M07_CAPTURE` em 9 runs.
- `validate_m07_lab.py`: 9/9 runs `PASS`.
- `build_m07_runtime.py --check`: `M07_RENDER2D_RUNTIME_CHECK_PASS: 9 runs`.
- CanvasPlanner: `NEX_M07_S01_SMOKE_PASS: 46 checks`.
- Suíte CI completa e builders/validadores verdes antes da PR.

## O que não foi feito / não é alegado

- Nenhum renderer 2D de produção, atlas packing, y-sort ou shader customizado.
- Nenhum M08/2.5D, M10 animação, M11 assets, gameplay, rede ou cloud.
- Nenhum input-to-photon, VRAM, cross-device ou claim generalizado de FPS/qualidade.
- Nenhum asset, shader, cena ou paridade com PoE2.
- Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; sem revisor independente.

## Rollback

Reverter o laboratório M07, o layout no `session.gd`, as evidências, o builder/relatórios, o teste, o workflow, ADR/ledger/WO/lock/evidência/delta, atualizações de AGENTS/SCOPE/CHECKPOINT e o fechamento da issue.
