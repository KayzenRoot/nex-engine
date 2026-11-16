# Evidence Bundle · NEX-M06-FINAL-REFERENCE-WO-001

**Status:** `M06_PERFORMANCE_REFERENCE_EVIDENCE / NATIVE_LAB / NO_POE2_PARITY_CLAIM / ADMIN_SOLO_NOT_INDEPENDENT`
**Parent:** M06 #11 · **Base:** `c763319d04d0bf353c15db8378872bdf8fab1734`
**Audit:** `ADMIN_SOLO / NOT_INDEPENDENT` · **Risk:** ELEVATED

## Entregue

- **Bottleneck Atlas:** 33 runs nativos classificados em 22 GPU e 11 pacing.
- **BatchWeave:** planner espacial + MultiMesh; 9 runs individual/multimesh/batched em três cenas.
- **LOD Governor:** seleção high/low com histerese; 6 runs e 6 capturas.
- **Occlusion Mapper:** classificador frustum/AABB; 6 runs ON/OFF com FOV 25.
- **StreamGuard:** 17 checks; cargas frias de três cenas em 14.0–21.0 ms.
- **FramePacer:** política com histerese/cooldown; render scale 1.0/0.85/0.70 em 3 runs.
- **VRAM Sentinel:** 9 checks; 22 texturas; engine video memory 12.6 MB → 211.5 MB.
- **FillRate X-Ray:** matriz 1/10/100 eventos × 720p/1080p/1440p; 9 runs.
- **QA:** 27 imagens, 3 smokes, `runs.v1.json`, SHA256SUMS e `M06-RUNTIME.md`.
- **Governança:** `NEX-ADR-0017`, `NEX-D-028`, WO/lock/evidência/delta/gate.

## Resultado

- **S02:** draw calls 385→223 no corredor; diff visual 0.000%; CPU p95 -6.1%.
- **S03:** GPU p95 -8.17%/-7.10%/-1.00%; pixels 3.458%/4.314%/0.967%; 1% low do corredor -39.39%.
- **S04:** GPU inalterado; arena false-hide 2.284%; oclusão real `INCONCLUSIVE_NOT_BAKED`; decisão **NO_GO** para mapper customizado.
- **S05:** 17 checks; 3 cenas prontas em 14.029/14.031/20.954 ms.
- **S06:** render scale 0.85/0.70 com GPU -15.41%/-28.23%; pixels 2.478%/3.748%.
- **S09:** +198.883.840 bytes de engine video memory; estado `OK` com ratio 0.0352.
- **S10:** 1440p +135.9% vs 720p em 1 evento; 100 vs 1 evento em 1080p +11.1%.
- Nenhum asset de terceiros; todas as cenas e texturas são do repositório.

## Verificação

- `modules_smoke.gd`: `M06_MODULE_SMOKE_PASS 78 checks` (windowed; MultiMesh transform requer renderer nativo).
- `stream_smoke.gd`: `M06_STREAM_SMOKE_PASS 17 checks`.
- `vram_smoke.gd`: `M06_VRAM_SMOKE_PASS 9 checks textures=22 delta=198883840`.
- `validate_preset_ab.py`: 33/33 runs `PASS`.
- `build_m06_runtime.py --check`: `M06_PERFORMANCE_RUNTIME_CHECK_PASS: 33 runs`.
- Suíte CI completa e builders/validadores verdes antes da PR.

## O que não foi feito / não é alegado

- Nenhuma alteração no renderer core, GDExtension, Godot fork ou `project.godot`.
- Nenhum LOD engine de produção, oclusão baked, render scale dinâmico, shader prewarm ou eviction de VRAM.
- Nenhum streaming de cena, prefetch de disco ou orçamento global intermodular.
- Nenhum jogo, gameplay, rede, cloud ou asset de terceiros.
- Nenhum claim generalizado de FPS/qualidade, cross-device ou paridade com PoE2.
- Aprovação `OWNER_AUTHORIZED_ADMIN_SOLO`; sem revisor independente.

## Rollback

Reverter o laboratório M06, as flags no `preset_ab`, as evidências, o builder/relatórios, o teste, o workflow, ADR/ledger/WO/lock/evidência/delta, atualizações de AGENTS/SCOPE/CHECKPOINT e o fechamento das issues.
